"""

:synopsis: The "chem" ChadoObject.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>,
               Ian Longden <ianlongden@morgan.harvard.edu>
"""

from harvdev_utils.production import (
    Pub, Db, Dbxref,
    Feature, Featureprop, FeaturePub,
    FeatureDbxref, FeatureSynonym, Synonym
)
from chado_object.feature.chado_feature import ChadoFeatureObject, FIELD_VALUE
from harvdev_utils.chado_functions import (
    get_or_create, DataError, ExternalLookup,
    feature_synonym_lookup, feature_name_lookup,
    get_default_organism_id
)
from harvdev_utils.char_conversions import (
    sub_sup_to_sgml, sgml_to_unicode, sgml_to_plain_text
)

from datetime import datetime
import os
import logging

log = logging.getLogger(__name__)


class ChadoChem(ChadoFeatureObject):
    """Process the Chemical Proforma."""

    def __init__(self, params):
        """Initialise the chado object."""
        # Initiate the parent.
        super(ChadoChem, self).__init__(params)
        log.debug('Initializing ChadoChem object.')

        self.proforma_start_line_number = params.get('proforma_start_line_number')
        self.reference = params.get('reference')

        ###########################################################
        # Values queried later, placed here for reference purposes.
        ############################################################
        self.pub = None             # All other proforma need a reference to a pub
        self.feature = None        # The chemical object, to get feature_id use self.chemical.feature_id.
        self.chebi_pub_id = None    # Used for attributing chemical curation.
        self.pubchem_pub_id = None  # Used for attributing chemical curation.

        # yaml file defines what to do with each field. Follow the light
        self.type_dict = {'featureprop': self.load_featureprop,
                          'synonym': self.load_synonym_chem,
                          'ignore': self.ignore,
                          'value': self.ignore,
                          'disspub': self.dissociate_from_pub}

        self.delete_dict = {'ignore': self.ignore,
                            'synonym': self.rename_synonym,
                            'featureprop': self.delete_featureprop,
                            'value': self.change_featurepropvalue}
        # Chemical storage dictionary.
        # This dictionary contains all the information required to create a new FBch.

        self.chemical_information = {
            'identifier': None,
            'accession': None,
            'source': None,
            'name': None,
            'description': None,
            'inchikey': None,
            'synonyms': None,
            'DBObject': None,
            'PubID': None
        }
        # if above is for chebi, then store equivalent pubchem data here
        # if it can be found. And vice versa.
        self.alt_chemical_information = {
            'identifier': None,
            'accession': None,
            'source': None,
            'name': None,
            'description': None,
            'inchikey': None,
            'synonyms': None,
            'DBObject': None,
            'PubID': None
        }
        self.feature = None
        self.type_name = 'chemical entity'

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
        if not self.feature:
            log.info("CHEM/FEAT NO FEATURE???")
            return

        # Dissociate pub ONLY
        if self.has_data('Ch1c'):
            self.dissociate_from_pub(self, 'CH1c')
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
        return self.feature

    def fetch_by_FBch_and_check(self, chemical_cvterm_id):
        """Fetch by the FBch (CH1f) and check the name is the same if it is given (CH1a).

        Args:
            chemical_cvterm_id (int): cvterm_id to be used as type in getting feature.

        Raises:
            critical error if CH1f and CH1a are specified and do not match.
        """
        self.feature, is_new = get_or_create(self.session, Feature, type_id=chemical_cvterm_id,
                                             uniquename=self.process_data['CH1f']['data'][FIELD_VALUE])
        if is_new:
            message = "Could not find {} in the database. Please check it exists.".format(self.process_data['CH1f']['data'][FIELD_VALUE])
            self.critical_error(self.process_data['CH1f']['data'], message)
        if self.has_data('CH1a'):
            if self.process_data['CH1a']['data'][FIELD_VALUE] != self.feature.name:
                message = "Name given does not match that in database. {} does not equal {}".\
                    format(self.process_data['CH1f']['data'][FIELD_VALUE],
                           self.feature.name)
                self.critical_error(self.process_data['CH1a']['data'], message)

    def get_external_chemical_pub_id(self):
        """Get pub id for Chemical."""
        return self.chemical_information['PubID']

    def alt_comparison(self):  # noqa
        """Compare with Alternative Chemical ID."""
        if not self.has_data('CH3d'):
            return

        alt_identifier_found = self.validate_fetch_identifier_at_external_db('CH3d', self.alt_chemical_information)
        if not alt_identifier_found:
            message = "Unable to find alternative chemical db entry."
            self.warning_error(self.process_data['CH3d']['data'], message)
            return

        # If they both have equal inchikeys and it is not None they match.
        if self.chemical_information['inchikey'] == self.alt_chemical_information['inchikey']:
            # Same and not None
            if self.chemical_information['inchikey']:
                self.add_alt_synonym()
                return
        # different and both are not None
        elif self.chemical_information['inchikey'] and self.alt_chemical_information['inchikey']:
            message = "Inchikeys do not match\n{}->{} and\n{}->{}".format(
                self.chemical_information['identifier'],
                self.chemical_information['inchikey'],
                self.alt_chemical_information['identifier'],
                self.alt_chemical_information['inchikey']
            )
            self.warning_error(self.process_data['CH3d']['data'], message)
            return

        # So at least one does not have an inchikey so lets try names.
        if self.chemical_information['name'].upper() == self.alt_chemical_information['name'].upper():
            return

        found = False
        for name in self.chemical_information['synonyms']:
            for alt_name in self.alt_chemical_information['synonyms']:
                if name.upper() == alt_name.upper():
                    found = True
                    break
        if not found:
            # Not found so give a warning
            message = "No synonyms match for CH3d and CH3a!!!\n"
            message += "{} synonyms are: {}\n".format(self.chemical_information['identifier'], self.chemical_information['synonyms'])
            message += "{} synonyms are: {}\n".format(self.alt_chemical_information['identifier'], self.alt_chemical_information['synonyms'])
            self.warning_error(self.process_data['CH3a']['data'], message)

    def add_alternative_info(self):
        """Add data from alternative chemical DB.

        Add feature pub to alt pub? Done
        Add feature dbxref ? Done
        Add feature Synonym ? Done
        """
        if not self.has_data('CH3d') or not self.alt_chemical_information['PubID']:
            return
        # Add pub link to Chebi or pubchem depending on type
        feature_pub, _ = get_or_create(
            self.session, FeaturePub,
            feature_id=self.feature.feature_id,
            pub_id=self.alt_chemical_information['PubID'])
        log.debug("Created new feature_pub for alt chem db: {}".format(feature_pub.feature_pub_id))

        self.add_dbxref(self.alt_chemical_information)

        # Add synonym including Pubchem/CHEBI bit
        self.alt_chemical_information['synonyms'].append(self.alt_chemical_information['identifier'])
        self.process_synonyms_from_external_db(self.alt_chemical_information, alt=True)

    def add_dbxref(self, chemical):
        """Add dbxref."""
        dbxref, _ = get_or_create(self.session, Dbxref,
                                  db_id=chemical['DBObject'].db_id,
                                  accession=chemical['accession'])

        log.debug("Updating FBch with dbxref.dbxref_id: {}".format(dbxref.dbxref_id))
        f_dbx, _ = get_or_create(self.session, FeatureDbxref,
                                 feature_id=self.feature.feature_id,
                                 dbxref_id=dbxref.dbxref_id)

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
            if not self.has_data('CH1c'):
                feature_pub, _ = get_or_create(self.session, FeaturePub,
                                               feature_id=self.feature.feature_id,
                                               pub_id=self.pub.pub_id)
            return

        # So we have a new chemical, lets get the data for this.
        try:
            identifier_found = self.validate_fetch_identifier_at_external_db('CH3a', self.chemical_information)
        except Exception as e:
            message = "Lookup failed and generated the error {}.".format(e)
            self.critical_error(self.process_data['CH3a']['data'], message)
            return

        if not identifier_found:
            return

        self.alt_comparison()

        exists_already = self.check_existing_already()
        if exists_already:
            self.feature = exists_already
            if self.has_data('CH1c'):
                pass
            else:
                feature_pub, _ = get_or_create(self.session, FeaturePub, feature_id=self.feature.feature_id,
                                               pub_id=self.pub.pub_id)
            return

        # Check if we already have an existing entry by feature name -> dbx xref.
        # FBch features -> dbxrefs are UNIQUE for EACH external database.
        # e.g. There should never be more than one connection from FBch -> ChEBI.
        # If so, someone has already made an FBch which corresponds to the that CheBI.
        self.check_existing_dbxref(self.chemical_information)

        # Look up organism id.
        organism_id = get_default_organism_id(self.session)

        if self.has_data('CH1a'):
            name = sgml_to_plain_text(self.process_data['CH1a']['data'][FIELD_VALUE])
        else:
            name = self.chemical_information['name']

        self.feature, _ = get_or_create(self.session, Feature, organism_id=organism_id,
                                        name=name,
                                        type_id=chemical_cvterm_id,
                                        uniquename='FBch:temp_0')

        log.debug("New chemical entry created: {}".format(self.feature.name))

        self.add_dbxref(self.chemical_information)

        # Add pub link to Chebi or pubchem amd current pub
        feature_pub, _ = get_or_create(self.session, FeaturePub,
                                       feature_id=self.feature.feature_id,
                                       pub_id=self.chemical_information['PubID'])
        log.debug("Created new feature_pub: {}".format(feature_pub.feature_pub_id))
        feature_pub, _ = get_or_create(self.session, FeaturePub,
                                       feature_id=self.feature.feature_id,
                                       pub_id=self.pub.pub_id)

        self.add_alternative_info()

        # Add the identifier as a synonym and other synonyms
        self.process_synonyms_from_external_db(self.chemical_information)

        # Add the description as a featureprop.
        self.add_description_to_featureprop()

        # Add the inchikey as a featureprop.
        self.add_inchikey_to_featureprop()

    def check_existing_already(self):
        """Check if we already have an existing entry.

        This needs a little explaining.
        We check the name and all the synonyms.
        This is becouse ChEBI and PubChem could be the same and we do not want
        duplicate entries. Does not matter if it is stored via ChEBI or PubChem
        but we only really want a chemical in the database once.

        This also sets self.new_chemical_entry to Flase if found even if the curator
        has set it to new in the proforma, Curators requested no consequences of loading
        a chemical more than once, apart from it not being duplicated again.
        """
        #
        # Look up organism id.
        #
        organism_id = get_default_organism_id(self.session)

        #
        # check name from lookup
        #
        entry_already_exists = None
        entry_already_exists = self.chemical_feature_lookup(organism_id, 'CH3a', self.chemical_information['name'], current=True)
        if entry_already_exists:
            self.new_chemical_entry = False
            log.debug('An entry already exists in the database with this name: {}'.format(entry_already_exists.name))
            return entry_already_exists

        #
        # check Flybase name if given
        #
        if self.has_data('CH1a'):
            entry_already_exists = self.chemical_feature_lookup(organism_id, 'CH1a', self.process_data['CH1a']['data'][FIELD_VALUE], current=True)

        # If we already have an entry and we already know it is new then we have a problem.
        if entry_already_exists:
            self.new_chemical_entry = False
            log.debug('An entry already exists in the database with this name: {}'.format(entry_already_exists.name))
            return entry_already_exists

        #
        # Check for any symbol synonym can be not current and if found Just give a warning
        #
        entry_already_exists = self.chemical_feature_lookup(organism_id, 'CH3a', self.chemical_information['name'], current=False)
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
        """Delete the featureprop."""
        prop_cv_id = self.cvterm_query(self.process_data[key]['cv'], self.process_data[key]['cvterm'])

        fp, is_new = get_or_create(self.session, Featureprop, feature_id=self.feature.feature_id,
                                   type_id=prop_cv_id)
        if is_new:
            message = "No current {} field specified in chado so cannot bangc it".format(key)
            self.critical_error(self.process_data[key]['data'], message)
        else:
            self.session.delete(fp)
        self.process_data[key]['data'] = None

    def change_featurepropvalue(self, key, bangc=True):
        """Change the featureporp value."""
        prop_cv_id = self.cvterm_query(self.process_data['CH3b']['cv'], self.process_data['CH3b']['cvterm'])

        fp, is_new = get_or_create(self.session, Featureprop, feature_id=self.feature.feature_id,
                                   type_id=prop_cv_id)
        if is_new:
            message = "No current value specified in chado so cannot bangc it"
            self.critical_error(self.process_data[key]['data'], message)
        else:
            fp.value = self.process_data[key]['data'][FIELD_VALUE]
        self.process_data[key]['data'] = None
        self.process_data['CH3b']['data'] = None

    def rename_synonym(self, key, bangc=True):
        """Rename the synonym."""
        if not self.has_data(key):
            message = "Bangc MUST have a value."
            self.critical_error(self.process_data[key]['data'], message)
            return
        self.load_synonym_chem(key)
        self.process_data[key]['data'] = None

    def load_synonym_chem(self, key):
        """Load the synonym.

        Chemicals can be listed more than once
        But are only loaded once. We do not allow synoym changes
        for these repeated chemicals. !c Should be used in this case
        """
        if not self.new_chemical_entry and key not in self.bang_c:
            return
        self.load_synonym(key, unattrib=False)

    def add_description_to_featureprop(self):
        """Associate the description from PubChem to a feature via featureprop."""
        log.debug('Adding PubChem description to featureprop.')

        description_cvterm_id = self.cvterm_query('property type', 'description')

        get_or_create(self.session, Featureprop, feature_id=self.feature.feature_id,
                      type_id=description_cvterm_id, value=self.chemical_information['description'])

    def add_inchikey_to_featureprop(self):
        """Associates the inchikey from PubChem to a feature via featureprop.

        :return:
        """
        if not self.chemical_information['inchikey']:
            return

        log.debug('Adding PubChem description to featureprop.')

        description_cvterm_id = self.cvterm_query('property type', 'inchikey')

        get_or_create(self.session, Featureprop, feature_id=self.feature.feature_id,
                      type_id=description_cvterm_id, value=self.chemical_information['inchikey'])

    def process_synonyms_from_external_db(self, chemical, alt=False):
        """
        Add the synonyms obtained from the external db for the chemical.

        :return:
        """
        symbol_cv_id = self.cvterm_query('synonym type', 'symbol')

        pub_id = chemical['PubID']

        seen_it = set()
        if chemical['synonyms']:
            log.debug("Adding non current synonyms {}".format(chemical['synonyms']))
            for item in chemical['synonyms']:
                for lowercase in [True, False]:
                    name = item[:255]  # Max 255 chars
                    if lowercase:
                        name = name.lower()
                    sgml = sgml_to_unicode(name)[:255]  # MAx 255 chars
                    if name in seen_it:
                        log.debug("Ignoring {} as already seen".format(name))
                        continue
                    log.debug("Adding synonym {}".format(name))

                    new_synonym, _ = get_or_create(self.session, Synonym, type_id=symbol_cv_id,
                                                   synonym_sgml=sgml,
                                                   name=name)
                    seen_it.add(name)
                    fs, _ = get_or_create(self.session, FeatureSynonym, feature_id=self.feature.feature_id,
                                          pub_id=pub_id, synonym_id=new_synonym.synonym_id)
                    fs.is_current = False

        log.debug("Adding new synonym entry for {}.".format(chemical['identifier']))

        if alt:  # If alternative then already done.
            return
        if self.has_data('CH1a'):
            name = sgml_to_plain_text(self.process_data['CH1a']['data'][FIELD_VALUE])
            sgml = sgml_to_unicode(sub_sup_to_sgml(self.process_data['CH1a']['data'][FIELD_VALUE]))
        else:
            name = chemical['name'][:255]  # removes .lower()
            sgml = sgml_to_unicode(sub_sup_to_sgml(name))

        new_synonym, _ = get_or_create(self.session, Synonym, type_id=symbol_cv_id,
                                       synonym_sgml=sgml,
                                       name=name)

        fs, _ = get_or_create(self.session, FeatureSynonym, feature_id=self.feature.feature_id,
                              pub_id=pub_id, synonym_id=new_synonym.synonym_id)
        fs.is_current = True

    def check_existing_dbxref(self, chemical):
        """Check for existing dbxref."""
        log.debug('Querying for existing accession ({}) via feature -> dbx -> db.'.format(chemical['accession']))

        feature_dbxref_chemical_chebi_result = self.session.query(Feature, Dbxref).\
            join(Feature, (Feature.dbxref_id == Dbxref.dbxref_id)).\
            filter(Dbxref.accession == chemical['accession'],
                   Dbxref.db_id == chemical['DBObject'].db_id).one_or_none()

        # feature_dbxref_chemical_chebi_result[0] accesses the 'Feature' object from the result.
        if feature_dbxref_chemical_chebi_result:
            self.critical_error(self.process_data['CH3a']['data'],
                                'A feature -> {} association already exists for this ID. Check: {}'
                                .format(chemical['source'], feature_dbxref_chemical_chebi_result[0].uniquename))

    def chemical_feature_lookup(self, organism_id, key_name, name, current=True):
        """Lookup the chemical feature."""
        log.debug("chemical feature lookup for {} and current = {}".format(name, current))
        entry = None
        name = sgml_to_plain_text(name)
        if current:
            entry = feature_name_lookup(self.session, name,
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
                log.debug(message)
                return features[0]
        return entry

    def look_up_static_references(self):
        """Lookup pub id for chebi and pubchem."""
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

    def validate_fetch_identifier_at_external_db(self, process_key, chemical):
        """Fetch and validate externaldb.

        process_key: Key to use to get data , should be CH3a or CH3d
        chemical: Chemical entity to store in should be either self.chemical_information
                  or self.alt_chemical_information

        Identifiers and names for ChEBI / PubChem entries are processed at their respective db.
        However, InChIKey entries and definitions always come from PubChem.
        This is because PubChem cites ChEBI (as well as other external definitions) whereas
        ChEBI does not provide this service.
        """
        identifier_unprocessed = self.process_data[process_key]['data'][FIELD_VALUE]
        identifier_unprocessed = sgml_to_unicode(sub_sup_to_sgml(identifier_unprocessed))
        chemical['identifier'], chemical['name'] = self.split_identifier_and_name(identifier_unprocessed, process_key)
        if not chemical['name'] or not chemical['name'].strip():
            message = "Wrong format should be 'DBNAME:number ; text'"
            self.critical_error(self.process_data[process_key]['data'], message)
            return False
        log.debug('Found identifier: {} and identifier_name: {}'.format(chemical['identifier'], chemical['name']))

        chemical['source'], chemical['accession'] = chemical['identifier'].split(':')

        log.debug("DB is '{}'".format(chemical['source']))
        database_dispatch_dictionary = {
            'CHEBI': self.check_chebi_for_identifier,
            'PubChem': self.check_pubchem_for_identifier,
            'PubChem_SID': self.check_pubchem_for_identifier
        }

        # Obtain our identifier, name, definition, and InChIKey from ChEBI / PubChem.
        try:
            identifier_and_data = database_dispatch_dictionary[chemical['source']](chemical, process_key)
            log.debug("identifier_and_data is {}".format(identifier_and_data))
        except KeyError as e:
            self.critical_error(self.process_data[process_key]['data'],
                                'Database name not recognized from identifier: {}. {}'.format(chemical['source'], e))
            return False
        if identifier_and_data is False:  # Errors are already declared in the sub-functions.
            return False

        # If we're at this stage, we have all our data for PubChem BUT
        # for a ChEBI query we need to go to PubChem for the definition.
        if chemical['source'] != 'PubChem':
            # Set the identifier name to the result queried from ChEBI.
            self.add_description_from_pubchem(chemical)
        elif chemical['source'] == 'PubChem_SID':
            chemical['source'] == 'PubChem'
        return True

    def check_chebi_for_identifier(self, chemical, process_key):
        """Check for chebi identifier.

        Returns: True if data is successfully found.
                 False if there are any issues.
        """
        chebi = ExternalLookup.lookup_chebi(chemical['identifier'], synonyms=True)
        if not chebi:
            self.critical_error(self.process_data[process_key]['data'], chebi.error)
            return False

        if not chebi.inchikey:
            log.debug('No InChIKey found for entry: {}'.format(chemical['identifier']))

        # Check whether the name intended to be used in FlyBase matches
        # the name returned from the database.
        if self.has_data('CH1a'):
            plain_text = sgml_to_plain_text(self.process_data['CH1a']['data'][FIELD_VALUE])
            if chebi.name.lower() != plain_text.lower():
                log.debug('ChEBI name does not match name specified for FlyBase: {} -> {}'.format(chebi.name, plain_text))
            else:
                log.debug('Queried name \'{}\' matches name used in proforma \'{}\''.format(chebi.name, self.process_data['CH1a']['data'][FIELD_VALUE]))

        # Check whether the identifier_name supplied by the curator matches
        # the name returned from the database.
        if chemical['name']:
            plain_text = sgml_to_plain_text(chemical['name'])
            if chebi.name.lower() != plain_text.lower():
                message = 'ChEBI name does not match name specified in identifier field: {} -> {}'.\
                    format(chebi.name, chemical['name'])
                log.debug(message)

        chemical['name'] = chebi.name
        chemical['inchikey'] = chebi.inchikey
        chemical['synonyms'] = chebi.synonyms
        chemical['PubID'] = self.chebi_pub_id
        chemical['DBObject'] = self.session.query(Db). \
            filter(Db.name == chemical['source']).one()

        return True

    def add_alt_synonym(self):
        """Add synonym of the alternative chemical id.

        Add feature_dbxref ???
        """
        pass

    def add_description_from_pubchem(self, chemical):
        """Add description from pubchem."""
        if not chemical['description']:
            pubchem = ExternalLookup.lookup_by_name('pubchem', chemical['name'])
            if pubchem.error:
                log.error(pubchem.error)
                return False
            else:
                chemical['description'] = pubchem.description

    def check_pubchem_for_identifier(self, chemical, process_key):
        """Check identifier is in pubchem.

        Get data from pubchem.
        NOTE: Pub chem has a rediculous number of synonyms BUT they are ranked
              so just take the top 10.
        """
        pubchem = ExternalLookup.lookup_by_id(chemical['source'].lower(), chemical['accession'], synonyms=True)

        if pubchem.error:
            log.error(pubchem.error)
            message = "Error looking up {} for {}. Error is {}".\
                format(chemical['source'], chemical['accession'], pubchem.error)
            self.critical_error(self.process_data[process_key]['data'], message)
            return False

        if self.has_data('CH1a'):
            plain_text = sgml_to_plain_text(self.process_data['CH1a']['data'][FIELD_VALUE])
            pubchem.name = str(pubchem.name)
            if pubchem.name.lower() != plain_text.lower():
                log.debug('PubChem name does not match name specified for FlyBase: {} -> {}'.format(pubchem.name, plain_text))
            else:
                log.debug('Queried name \'{}\' matches name used in proforma \'{}\''.format(pubchem.name, plain_text))

        # Check whether the identifier_name supplied by the curator matches
        # the name returned from the database.
        if chemical['name']:
            plain_text = sgml_to_plain_text(self.process_data['CH1a']['data'][FIELD_VALUE])
            if pubchem.name.lower() != plain_text.lower():
                message = 'PubChem name does not match name specified in identifier field: {} -> {}'.\
                    format(pubchem.name, chemical['name'])
                log.debug(message)
        if chemical['source'] == 'PubChem_SID':
            chemical['source'] = 'PubChem'
        chemical['name'] = pubchem.name
        chemical['inchikey'] = pubchem.inchikey
        chemical['description'] = pubchem.description
        chemical['synonyms'] = pubchem.synonyms[0:10]  # Top 10 will do.
        chemical['PubID'] = self.pubchem_pub_id
        chemical['DBObject'] = self.session.query(Db). \
            filter(Db.name == chemical['source']).one()

        return True

    def split_identifier_and_name(self, identifier_unprocessed, process_key):
        """Strip away the name if one is supplied with the identifier."""
        identifier = None
        identifier_name = None
        if ';' in identifier_unprocessed:
            log.debug('Semicolon found, splitting identifier: {}'.format(identifier_unprocessed))
            identifier_split_list = identifier_unprocessed.split(';')
            try:
                identifier = identifier_split_list.pop(0).strip()
                identifier_name = identifier_split_list.pop(0).strip()
            except IndexError:
                self.critical_error(self.process_data[process_key]['data'],
                                    "Error splitting identifier and name using semicolon. {}".format(identifier_unprocessed))
            if identifier_split_list:  # If the list is not empty by this point, raise an error.
                self.critical_error(self.process_data[process_key]['data'],
                                    "Error splitting identifier and name using semicolon. {}".format(identifier_unprocessed))
                identifier_name = None  # Set name to None before returning. It might be wrong otherwise.
                return identifier, identifier_name
        else:
            identifier = identifier_unprocessed.strip()

        return identifier, identifier_name
