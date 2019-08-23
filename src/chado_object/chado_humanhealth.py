"""
.. module:: chado_humanhealth
   :synopsis: The "humanhealth" ChadoObject.

.. moduleauthor:: Ian Longden <ilongden@morgan.harvard.edu>
"""
import os
from .chado_base import ChadoObject, FIELD_VALUE
from harvdev_utils.production import (
    Humanhealth, Organism
    # Cv, Cvterm, HumanhealthCvterm, Db, Dbxref
)
from harvdev_utils.chado_functions import get_or_create

import logging
from datetime import datetime

log = logging.getLogger(__name__)


class ChadoHumanhealth(ChadoObject):
    def __init__(self, params):
        log.info('Initializing ChadoHumanhealth object.')
        ##########################################
        # Set up how to process each type of input
        ##########################################
        self.type_dict = {'direct': self.load_direct,
                          'relationship': self.load_relationship,
                          'prop': self.load_pubprop,
                          'synonym': self.load_synonym,
                          'dissociate_pub': self.dissociate_pub,
                          'dissociate_hgnc': self.dissociate_hgnc,
                          'obsolete': self.make_obsolete,
                          'ignore': self.ignore,
                          'dbxref': self.load_dbxref,
                          'dbxrefprop': self.load_dbxrefprop,
                          'featureprop': self.load_featureprop}

        # self.delete_dict = {'direct': self.delete_direct,
        #                    'pubauthor': self.delete_author,
        #                    'relationship': self.delete_relationships,
        #                    'pubprop': self.delete_pubprops,
        #                    'dbxref': self.delete_dbxref,
        #                    'ignore': self.delete_ignore,
        #                    'obsolete': self.delete_obsolete}

        self.proforma_start_line_number = params.get('proforma_start_line_number')
        self.reference = params.get('reference')

        ###########################################################
        # Values queried later, placed here for reference purposes.
        ############################################################
        self.pub = None   # All other proforma need a reference to a pub
        self.newhumanhealth = False

        # Initiate the parent.
        super(ChadoHumanhealth, self).__init__(params)

        ############################################################
        # Get processing info and data to be processed.
        # Please see the yml/humanhealth.yml file for more details
        ############################################################
        yml_file = os.path.join(os.path.dirname(__file__), 'yml/humanhealth.yml')
        # Populated self.process_data with all possible keys.
        self.process_data = self.load_reference_yaml(yml_file, params)

    def load_content(self):
        """
        Main processing routine
        """
        if self.process_data['HH1f']['data'][FIELD_VALUE] == "new":
            self.newhumanhealth = True
        self.humanhealth = self.get_humanhealth()

        self.pub = super(ChadoHumanhealth, self).pub_from_fbrf(self.reference, self.session)

        if self.humanhealth:  # Only proceed if we have a hh. Otherwise we had an error.
            self.extra_checks()
        else:
            return

        # bang c first as this supersedes all things
        # if self.bang_c:
        #    self.bang_c_it()
        # if self.bang_d:
        #    self.bang_d_it()

        for key in self.process_data:
            log.debug("Processing {}".format(self.process_data[key]['data']))
            self.type_dict[self.process_data[key]['type']](key)

        timestamp = datetime.now().strftime('%c')
        curated_by_string = 'Curator: %s;Proforma: %s;timelastmodified: %s' % (self.curator_fullname, self.filename_short, timestamp)
        log.info('Curator string assembled as:')
        log.info('%s' % (curated_by_string))

    def obtain_session(self, session):
        self.session = session

    def get_humanhealth(self):
        """
        get humanhealth or create humanhealth if new.
        returns None or the humanhealth to be used.
        """
        if not self.newhumanhealth:
            hh = self.session.query(Humanhealth).\
                filter(Humanhealth.uniquename == self.process_data['HH1f']['data'][FIELD_VALUE]).\
                one_or_none()
            if not hh:
                self.critical_error(self.process_data['HH1f']['data'], 'Humanhealth does not exist in the database.')
                return
            # Check synonym name is the same as HH1b
            name = self.process_data['HH1b']['data'][FIELD_VALUE]
            if hh.name != name:
                self.critical_error(self.process_data['HH1b']['data'], 'HH1b field "{}" does NOT match the one in the database "{}"'.format(name, hh.name))
        else:
            # triggers add dbxref and proper uniquename
            # check we have HH2a, HH1g and HH1b
            organism = get_or_create(self.session, Organism, abbreviation='Hsap')
            hh = get_or_create(self.session, Humanhealth, name=self.process_data['HH1b']['data'][FIELD_VALUE],
                               organism_id=organism.organism_id, uniquename='FBhh:temp_0')
            log.info(hh)
            # db has correct FBhh0000000x in it but here still has 'FBhh:temp_0'. ???
            # presume triggers start after hh is returned. Maybe worth getting form db again
            log.info("New humanhealth created with fbhh {}.".format(hh.uniquename))
        return hh

    def extra_checks(self):
        pass

    def load_direct(self, key):
        if self.has_data(key):
            old_attr = getattr(self.humanhealth, self.process_data[key]['name'])
            if old_attr:
                self.warning_error(self.process_data[key]['data'], "No !c but still overwriting existing value of {}".format(old_attr))
            setattr(self.humanhealth, self.process_data[key]['name'], self.process_data[key]['data'][FIELD_VALUE])

    def load_relationship(self, key):
        pass

    def load_pubprop(self, key):
        pass

    def load_synonym(self, key):
        pass

    def dissociate_pub(self, key):
        pass

    def dissociate_hgnc(self, key):
        pass

    def make_obsolete(self, key):
        pass

    def ignore(self, key):
        return

    def load_dbxref(self, key):
        pass

    def load_dbxrefprop(self, key):
        pass

    def load_featureprop(self, key):
        pass
