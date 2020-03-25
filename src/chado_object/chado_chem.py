"""

:synopsis: The "chem" ChadoObject.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>, Ian Longden <ilongden@morgan.harvard.edu>
"""

from harvdev_utils.production import (
    Pub, Db, Dbxref,
    Feature, Featureprop, FeaturePub, FeatureRelationship,
    FeatureSynonym, Synonym, FeatureRelationshipprop
)

from harvdev_utils.chado_functions import get_or_create, DataError
from harvdev_utils.chado_functions.external_lookups import ExternalLookup
from harvdev_utils.char_conversions import sgml_to_plain_text
from .chado_base import ChadoObject, FIELD_VALUE
from chado_object.utils.feature_synonym import fs_add_by_synonym_name_and_type, fs_remove_current_symbol
from chado_object.utils.feature import feature_symbol_lookup, feature_synonym_lookup, feature_name_lookup
from chado_object.utils.organism import get_default_organism_id
from chado_object.utils.util_errors import CodingError

from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime
import os
import logging

log = logging.getLogger(__name__)


class ChadoChem(ChadoObject):
    """Process the Chemical Proforma."""

    def __init__(self, params):
        """Initialise the chado object."""
        log.debug('Initializing ChadoChem object.')

        self.proforma_start_line_number = params.get('proforma_start_line_number')
        self.reference = params.get('reference')

        ###########################################################
        # Values queried later, placed here for reference purposes.
        ############################################################
        self.pub = None             # All other proforma need a reference to a pub
        self.chemical = None        # The chemical object, to get feature_id use self.chemical.feature_id.
        self.chebi_pub_id = None    # Used for attributing chemical curation.
        self.pubchem_pub_id = None  # Used for attributing chemical curation.

        # yaml file defines what to do with each field. Follow the light
        self.type_dict = {'featureprop': self.load_featureprop,
                          'synonym': self.load_synonym,
                          'ignore': self.ignore,
                          'value': self.ignore}

        self.delete_dict = {'ignore': self.ignore,
                            'synonym': self.rename_synonym,
                            'featureprop': self.delete_featureprop,
                            'value': self.change_featurepropvalue}
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
            },
            'synonyms': {
                'data': [],
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

    def ignore(self, key):
        """Ignore."""
        pass

    def load_content(self, references):
        """Process the proforma fields."""
        try:
            self.pub = references['ChadoPub']
        except KeyError:
            message = "Unable to find publication."
            self.critical_error(self.process_data['CH1a']['data'], message)
            return None

        self.get_or_create_chemical()
        if not self.chemical:
            return

        # bang c first as this supersedes all things
        if self.bang_c:
            self.bang_c_it()
        if self.bang_d:
            self.bang_d_it()

        for key in self.process_data:
            if self.process_data[key]['data']:
                log.debug("Processing {}".format(self.process_data[key]['data']))
                self.type_dict[self.process_data[key]['type']](key)

        timestamp = datetime.now().strftime('%c')
        curated_by_string = 'Curator: %s;Proforma: %s;timelastmodified: %s' % (
            self.curator_fullname, self.filename_short, timestamp)
        log.debug('Curator string assembled as:')
        log.debug('%s' % curated_by_string)

    def fetch_by_FBch_and_check(self, chemical_cvterm_id):
        """Fetch by the FBch (CH1f) and check the name is the same if it is given (CH1a).

        Args:
            chemical_cvterm_id: cvterm_id to be used as type in getting feature.

        Raises:
            critical error if CH1f and CH1a are specified and do not match.
        """
        self.chemical, is_new = get_or_create(self.session, Feature, type_id=chemical_cvterm_id,
                                              uniquename=self.process_data['CH1f']['data'][FIELD_VALUE])
        if is_new:
            message = "Could not find {} in the database. Please check it exists.".format(self.process_data['CH1f']['data'][FIELD_VALUE])
            self.critical_error(self.process_data['CH1f']['data'], message)
        if self.has_data('CH1a'):
            if self.process_data['CH1a']['data'][FIELD_VALUE] != self.chemical.name:
                message = "Name given does not match that in database. {} does not equal {}".\
                    format(self.process_data['CH1f']['data'][FIELD_VALUE],
                           self.chemical.name)
                self.critical_error(self.process_data['CH1a']['data'], message)

    def get_or_create_chemical(self):
        """Validate the identifier in an external database.

        Also looks for conflicts between the external name and
        the name specified for FlyBase. It also returns data that we use
        to populate fields in Chado.

        Look up the ChEBI / PubChem reference pub_id's.
        Assigns a value to 'self.chebi_pub_id' and 'self.pubchem_pub_id'
        """
        self.look_up_static_references()

        # Look up chemical cv term id. Ch1f yaml data for cv and cvterms
        chemical_cvterm_id = self.cvterm_query(self.process_data['CH1f']['cv'], self.process_data['CH1f']['cvterm'])

        if not self.new_chemical_entry:  # Fetch by FBch and check CH1a ONLY
            self.fetch_by_FBch_and_check(chemical_cvterm_id)
            return

        # So we have a new chemical, lets get the data for this.
        identifier_found = self.validate_fetch_identifier_at_external_db()

        if not identifier_found:
            return

        identifier_accession_num_only = self.chemical_information['identifier']['data'].split(':')[1]
        log.debug('Identifier accession number only: {}'.format(identifier_accession_num_only))

        exists_already = self.check_existing_already()
        if exists_already:
            self.chemical = exists_already
            return

        # Check if we already have an existing entry by feature name -> dbx xref.
        # FBch features -> dbxrefs are UNIQUE for EACH external database.
        # e.g. There should never be more than one connection from FBch -> ChEBI.
        # If so, someone has already made an FBch which corresponds to the that CheBI.
        self.check_existing_dbxref(identifier_accession_num_only)

        # Look up organism id.
        organism_id = get_default_organism_id(self.session)

        database = self.session.query(Db). \
            filter(Db.name == self.chemical_information['identifier']['source']).one()

        self.chemical, _ = get_or_create(self.session, Feature, organism_id=organism_id,
                                         # name=self.process_data['CH1a']['data'][FIELD_VALUE],
                                         name=self.chemical_information['name']['data'].lower(),
                                         type_id=chemical_cvterm_id,
                                         uniquename='FBch:temp_0')

        log.debug("New chemical entry created: {}".format(self.chemical.name))

        dbx_ref, _ = get_or_create(self.session, Dbxref, db_id=database.db_id,
                                   accession=identifier_accession_num_only)

        log.debug("Creating new dbxref: {}".format(dbx_ref.dbxref_id))
        log.debug("Updating FBch with dbxref.dbxref_id: {}".format(dbx_ref.dbxref_id))
        self.chemical.dbxref_id = dbx_ref.dbxref_id

        feature_pub, _ = get_or_create(self.session, FeaturePub, feature_id=self.chemical.feature_id,
                                       pub_id=self.pub.pub_id)
        log.debug("Created new feature_pub: {}".format(feature_pub.feature_pub_id))
        # Add pub link to Chebi or pubchem
        pub_id = self.get_external_chemical_pub_id('CH3a')
        feature_pub, _ = get_or_create(self.session, FeaturePub, feature_id=self.chemical.feature_id, pub_id=pub_id)
        log.debug("Created new feature_pub: {}".format(feature_pub.feature_pub_id))

        # TODO Do we ever remove feature_pubs once all synonym connections are removed?
        # TODO Probably not because other objects can create feature_pub relationships?

        # Add the identifier as a synonym and other synonyms
        self.process_synonyms_from_external_db()

        # Add the description as a featureprop.
        self.add_description_to_featureprop()

        # Add the inchikey as a featureprop.
        self.add_inchikey_to_featureprop()

    def check_existing_already(self):
        # Check if we already have an existing entry.
        #
        # This needs a little explaining.
        # We check the name and all the synonyms.
        # This is becouse ChEBI and PubChem could be the same and we do not want
        # duplicate entries. Does not matter if it is stored via ChEBI or PubChem
        # but we only really want a chemical in the database once.
        #
        # This also sets self.new_chemical_entry to Flase if found even if the curator
        # has set it to new in the proforma, Curators requested no consequences of loading
        # a chemical more than once, apart from it not being duplicated again.
        #

        #
        # Look up organism id.
        #
        organism_id = get_default_organism_id(self.session)

        #
        # check name from lookup
        #
        entry_already_exists = None
        entry_already_exists = self.chemical_feature_lookup(organism_id, 'CH3a', self.chemical_information['name']['data'].lower(), current=True)
        if entry_already_exists:
            self.new_chemical_entry = False
            self.warning_error(self.process_data['CH3a']['data'],
                               'An entry already exists in the database with this name: {}'
                               .format(entry_already_exists.name))
            return entry_already_exists

        #
        # check Flybase name if given
        #
        if self.has_data('CH1a'):
            entry_already_exists = self.chemical_feature_lookup(organism_id, 'CH1a', self.process_data['CH1a']['data'][FIELD_VALUE], current=True)

        # If we already have an entry and we already know it is new then we have a problem.
        if entry_already_exists:
            self.new_chemical_entry = False
            self.warning_error(self.process_data['CH1a']['data'],
                               'An entry already exists in the database with this name: {}'
                               .format(entry_already_exists.name))
            return entry_already_exists

        #
        # Check for any symbol synonym can be not current and if found Just give a warning
        #
        entry_already_exists = self.chemical_feature_lookup(organism_id, 'CH3a', self.chemical_information['name']['data'].lower(), current=False)
        if entry_already_exists:
            self.new_chemical_entry = False
            return entry_already_exists

        if self.has_data('CH1a') and not entry_already_exists:
            entry_already_exists = self.chemical_feature_lookup(organism_id, 'CH1a', self.process_data['CH1a']['data'][FIELD_VALUE], current=False)
            if entry_already_exists:
                self.new_chemical_entry = False
                return entry_already_exists
        return entry_already_exists

    def delete_featureprop(self, key, bangc=True):
        prop_cv_id = self.cvterm_query(self.process_data[key]['cv'], self.process_data[key]['cvterm'])

        fp, is_new = get_or_create(self.session, Featureprop, feature_id=self.chemical.feature_id,
                                   type_id=prop_cv_id)
        if is_new:
            message = "No current {} field specified in chado so cannot bangc it".format(key)
            self.critical_error(self.process_data[key]['data'], message)
        else:
            self.session.delete(fp)
        self.process_data[key]['data'] = None

    def change_featurepropvalue(self, key, bangc=True):
        prop_cv_id = self.cvterm_query(self.process_data['CH3b']['cv'], self.process_data['CH3b']['cvterm'])

        fp, is_new = get_or_create(self.session, Featureprop, feature_id=self.chemical.feature_id,
                                   type_id=prop_cv_id)
        if is_new:
            message = "No current value specified in chado so cannot bangc it"
            self.critical_error(self.process_data[key]['data'], message)
        else:
            fp.value = self.process_data[key]['data'][FIELD_VALUE]
        self.process_data[key]['data'] = None
        self.process_data['CH3b']['data'] = None

    def rename_synonym(self, key, bangc=True):
        if not self.has_data(key):
            message = "Bangc MUST have a value."
            self.critical_error(self.process_data[key]['data'], message)
            return
        self.load_synonym(key)
        self.process_data[key]['data'] = None

    def get_external_chemical_pub_id(self, key):
        pub_id = None
        db_type = self.session.query(Db).join(Dbxref).join(Feature).\
            filter(Feature.dbxref_id == Dbxref.dbxref_id,
                   Db.db_id == Dbxref.db_id,
                   Feature.feature_id == self.chemical.feature_id).one()
        if db_type.name == "CHEBI":
            pub_id = self.chebi_pub_id
        elif db_type.name == "PubChem":
            pub_id = self.pubchem_pub_id
        else:
            message = "Do not know how to look up pub for the feature {} based on db {}.".format(self.chemical.name, db_type.name)
            self.critical_error(self.process_data[key]['data'], message)
        return pub_id

    def load_synonym(self, key):

        # Chemicals can be listed more than once
        # But are only loaded once. We do not allow synoym changes
        # for these repeated chemicals. !c Should be used in this case
        if not self.new_chemical_entry and key not in self.bang_c:
            return
        cv_name = self.process_data[key]['cv']
        cvterm_name = self.process_data[key]['cvterm']
        is_current = self.process_data[key]['is_current']

        if 'pub' in self.process_data[key] and self.process_data[key]['pub'] == 'current':
            pub_id = self.pub.pub_id
        else:
            # is this chebi or pubchem
            pub_id = self.get_external_chemical_pub_id(key)

        # remove the current symbol if is_current is set and yaml says remove old is_current
        if 'remove_old' in self.process_data[key] and self.process_data[key]['remove_old']:
            fs_remove_current_symbol(self.session, self.chemical.feature_id, cv_name, cvterm_name, pub_id)

        # add the new synonym
        if type(self.process_data[key]['data']) is list:
            for item in self.process_data[key]['data']:
                fs_add_by_synonym_name_and_type(self.session, self.chemical.feature_id,
                                                item[FIELD_VALUE], cv_name, cvterm_name, pub_id,
                                                synonym_sgml=None, is_current=is_current, is_internal=False)
        else:
            fs_add_by_synonym_name_and_type(self.session, self.chemical.feature_id,
                                            self.process_data[key]['data'][FIELD_VALUE], cv_name, cvterm_name, pub_id,
                                            synonym_sgml=None, is_current=is_current, is_internal=False)

            if is_current and cvterm_name == 'symbol':
                self.chemical.name = sgml_to_plain_text(self.process_data[key]['data'][FIELD_VALUE])

    def load_featureprop(self, key):
        """
        Store the feature prop. If there is a value then it will have a 'value' in the yaml
        pointing to the field that is holding the value.
        """
        value = None
        if ('value' in self.process_data[key] and self.has_data(self.process_data[key]['value'])):
            value = self.process_data[self.process_data[key]['value']]['data'][FIELD_VALUE]
        prop_cv_id = self.cvterm_query(self.process_data[key]['cv'], self.process_data[key]['cvterm'])

        fp, is_new = get_or_create(self.session, Featureprop, feature_id=self.chemical.feature_id,
                                   type_id=prop_cv_id)
        if is_new:
            fp.value = value
        elif fp.value:
            message = "Already has a value. Use bangc to change it"
            self.critical_error(self.process_data[self.process_data[key]['value']]['data'], message)

    def load_feature_relationship(self, key):
        """
        Adds a relationship between the FBch features of CH1f and key (at the moment just CH4a).

        :return:

        NOTE: Never called as this functionality was removed.
              Keeping code here for a short while incase that changes.
        """
        ch4a_value = self.process_data[key]['data'][FIELD_VALUE]

        log.debug('Looking up feature id for existing chemical feature {}.'.format(ch4a_value))

        if ch4a_value.startswith('FBch'):
            feature_for_related_fbch = self.session.query(Feature). \
                filter(Feature.uniquename == ch4a_value).one()
        else:
            try:
                feature_for_related_fbch = feature_symbol_lookup(self.session, 'chemical entity', ch4a_value)
            except NoResultFound:
                message = "Could not find {} in database.".format(ch4a_value)
                self.critical_error(self.process_data[key]['data'], message)
                return
            except CodingError as e:
                self.critical_error(self.process_data[key]['data'], e.error)
                return

        related_fbch_feature_id = feature_for_related_fbch.feature_id

        description_cv_id = self.cvterm_query(self.process_data[key]['cv'], self.process_data[key]['cvterm'])

        log.debug('Creating relationship between feature in CH1f and CH4a.')
        feat_rel, _ = get_or_create(self.session, FeatureRelationship, subject_id=self.chemical.feature_id,
                                    object_id=related_fbch_feature_id, type_id=description_cv_id)
        prop_key = self.process_data[key]['prop']
        if self.has_data(prop_key):
            prop_cv_id = self.cvterm_query(self.process_data[prop_key]['cv'], self.process_data[prop_key]['cvterm'])

            get_or_create(self.session, FeatureRelationshipprop,
                          feature_relationship_id=feat_rel.feature_relationship_id,
                          type_id=prop_cv_id,
                          value=self.process_data[prop_key]['data'][FIELD_VALUE])

    def add_description_to_featureprop(self):
        """
        Associates the description from PubChem to a feature via featureprop.

        :return:
        """

        log.debug('Adding PubChem description to featureprop.')

        description_cvterm_id = self.cvterm_query('property type', 'description')

        get_or_create(self.session, Featureprop, feature_id=self.chemical.feature_id,
                      type_id=description_cvterm_id, value=self.chemical_information['description']['data'])

    def add_inchikey_to_featureprop(self):
        """
        Associates the inchikey from PubChem to a feature via featureprop.

        :return:
        """
        if not self.chemical_information['inchikey']['data']:
            return

        log.debug('Adding PubChem description to featureprop.')

        description_cvterm_id = self.cvterm_query('property type', 'inchikey')

        get_or_create(self.session, Featureprop, feature_id=self.chemical.feature_id,
                      type_id=description_cvterm_id, value=self.chemical_information['inchikey']['data'])

    def process_synonyms_from_external_db(self):
        """
        Add the synonyms obtained from the external db for the chemical.
        :return:
        """
        # insert into feature_synonym(is_internal, pub_id, synonym_id, is_current, feature_id) values('FALSE', 221699, 6555779, 'FALSE', 3107733)

        log.debug('Looking up synonym type cv and symbol cv term.')
        symbol_cv_id = self.cvterm_query('synonym type', 'symbol')

        if self.chemical_information['identifier']['source'] == "CHEBI":
            pub_id = self.chebi_pub_id
        else:
            pub_id = self.pubchem_pub_id

        seen_it = set()
        if self.chemical_information['synonyms']['data']:
            log.debug("Adding non current synonyms {}".format(self.chemical_information['synonyms']['data']))
            for item in self.chemical_information['synonyms']['data']:
                item_lower = item.lower()[:255]  # Max 255 chars
                if item_lower in seen_it:
                    log.debug("Ignoring {} as already seen".format(item_lower))
                    continue
                log.debug("Adding synonym {}".format(item_lower))
                new_synonym, _ = get_or_create(self.session, Synonym, type_id=symbol_cv_id,
                                               synonym_sgml=item_lower,
                                               name=item_lower)
                seen_it.add(item_lower)
                fs, _ = get_or_create(self.session, FeatureSynonym, feature_id=self.chemical.feature_id,
                                      pub_id=pub_id, synonym_id=new_synonym.synonym_id)
                fs.is_current = False

        log.debug("Adding new synonym entry for {}.".format(self.chemical_information['identifier']['data']))
        name_lower = self.chemical_information['name']['data'].lower()[:255]
        new_synonym, _ = get_or_create(self.session, Synonym, type_id=symbol_cv_id,
                                       synonym_sgml=name_lower,
                                       name=name_lower)

        fs, _ = get_or_create(self.session, FeatureSynonym, feature_id=self.chemical.feature_id,
                              pub_id=pub_id, synonym_id=new_synonym.synonym_id)
        fs.is_current = True

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

    def chemical_feature_lookup(self, organism_id, key_name, name, current=True):
        log.debug("chemical feature lookup for {} and current = {}".format(name, current))
        entry = None
        if current:
            entry = feature_name_lookup(self.session, name.lower(),
                                        organism_id=organism_id, type_name='chemical entity')
        else:
            try:
                features = feature_synonym_lookup(self.session, 'chemical entity',
                                                  name.lower(),
                                                  organism_id=organism_id)
            except DataError:
                return entry
            if features:
                log.debug("features = {}".format(features))
                message = "Synonym found for this already: Therefore not reloading Chemical Entity but using existing one {}.".format(features[0].name)
                self.warning_error(self.process_data[key_name]['data'], message)
                return features[0]
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
        if not identifier_name:
            return False
        log.debug('Found identifier: {} and identifier_name: {}'.format(identifier, identifier_name))

        database_to_query = identifier.split(':')[0]
        log.debug("DB is '{}'".format(database_to_query))
        database_dispatch_dictionary = {
            'CHEBI': self.check_chebi_for_identifier,
            'PubChem': self.check_pubchem_for_identifier
        }

        # TODO Check for valid ID format.
        self.check_valid_id(identifier)

        # Obtain our identifier, name, definition, and InChIKey from ChEBI / PubChem.
        try:
            identifier_and_data = database_dispatch_dictionary[database_to_query](identifier, identifier_name)
            log.debug("identifier_and_data is {}".format(identifier_and_data))
        except KeyError as e:
            self.critical_error(self.process_data['CH3a']['data'],
                                'Database name not recognized from identifier: {}. {}'.format(database_to_query, e))
            return False

        if identifier_and_data is False:  # Errors are already declared in the sub-functions.
            return False

        # If we're at this stage, we have all our data for PubChem BUT
        # for a ChEBI query we need to go to PubChem for the definition.
        if self.chemical_information['identifier']['source'] != 'PubChem':
            # Set the identifier name to the result queried from ChEBI.
            identifier_name = self.chemical_information['name']['data']
            self.add_description_from_pubchem(identifier, identifier_name)

        return True

    def check_chebi_for_identifier(self, identifier, identifier_name):
        # Return True if data is successfully found.
        # Return False if there are any issues.

        chebi = ExternalLookup.lookup_chebi(identifier, synonyms=True)
        if not chebi:
            self.critical_error(self.process_data['CH3a']['data'], chebi.error)
            return False

        if not chebi.inchikey:
            self.warning_error(self.process_data['CH3a']['data'],
                               'No InChIKey found for entry: {}'
                               .format(identifier))

        # Check whether the name intended to be used in FlyBase matches
        # the name returned from the database.
        if self.has_data('CH1a'):
            if chebi.name.lower() != self.process_data['CH1a']['data'][FIELD_VALUE].lower():
                self.warning_error(self.process_data['CH1a']['data'],
                                   'ChEBI name does not match name specified for FlyBase: {} -> {}'
                                   .format(chebi.name,
                                           self.process_data['CH1a']['data'][FIELD_VALUE]))
            else:
                log.debug('Queried name \'{}\' matches name used in proforma \'{}\''.format(chebi.name, self.process_data['CH1a']['data'][FIELD_VALUE]))

        # Check whether the identifier_name supplied by the curator matches
        # the name returned from the database.
        if identifier_name:
            if chebi.name.lower() != identifier_name.lower():
                self.critical_error(self.process_data['CH3a']['data'],
                                    'ChEBI name does not match name specified in identifier field: {} -> {}'
                                    .format(chebi.name,
                                            identifier_name))
                return False

        self.chemical_information['identifier']['data'] = identifier
        self.chemical_information['identifier']['source'] = 'CHEBI'
        self.chemical_information['name']['data'] = chebi.name
        self.chemical_information['name']['source'] = 'CHEBI'
        self.chemical_information['inchikey']['data'] = chebi.inchikey
        self.chemical_information['inchikey']['source'] = 'CHEBI'
        self.chemical_information['synonyms']['data'] = chebi.synonyms
        self.chemical_information['synonyms']['source'] = 'CHEBI'

        return True

    def add_description_from_pubchem(self, identifier, identifier_name):
        if not self.chemical_information['description']['data']:
            pubchem = ExternalLookup.lookup_by_name('pubchem', identifier_name)
            if pubchem.error:
                log.error(pubchem.error)
                return False
            else:
                self.chemical_information['description']['data'] = pubchem.description

    def check_pubchem_for_identifier(self, identifier, identifier_name):

        # Get data from pubchem.
        # NOTE: Pub chem has a rediculous number of synonyms BUt they are ranked
        #       so just take the top 10.
        pubchem = ExternalLookup.lookup_by_name('pubchem', identifier_name, synonyms=True)
        if pubchem.error:
            log.error(pubchem.error)
            return False

        if self.has_data('CH1a'):
            if pubchem.name.lower() != self.process_data['CH1a']['data'][FIELD_VALUE].lower():
                self.warning_error(self.process_data['CH1a']['data'],
                                   'PubChem name does not match name specified for FlyBase: {} -> {}'
                                   .format(pubchem.name,
                                           self.process_data['CH1a']['data'][FIELD_VALUE]))
            else:
                log.debug('Queried name \'{}\' matches name used in proforma \'{}\''.format(pubchem.name, self.process_data['CH1a']['data'][FIELD_VALUE]))

        self.chemical_information['identifier']['data'] = identifier
        self.chemical_information['identifier']['source'] = 'PubChem'
        self.chemical_information['name']['data'] = pubchem.name
        self.chemical_information['name']['source'] = 'PubChem'
        self.chemical_information['inchikey']['data'] = pubchem.inchikey
        self.chemical_information['inchikey']['source'] = 'PubChem'
        self.chemical_information['description']['data'] = pubchem.description
        self.chemical_information['description']['source'] = 'PubChem'
        self.chemical_information['synonyms']['data'] = pubchem.synonyms[0:10]  # Top 10 will do.
        self.chemical_information['synonyms']['source'] = 'PubChem'

        return True

    def check_valid_id(self, identifier):
        # Added regex checks for identifiers here.
        pass

    def split_identifier_and_name(self, identifier_unprocessed):
        # Strip away the name if one is supplied with the identifier.
        identifier = None
        identifier_name = None
        if ';' in identifier_unprocessed:
            log.debug('Semicolon found, splitting identifier: {}'.format(identifier_unprocessed))
            identifier_split_list = identifier_unprocessed.split('; ')
            identifier = identifier_split_list.pop(0).strip()
            identifier_name = identifier_split_list.pop(0).strip()
            if identifier_split_list:  # If the list is not empty by this point, raise an error.
                self.critical_error(self.process_data['CH3a']['data'],
                                    "Error splitting identifier and name using semicolon. {}".format(identifier_unprocessed))
                identifier_name = None  # Set name to None before returning. It might be wrong otherwise.
                return identifier, identifier_name
        else:
            identifier = identifier_unprocessed.strip()

        return identifier, identifier_name
