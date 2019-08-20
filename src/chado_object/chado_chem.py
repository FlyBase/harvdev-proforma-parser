"""
.. module:: chado_chem
   :synopsis: The "chem" ChadoObject.

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
import re
import os
import yaml
from bioservices import ChEBI
from .chado_base import ChadoObject, FIELD_VALUE, FIELD_NAME
from harvdev_utils.production import (
    Cv, Cvterm, Pub, Pubprop, Pubauthor, PubRelationship, Db, Dbxref, PubDbxref, Organism,
    Feature
)
from harvdev_utils.chado_functions import get_or_create

import logging
from datetime import datetime

log = logging.getLogger(__name__)


class ChadoChem(ChadoObject):
    # TODO
    #  - Warn for mismatch between database ID; database name in CH1g.
    #  - In initial YAML validator, regex for proper ChEBI name and other db identifiers.
    #  - CHEBI or NCBI Chemical ID stored as synonym.

    def __init__(self, params):
        log.info('Initializing ChadoChem object.')
        ##########################################
        # Set up how to process each type of input
        ##########################################
        # self.type_dict = {'direct': self.load_direct}

        # self.delete_dict = {'direct': self.delete_direct,
        #               'obsolete': self.delete_obsolete}

        self.proforma_start_line_number = params.get('proforma_start_line_number')
        self.reference = params.get('reference')

        ###########################################################
        # Values queried later, placed here for reference purposes.
        ############################################################
        self.pub = None  # All other proforma need a reference to a pub
        self.chemical_feature_id = None  # The feature id used for the chemical.
        self.chebi_pub_id = None # Used for attributing chemical curation.

        # Initiate the parent.
        super(ChadoChem, self).__init__(params)

        ############################################################
        # Get processing info and data to be processed.
        # Please see the yml/chemical.yml file for more details
        ############################################################
        yml_file = os.path.join(os.path.dirname(__file__), 'yml/chemical.yml')
        # Populated self.process_data with all possible keys.
        self.process_data = self.load_reference_yaml(yml_file, params)

        #####################################################
        # Checking whether we're working with a new chemical.
        #####################################################
        if self.process_data['CH1f']['data'][FIELD_VALUE] == "new":
            self.new_chemical_entry = True
        else:
            self.new_chemical_entry = False

    def obtain_session(self, session):
        self.session = session

    def load_content(self):
        """
        Main processing routine.
        """

        self.pub = super(ChadoChem, self).pub_from_fbrf(self.reference, self.session)

        # Bang c first, as it supersedes all things.
        # if self.bang_c:
        #     self.bang_c_it()
        # if self.bang_d:
        #     self.bang_d_it()

        self.get_or_create_chemical()

        # for key in self.process_data:
        #     if self.process_data[key]['data']:
        #         log.debug("Processing {}".format(self.process_data[key]['data']))
        #         self.type_dict[self.process_data[key]['type']](key)

        timestamp = datetime.now().strftime('%c')
        curated_by_string = 'Curator: %s;Proforma: %s;timelastmodified: %s' % (
            self.curator_fullname, self.filename_short, timestamp)
        log.info('Curator string assembled as:')
        log.info('%s' % curated_by_string)

    def get_or_create_chemical(self):

        # Validate the identifier in an external database.
        # Also looks for conflicts between the external name and
        # the name specified for FlyBase. It also returns data that we use
        # to populate fields in Chado.
        bioservice_results, identifier = self.validate_fetch_identifier_at_external_db()

        identifier_accession_num_only = identifier.split(':')[1]

        # Look up organism id.
        organism = self.session.query(Organism). \
            filter(Organism.genus == 'Drosophila',
                   Organism.species == 'melanogaster').one()

        organism_id = organism.organism_id

        # Look up chemical cv term id.
        chemical = self.session.query(Cvterm).join(Cv). \
            filter(Cvterm.cv_id == Cv.cv_id,
                   Cvterm.name == 'chemical entity',
                   Cv.name == 'FlyBase miscellaneous CV',
                   Cvterm.is_obsolete == 0).one()

        chemical_id = chemical.cvterm_id

        # Check if we already have an existing entry.
        entry_already_exists = self.chemical_feature_lookup(organism_id, chemical_id)

        # Check if we already have an existing entry by feature name -> dbx xref.
        # FBch features -> dbxrefs are UNIQUE for EACH external database.
        # e.g. There should never be more than one connection from FBch -> ChEBI.
        # If so, someone has already made an FBch which corresponds to the that CheBI.
        # self.check_existing_dbxref(identifier_accession_num_only)

        # If we already have an entry and this should be be a new entry.
        if entry_already_exists and self.new_chemical_entry:
            self.critical_error(self.process_data['CH1a']['data'],
                                'An entry already exists in the database with this name: {}'
                                .format(entry_already_exists.uniquename))
        # If we're not dealing with a new entry.
        # Verify that the FBch and Name specified in the proforma match.
        elif entry_already_exists:
            if entry_already_exists.uniquename != self.process_data['CH1f']['data'][FIELD_VALUE]:
                self.critical_error(self.process_data['CH1f']['data'],
                                    'Name and FBch in this proforma do not match.')
        else:
            chemical = get_or_create(self.session, Feature, organism_id=organism_id,
                                     name=self.process_data['CH1a']['data'][FIELD_VALUE],
                                     type_id=chemical_id,
                                     uniquename='FBch:temp_0')

            log.info("New chemical entry created: {}".format(chemical.name))

    def check_existing_dbxref(self, identifier_access_num_only):
        log.debug('Querying for existing accession ({}) via feature -> dbx -> db.'.format(identifier_access_num_only))

        feature_dbxref_chemical_chebi_result = self.session.query(Feature, Dbxref, Db).\
            join(Feature, (Feature.dbxref_id == Dbxref.dbxref_id)).\
            join(Db, (Dbxref.db_id == Db.db_id)).\
            filter(Dbxref.accession == identifier_access_num_only).one_or_none()

        log.debug(feature_dbxref_chemical_chebi_result)

        if feature_dbxref_chemical_chebi_result:
            self.critical_error(self.process_data['CH3a']['data'],
                                'A feature -> ChEBI association already exists for this ID. Check: {}'
                                .format(feature_dbxref_chemical_chebi_result.feature_uniquename))

    def chemical_feature_lookup(self, organism_id, description_id):
        entry = self.session.query(Feature). \
            filter(Feature.name == self.process_data['CH1a']['data'][FIELD_VALUE],
                   Feature.type_id == description_id,
                   Feature.organism_id == organism_id).one_or_none()

        return entry

    def look_up_chebi_reference(self):
        log.debug('Retrieving ChEBI FBrf for association.')

        chebi_publication_title = 'ChEBI: Chemical Entities of Biological Interest, EBI.'

        chebi_ref_pub_id_query = self.session.query(Pub). \
            filter(Pub.title == chebi_publication_title).one()

        self.chebi_pub_id = chebi_ref_pub_id_query.pub_id
        log.debug('Returned ChEBI FBrf pub id as {}'.format(self.chebi_pub_id))

    def validate_fetch_identifier_at_external_db(self):
        # TODO Check identifier and use proper database.
        # Initial implementation will be ChEBI only.

        identifier_unprocessed = self.process_data['CH3a']['data'][FIELD_VALUE]

        identifier, identifier_name = self.split_identifier_and_name(identifier_unprocessed)

        # TODO Check for valid ID format.
        self.check_valid_id(identifier)

        ch = ChEBI()
        results = ch.getCompleteEntity(identifier)
        if not results:
            self.critical_error(self.process_data['CH3a']['data'],
                                'No results found when querying ChEBI for {}'
                                .format(identifier))
            return
        name_from_chebi = results.chebiAsciiName
        definition = results.definition
        CAS_number = results.RegistryNumbers


        # Check whether the name intended to be used in FlyBase matches
        # the name returned from the database.
        if name_from_chebi != self.process_data['CH1a']['data'][FIELD_VALUE]:
            self.warning_error(self.process_data['CH1a']['data'],
                               'ChEBI name does not match name specified for FlyBase: {} -> {}'
                               .format(name_from_chebi,
                                       self.process_data['CH1a']['data'][FIELD_VALUE]))
        else:
            log.info('Queried name \'{}\' matches name used in proforma \'{}\''
                     .format(name_from_chebi, self.process_data['CH1a']['data'][FIELD_VALUE]))

        # Check whether the identifier_name supplied by the curator matches
        # the name returned from the database.
        if identifier_name:
            if name_from_chebi != identifier_name:
                self.critical_error(self.process_data['CH3a']['data'],
                                    'ChEBI name does not match name specified in identifier field: {} -> {}'
                                    .format(name_from_chebi,
                                            identifier_name))
        return results, identifier

    def check_valid_id(self, identifier):
        # Added regex checks for identifiers here.
        pass

    def split_identifier_and_name(self, identifier_unprocessed):
        # Strip away the name if one is supplied with the identifier.
        identifier = None
        identifier_name = None
        if ';' in identifier_unprocessed:
            log.debug('Semicolon found, splitting identifier: {}'.format(identifier_unprocessed))
            identifier_split_list = identifier_unprocessed.split(';')
            identifier = identifier_split_list.pop(0).strip()
            identifier_name = identifier_split_list.pop(0).strip()
            if identifier_split_list:  # If the list is not empty by this point, raise an error.
                self.critical_error(self.process_data['CH3a']['data'],
                                    'Error splitting identifier and name using semicolon.')
                identifier_name = None # Set name to None before returning. It might be wrong otherwise.
                return identifier, identifier_name
        else:
            identifier = identifier_unprocessed.strip()

        return identifier, identifier_name
