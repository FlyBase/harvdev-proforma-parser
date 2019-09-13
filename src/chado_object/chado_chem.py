"""
.. module:: chado_chem
   :synopsis: The "chem" ChadoObject.

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
from bioservices import ChEBI
from .chado_base import ChadoObject, FIELD_VALUE
from harvdev_utils.production import (
    Cv, Cvterm, Pub, Db, Dbxref, Organism,
    Feature, Featureprop, FeaturePub, FeatureRelationship, FeatureRelationshipprop,
    FeatureSynonym, Synonym
)
from harvdev_utils.chado_functions import get_or_create
from datetime import datetime
from pprint import pprint, pformat
import os
import logging
import pubchempy
import json

log = logging.getLogger(__name__)
# Stop bioservices from outputting tons of unnecessary info in DEBUG mode.
logging.getLogger("suds").setLevel(logging.INFO)


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
        self.chebi_pub_id = None  # Used for attributing chemical curation.
        self.pubchem_pub_id = None  # Used for attributing chemical curation.

        # Chemical storage dictionary.
        # This dictionary contains all the information required to create a new FBch.
        # The nested dictionaries contain the data as well as the source.
        # This style allows for proper attribution when creating the entries in FB.

        self.chemical_information = {
            'identifier': {
                'data': None,
                'source': None
            },
            'description': {
                'data': None,
                'source': None
            },
            'inchikey': {
                'data': None,
                'source': None
            },
            'name': {
                'data': None,
                'source': None
            }
        }

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

        # bang c first as this supersedes all things
        if self.bang_c:
            self.bang_c_it()
        if self.bang_d:
            self.bang_d_it()

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
        identifier_found = self.validate_fetch_identifier_at_external_db()

        if identifier_found is False:
            return

        identifier_accession_num_only = self.chemical_information['identifier']['data'].split(':')[1]
        log.debug('Identifier accession number only: {}'.format(identifier_accession_num_only))

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

        chebi_database = self.session.query(Db). \
            filter(Db.name == 'CHEBI').one()

        chebi_database_id = chebi_database.db_id

        # Check if we already have an existing entry.
        entry_already_exists = self.chemical_feature_lookup(organism_id, chemical_id)

        # Check if we already have an existing entry by feature name -> dbx xref.
        # FBch features -> dbxrefs are UNIQUE for EACH external database.
        # e.g. There should never be more than one connection from FBch -> ChEBI.
        # If so, someone has already made an FBch which corresponds to the that CheBI.
        self.check_existing_dbxref(identifier_accession_num_only)

        # If we already have an entry and this should be be a new entry.
        if entry_already_exists and self.new_chemical_entry:
            self.critical_error(self.process_data['CH1a']['data'],
                                'An entry already exists in the database with this name: {}'
                                .format(entry_already_exists.uniquename))
            return

        # If we're not dealing with a new entry.
        # Verify that the FBch and Name specified in the proforma match.
        elif entry_already_exists:
            if entry_already_exists.uniquename != self.process_data['CH1f']['data'][FIELD_VALUE]:
                self.critical_error(self.process_data['CH1f']['data'],
                                    'Name and FBch in this proforma do not match.')
                return

        chemical, _ = get_or_create(self.session, Feature, organism_id=organism_id,
                                    name=self.process_data['CH1a']['data'][FIELD_VALUE],
                                    type_id=chemical_id,
                                    uniquename='FBch:temp_0')

        log.info("New chemical entry created: {}".format(chemical.name))

        dbx_ref, _ = get_or_create(self.session, Dbxref, db_id=chebi_database_id,
                                   accession=identifier_accession_num_only)

        log.debug("Creating new dbxref: {}".format(dbx_ref.dbxref_id))

        #  TODO Need pub_dbxref entry here?

        log.debug("Updating FBch with dbxref.dbxref_id: {}".format(dbx_ref.dbxref_id))
        chemical.dbxref_id = dbx_ref.dbxref_id

        feature_pub, _ = get_or_create(self.session, FeaturePub, feature_id=chemical.feature_id,
                                       pub_id=self.pub.pub_id)

        log.debug("Creating new feature_pub: {}".format(feature_pub.feature_pub_id))

        # TODO Do we ever remove feature_pubs once all synonym connections are removed?
        # TODO Probably not because other objects can create feature_pub relationships?

        # Add the identifier as a synonym.
        self.modify_synonym('add', chemical.feature_id)

        # Add the description as a featureprop.
        self.add_description_to_featureprop(chemical.feature_id)

        # If CH3b is declared as 'y', store that information in feature_dbxrefprop
        # TODO Are we creating a feature_dbxrefprop table? More discussion needed.

        # If CH4a is filled out, link two features together.
        if self.has_data('CH4a'):
            self.add_relationship_to_other_FBch(chemical.feature_id)

    def add_relationship_to_other_FBch(self, feature_id):
        """
        Adds a relationship between the FBch features of CH1f and CH4a.

        :param feature_id: specify the feature id used in the feature table.
        :return:
        """
        ch4a_value = self.process_data['CH4a']['data'][FIELD_VALUE]

        log.debug('Looking up feature id for existing chemical feature {}.'.format(ch4a_value))

        if ch4a_value.startswith('FBch'):
            feature_for_related_fbch = self.session.query(Feature). \
                filter(Feature.uniquename == ch4a_value).one()
        else:
            feature_for_related_fbch = self.session.query(Feature). \
                filter(Feature.name == ch4a_value).one()

        related_fbch_feature_id = feature_for_related_fbch.feature_id

        description_cv_id = self.cvterm_query('relationship type', 'derived_from', self.session)

        log.debug('Creating relationship between feature in CH1f and CH4a.')
        get_or_create(self.session, FeatureRelationship, subject_id=feature_id,
                      object_id=related_fbch_feature_id, type_id=description_cv_id)

    def add_description_to_featureprop(self, feature_id):
        """
        Associates the description from PubChem to a feature via featureprop.

        :param feature_id: str. Specify the feature id used in the featureprop table.
        :return:
        """

        log.debug('Adding PubChem description to featureprop.')

        description_cvterm_id = self.cvterm_query('property type', 'description', self.session)

        get_or_create(self.session, Featureprop, feature_id=feature_id,
                      type_id=description_cvterm_id, value=self.chemical_information['description']['data'])

    def modify_synonym(self, process, feature_id):
        """

        :param process: accepts either 'add' or 'remove'.
        'add' adds a new synonym to the chemical feature.
        'remove' removes the synonym from the chemical feature.

        :param feature_id: specify the feature id used in the feature_synonym table.

        :return:
        """
        # insert into feature_synonym(is_internal, pub_id, synonym_id, is_current, feature_id) values('FALSE', 221699, 6555779, 'FALSE', 3107733)

        log.debug('Looking up synonym type cv and symbol cv term.')
        symbol_cv_lookup = self.session.query(Cv, Cvterm). \
            join(Cvterm, (Cvterm.cv_id == Cv.cv_id)). \
            filter(Cv.name == 'synonym type'). \
            filter(Cvterm.name == 'symbol').one()

        symbol_cv_id = symbol_cv_lookup[1].cvterm_id

        # Look up the ChEBI / PubChem reference pub_id's.
        # Assigns a value to 'self.chebi_pub_id' and 'self.pubchem_pub_id'
        self.look_up_static_references()

        if process == 'add':
            log.info("Adding new synonym entry for {}.".format(self.chemical_information['identifier']['data']))
            new_synonym, _ = get_or_create(self.session, Synonym, type_id=symbol_cv_id,
                                           synonym_sgml=self.chemical_information['name']['data'],
                                           name=self.chemical_information['name']['data'])

            get_or_create(self.session, FeatureSynonym, feature_id=feature_id,
                          pub_id=self.chebi_pub_id, synonym_id=new_synonym.synonym_id,
                          is_current=False)

        elif process == 'remove':
            log.info("Removing synonym entry for {}.".format(self.chemical_information['identifier']['data']))
            synonym_lookup = self.session.query(Synonym). \
                filter(Synonym.name == self.chemical_information['name']['data']).\
                filter(Synonym.synonym_sgml == self.chemical_information['name']['data']).\
                filter(Synonym.type_id == symbol_cv_id).\
                delete()

            # TODO Remove feature_synonym row.
            log.debug(synonym_lookup)

    def check_existing_dbxref(self, identifier_access_num_only):
        log.debug('Querying for existing accession ({}) via feature -> dbx -> db.'.format(identifier_access_num_only))

        feature_dbxref_chemical_chebi_result = self.session.query(Feature, Dbxref, Db).\
            join(Feature, (Feature.dbxref_id == Dbxref.dbxref_id)).\
            join(Db, (Dbxref.db_id == Db.db_id)).\
            filter(Dbxref.accession == identifier_access_num_only).one_or_none()

        # feature_dbxref_chemical_chebi_result[0] accesses the 'Feature' object from the result.
        if feature_dbxref_chemical_chebi_result:
            self.critical_error(self.process_data['CH3a']['data'],
                                'A feature -> ChEBI association already exists for this ID. Check: {}'
                                .format(feature_dbxref_chemical_chebi_result[0].uniquename))

    def chemical_feature_lookup(self, organism_id, description_id):
        entry = self.session.query(Feature). \
            filter(Feature.name == self.process_data['CH1a']['data'][FIELD_VALUE],
                   Feature.type_id == description_id,
                   Feature.organism_id == organism_id).one_or_none()

        return entry

    def look_up_static_references(self):
        log.debug('Retrieving ChEBI / PubChem FBrfs for association.')

        chebi_publication_title = 'ChEBI: Chemical Entities of Biological Interest, EBI.'
        pubchem_publication_title = 'PubChem, NIH.'

        chebi_ref_pub_id_query = self.session.query(Pub). \
            filter(Pub.title == chebi_publication_title).one()

        pubchem_ref_pub_id_query = self.session.query(Pub). \
            filter(Pub.title == pubchem_publication_title).one()

        self.chebi_pub_id = chebi_ref_pub_id_query.pub_id
        self.pubchem_pub_id = pubchem_ref_pub_id_query.pub_id
        log.debug('Returned ChEBI FBrf pub id as {}'.format(self.chebi_pub_id))
        log.debug('Returned PubChem FBrf pub id as {}'.format(self.pubchem_pub_id))

    def validate_fetch_identifier_at_external_db(self):
        # Identifiers and names for ChEBI / PubChem entries are processed at their respective db.
        # However, InChIKey entries and definitions always come from PubChem.
        # This is because PubChem cites ChEBI (as well as other external definitions) whereas
        # ChEBI does not provide this service.

        identifier_unprocessed = self.process_data['CH3a']['data'][FIELD_VALUE]

        identifier, identifier_name = self.split_identifier_and_name(identifier_unprocessed)
        log.debug('Found identifier: {} and identifier_name: {}'.format(identifier, identifier_name))

        database_to_query = identifier.split(':')[0]

        database_dispatch_dictionary = {
            'CHEBI': self.check_chebi_for_identifier,
            'PubChem': self.check_pubchem_for_identifier
        }

        # TODO Check for valid ID format.
        self.check_valid_id(identifier)

        # Obtain our identifier, name, definition, and InChIKey from ChEBI / PubChem.
        try:
            identifier_and_data = database_dispatch_dictionary[database_to_query](identifier, identifier_name)
        except KeyError:
            self.critical_error(self.process_data['CH3a']['data'],
                                'Database name not recognized from identifier: {}'.format(database_to_query))
            return False

        if identifier_and_data is False:  # Errors are already declared in the sub-functions.
            return False

        # If we're at this stage, we have all our data for PubChem BUT
        # for a ChEBI query we need to go to PubChem for the definition.
        if self.chemical_information['identifier']['source'] != 'PubChem':
            # Set the identifier name to the result queried from ChEBI.
            identifier_name = self.chemical_information['name']['data']
            self.check_pubchem_for_identifier(identifier, identifier_name)

        return True

    def check_chebi_for_identifier(self, identifier, identifier_name):
        # Return True if data is successfully found.
        # Return False if there are any issues.

        ch = ChEBI()
        result = ch.getCompleteEntity(identifier)
        if not result:
            self.critical_error(self.process_data['CH3a']['data'],
                                'No results found when querying ChEBI for {}'
                                .format(identifier))
            return False

        # Obtain name and inchikey from results.
        name_from_chebi = result.chebiAsciiName
        inchikey = None
        try:
            inchikey = result.inchiKey
        except AttributeError:
            self.warning_error(self.process_data['CH3a']['data'],
                               'No InChIKey found for entry: {}'
                               .format(identifier))

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
                return False

        self.chemical_information['identifier']['data'] = identifier
        self.chemical_information['identifier']['source'] = 'ChEBI'
        self.chemical_information['name']['data'] = name_from_chebi
        self.chemical_information['name']['source'] = 'ChEBI'
        self.chemical_information['inchikey']['data'] = inchikey
        self.chemical_information['inchikey']['source'] = 'ChEBI'

        return True

    def check_pubchem_for_identifier(self, identifier, identifier_name):
        # TODO PubChem code for PubChem identifiers goes here.

        # Definitions always come from PubChem, regardless of identifier source.
        if not self.chemical_information['description']['data']:  # If the list is empty.

            log.info('Searching for definitions on PubChem.')
            results = pubchempy.get_compounds(identifier_name, 'name')
            cid_for_definition = results[0].cid
            log.info('Found PubChem CID: {} from query using {}'. format(cid_for_definition, identifier_name))

            description = pubchempy.request(cid_for_definition, operation='description')

            raw_data = description.read()
            encoding = description.info().get_content_charset('utf8')  # JSON default
            description_data = json.loads(raw_data.decode(encoding))
            log.debug(pformat(description_data))

            # We need to format the description from PubChem into a string to be loaded as a featureprop.
            string_to_add_for_description = ''

            # TODO Need to coordinate with IU on how to store / retrieve this data.
            for description_item in description_data['InformationList']['Information']:
                if 'Description' in description_item.keys() and 'DescriptionSourceName' in description_item.keys():
                    formatted_string = '{}: {}'.format(description_item['DescriptionSourceName'],
                                                           description_item['Description'])

                    string_to_add_for_description += formatted_string

            self.chemical_information['description']['data'] = string_to_add_for_description
            log.debug(pformat(self.chemical_information['description']['data']))

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
                identifier_name = None  # Set name to None before returning. It might be wrong otherwise.
                return identifier, identifier_name
        else:
            identifier = identifier_unprocessed.strip()

        return identifier, identifier_name
