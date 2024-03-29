"""

:synopsis: The "Species" ChadoObject.

:moduleauthor: Ian Longden <ilongden@morgan.harvard.edu>
"""
import os
from .chado_base import ChadoObject, FIELD_VALUE

from harvdev_utils.production import (
    Db, Dbxref, OrganismDbxref, Organism, Organismprop, OrganismPub
)
from harvdev_utils.chado_functions import get_or_create, get_cvterm

import logging
from datetime import datetime

log = logging.getLogger(__name__)


class ChadoSpecies(ChadoObject):
    def __init__(self, params):
        log.debug('Initializing ChadoSpecies object.')
        ##########################################
        # Set up how to process each type of input
        ##########################################
        self.type_dict = {'ignore': self.ignore,
                          'dbxref': self.load_dbxref,
                          'cvterm': self.load_cvterm}

        self.delete_dict = {'dbxref': self.delete_dbxref,
                            'cvterm': self.delete_cvterm}

        self.proforma_start_line_number = params.get('proforma_start_line_number')

        ###########################################################
        # Values queried later, placed here for reference purposes.
        ############################################################
        self.species = None   # All other proforma need a reference to a pub
        self.new_species = False  # Modified later when ignored are processed

        # Initiate the parent.
        super(ChadoSpecies, self).__init__(params)

        ############################################################
        # Get processing info and data to be processed.
        # Please see the yml/species.yml file for more details
        ############################################################
        yml_file = os.path.join(os.path.dirname(__file__), 'yml/species.yml')
        # Populated self.process_data with all possible keys.
        self.process_data = self.load_reference_yaml(yml_file, params)
        self.direct_key = 'SP1a'
        self.reference = params.get('reference')

    def load_content(self, references):  # noqa: C901
        """Process the Species proforma."""
        try:
            self.pub = references['ChadoPub']
        except KeyError:
            message = "Unable to find publication."
            self.critical_error(self.process_data['G1a']['data'], message)
            return None

        if not self.pub:
            message = "No publication specified!"
            self.critical_error(self.process_data['SP1g']['data'], message)
        # lookup species based on SP1a and SP1b
        self.species, self.new_species = get_or_create(self.session,
                                                       Organism,
                                                       genus=self.process_data['SP1a']['data'][FIELD_VALUE],
                                                       species=self.process_data['SP1b']['data'][FIELD_VALUE])

        if self.new_species:
            # Add the pub
            get_or_create(self.session, OrganismPub, organism_id=self.species.organism_id, pub_id=self.pub.pub_id)
        if not self.has_data('SP1g'):
            return None
        if self.new_species and self.process_data['SP1g']['data'][FIELD_VALUE] == 'y':
            message = "SP1g (is SP1a+SP1b already in FlyBase?) set to y but species NOT found."
            self.critical_error(self.process_data['SP1g']['data'], message)
        if not self.new_species and self.process_data['SP1g']['data'][FIELD_VALUE] == 'n':
            message = "SP1g (is SP1a+SP1b already in FlyBase?) set to n but species found in the database."
            self.critical_error(self.process_data['SP1g']['data'], message)

        if self.new_species:
            # add abbreviation
            setattr(self.species, 'abbreviation', self.process_data['SP2']['data'][FIELD_VALUE])
            # add common name
            setattr(self.species, 'common_name', self.process_data['SP3a']['data'][FIELD_VALUE])
        else:
            if self.has_data('SP3b') and self.process_data['SP3b']['data'][FIELD_VALUE] == 'y':
                setattr(self.species, 'common_name', self.process_data['SP3a']['data'][FIELD_VALUE])
            if self.has_data('SP2') and self.process_data['SP2']['data'][FIELD_VALUE] != self.species.abbreviation:
                message = "Abbreviation already set to {}".format(self.species.abbreviation)
                message += " But listed here as {}. Either correct or remove it".format(self.process_data['SP2']['data'][FIELD_VALUE])
                self.critical_error(self.process_data['SP2']['data'], message)

        # bang c first as this supersedes all things
        if self.bang_c:
            self.bang_c_it()
        if self.bang_d:
            self.bang_d_it()

        for key in self.process_data:
            log.debug("Processing {}".format(self.process_data[key]['data']))
            self.type_dict[self.process_data[key]['type']](key)

        timestamp = datetime.now().strftime('%c')
        curated_by_string = 'Curator: %s;Proforma: %s;timelastmodified: %s' % (self.curator_fullname, self.filename_short, timestamp)
        log.debug('Curator string assembled as:')
        log.debug('%s' % (curated_by_string))

    def ignore(self, key):
        """Ignore."""
        pass

    def load_dbxref(self, key):
        """Load the dbxref. given the proforma key.

        Args:
            key (str): proforma key name.

        Returns:
            None

        """
        db_name = self.process_data[key]['dbname']

        log.debug("Looking up db: {}.".format(db_name))
        db = self.session.query(Db).filter(Db.name == db_name).one_or_none()
        if not db:
            message = "db {} NOT found in the chado database.".format(db_name)
            self.critical_error(self.process_data[key]['data'], message)
            return

        dbxref, _ = get_or_create(self.session, Dbxref, db_id=db.db_id, accession=self.process_data[key]['data'][FIELD_VALUE])

        org_dbxref = self.session.query(OrganismDbxref).join(Dbxref).join(Db).filter(OrganismDbxref.organism_id == self.species.organism_id,
                                                                                     Db.db_id == db.db_id).one_or_none()
        if org_dbxref:
            message = "dbxref {} Already set for this organism. Please use !c or !d".format(db.name)
            self.critical_error(self.process_data[key]['data'], message)
            return
        get_or_create(
            self.session, OrganismDbxref,
            organism_id=self.species.organism_id,
            dbxref_id=dbxref.dbxref_id
        )

    def load_multiple_cvterms(self, key, cvterm):
        """Load cvterms.

        Args:
            key (str): proforma key name.
            cvterm (Cvterm Object): cvterm to add to orgasmism.
        Returns:
            None
        """
        #
        # Multiple cvterms need to be treated differently as they can be added
        # at any time and do not have as much restrictions
        #
        for item in self.process_data[key]['data']:
            org_prop = self.session.query(Organismprop).join(Organism).filter(Organismprop.organism_id == self.species.organism_id,
                                                                              Organismprop.type_id == cvterm.cvterm_id,
                                                                              Organismprop.value == item[FIELD_VALUE]).one_or_none()
            if org_prop:
                message = "Organism already has this value for {}. Will ignore and carry on".format(cvterm.name)
                self.warning_error(item, message)
            else:
                get_or_create(self.session, Organismprop,
                              organism_id=self.species.organism_id,
                              type_id=cvterm.cvterm_id,
                              value=item[FIELD_VALUE])

    def load_cvterm(self, key):
        """Load cvterm to species.

        Args:
            key (str): proforma key name.
        """
        if self.has_data(key):
            cvterm = get_cvterm(self.session, self.process_data[key]['cv'], self.process_data[key]['cvterm'])
            if not cvterm:
                message = 'Cvterm lookup failed for cv {} cvterm {}?'.format(self.process_data[key]['cv'],
                                                                             self.process_data[key]['cvterm'])
                self.critical_error(self.process_data[key]['data'], message)
                return
            # if it is a list then we can have multiple values.
            # so we need to treat that differently.
            if type(self.process_data[key]['data']) is list:
                return self.load_multiple_cvterms(key, cvterm)

            # Does it already have a value
            org_prop = self.session.query(Organismprop).join(Organism).filter(Organismprop.organism_id == self.species.organism_id,
                                                                              Organismprop.type_id == cvterm.cvterm_id).one_or_none()
            if org_prop and org_prop.value:
                message = "Organism already has a value for {}. Please use !c or !d".format(cvterm.name)
                self.critical_error(self.process_data[key]['data'], message)
                return
            elif not org_prop:
                get_or_create(self.session, Organismprop,
                              organism_id=self.species.organism_id,
                              type_id=cvterm.cvterm_id,
                              value=self.process_data[key]['data'][FIELD_VALUE])
            else:
                setattr(org_prop, 'value', self.process_data[key]['data'][FIELD_VALUE])

    def delete_cvterm(self, key, bangc=True):
        """Delete the cvterm.

        Args:
            key (string): Proforma field key
            bangc (Bool, optional): True if bangc operation
                                    False if bangd operation.
                                    Default is True.
        """
        cvterm = get_cvterm(self.session, self.process_data[key]['cv'], self.process_data[key]['cvterm'])
        if not cvterm:
            message = 'Cvterm lookup failed for cv {} cvterm {}?'.format(self.process_data[key]['cv'],
                                                                         self.process_data[key]['cvterm'])
            self.critical_error(self.process_data[key]['data'], message)
            return

        if bangc:
            count = 0
            for item in self.session.query(Organismprop).join(Organism).filter(Organismprop.organism_id == self.species.organism_id,
                                                                               Organismprop.type_id == cvterm.cvterm_id):
                self.session.delete(item)
                count += 1
            if count:
                log.debug("Deleted {} organismprops for cvterm {}".format(count, cvterm.name))
            else:
                message = "No organismprops deleted for cvterm {}?".format(cvterm.name)
                self.warning_error(self.process_data[key]['data'], message)
        else:
            if type(self.process_data[key]['data']) is list:
                prop_list = self.process_data[key]['data']
            else:
                prop_list = [self.process_data[key]['data']]
            if not self.process_data[key]['data']:
                self.critical_error(prop_list[0], "Must specify a value with !d.")
                self.process_data[key]['data'] = None
                return
            for item in prop_list:
                org_prop = self.session.query(Organismprop).join(Organism).\
                    filter(Organismprop.organism_id == self.species.organism_id,
                           Organismprop.type_id == cvterm.cvterm_id,
                           Organismprop.value == item[FIELD_VALUE]).one_or_none()
                if org_prop:
                    self.session.delete(org_prop)
                else:
                    message = "cvterm {} has no value {} for this Organism/Species.".format(cvterm.name, item[FIELD_VALUE])
                    self.critical_error(item, message)

    def delete_dbxref(self, key, bangc=True):
        """Delete the dbxref.

        Args:
            key (string): Proforma field key
            bangc (Bool, optional): True if bangc operation
                                    False if bangd operation.
                                    Default is True.
        """
        db = self.session.query(Db).filter(Db.name == self.process_data[key]['dbname']).one()
        if bangc:
            # delete only the organism_dbxref or dbxref is no others exist.
            count = 0
            for item in self.session.query(OrganismDbxref).join(Dbxref).filter(OrganismDbxref.organism_id == self.species.organism_id,
                                                                               OrganismDbxref.dbxref_id == Dbxref.dbxref_id,
                                                                               Dbxref.db_id == db.db_id):
                count += 1
                self.session.delete(item)
            log.debug("Removed {} dbxref's for {}.".format(count, key))
        else:
            if not self.process_data[key]['data']:
                self.critical_error((key, None, '?',), "Must specify a value with !d.")
                self.process_data[key]['data'] = None
                return
            dbxref = self.session.query(OrganismDbxref).join(Organism).join(Dbxref).filter(
                Organism.organism_id == OrganismDbxref.organism_id,
                Organism.organism_id == self.species.organism_id,
                OrganismDbxref.dbxref_id == Dbxref.dbxref_id,
                Dbxref.db_id == db.db_id,
                Dbxref.accession == self.process_data[key]['data'][FIELD_VALUE]).one_or_none()
            if not dbxref:
                message = "Species '{} {}'".format(self.species.genus, self.species.species)
                message += " has no dbxref of db '{}'".format(self.process_data[key]['dbname'])
                message += " and accession '{}'.".format(self.process_data[key]['data'][FIELD_VALUE])
                message += " So unable to remove it"
                self.critical_error(self.process_data[key]['data'], message)
                return

            self.session.delete(dbxref)
            log.debug("{} removed".format(dbxref))
