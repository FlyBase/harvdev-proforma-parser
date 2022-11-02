"""

:synopsis:  lookup chemical in pubchem or chebi.

:moduleauthor: Ian Longden <ilongden@morgan.harvard.edu>,

"""
from harvdev_utils.production import (
    FeatureDbxref,
    FeaturePub,
    Featureprop,
    FeatureSynonym,
    Db,
    Dbxref,
    Pub,
    Synonym
)
from harvdev_utils.chado_functions import (
    get_or_create,
    ExternalLookup,
    synonym_name_details
)
from harvdev_utils.char_conversions import (
    sgml_to_unicode, sgml_to_plain_text
)
from chado_object.feature.chado_feature import FIELD_VALUE


def process_chemical(self, key):
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
    self.add_alt_synonym()
    self.add_dbxref(self.chemical_information)

    # Add pub link to Chebi or pubchem amd current pub
    feature_pub, _ = get_or_create(self.session, FeaturePub,
                                   feature_id=self.feature.feature_id,
                                   pub_id=self.chemical_information['PubID'])
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

    """
    if not self.has_data('CH3d') or not self.alt_chemical_information['PubID']:
        return
    # Add pub link to Chebi or pubchem depending on type
    feature_pub, _ = get_or_create(
        self.session, FeaturePub,
        feature_id=self.feature.feature_id,
        pub_id=self.alt_chemical_information['PubID'])

    self.add_dbxref(self.alt_chemical_information)

    # Add synonym including Pubchem/CHEBI bit
    self.alt_chemical_information['synonyms'].append(self.alt_chemical_information['identifier'])
    self.process_synonyms_from_external_db(self.alt_chemical_information, alt=True)


def add_dbxref(self, chemical):
    """Add dbxref."""
    dbxref, _ = get_or_create(self.session, Dbxref,
                              db_id=chemical['DBObject'].db_id,
                              accession=chemical['accession'])

    # set the definition to the name
    if 'name' in chemical and chemical['name']:
        dbxref.description = chemical['name']
    self.log.debug("Updating FBch with dbxref.dbxref_id: {}".format(dbxref.dbxref_id))
    f_dbx, _ = get_or_create(self.session, FeatureDbxref,
                             feature_id=self.feature.feature_id,
                             dbxref_id=dbxref.dbxref_id)


def look_up_static_references(self):
    """Lookup pub id for chebi and pubchem."""
    self.log.debug('Retrieving ChEBI / PubChem FBrfs for association.')

    chebi_publication_title = 'ChEBI: Chemical Entities of Biological Interest, EBI.'
    pubchem_publication_title = 'PubChem, NIH.'

    chebi_ref_pub_id_query = self.session.query(Pub). \
        filter(Pub.title == chebi_publication_title).one()

    pubchem_ref_pub_id_query = self.session.query(Pub). \
        filter(Pub.title == pubchem_publication_title).one()

    self.chebi_pub_id = chebi_ref_pub_id_query.pub_id
    self.pubchem_pub_id = pubchem_ref_pub_id_query.pub_id
    self.log.debug('Returned ChEBI FBrf pub id as {}'.format(self.chebi_pub_id))
    self.log.debug('Returned PubChem FBrf pub id as {}'.format(self.pubchem_pub_id))


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
    identifier_unprocessed = sgml_to_unicode(identifier_unprocessed)
    chemical['identifier'], chemical['name'] = self.split_identifier_and_name(identifier_unprocessed, process_key)
    if not chemical['name'] or not chemical['name'].strip():
        message = "Wrong format should be 'DBNAME:number ; text'"
        self.critical_error(self.process_data[process_key]['data'], message)
        return False
    self.log.debug('Found identifier: {} and identifier_name: {}'.format(chemical['identifier'], chemical['name']))

    chemical['source'], chemical['accession'] = chemical['identifier'].split(':')

    database_dispatch_dictionary = {
        'CHEBI': self.check_chebi_for_identifier,
        'PubChem': self.check_pubchem_for_identifier,
        'PubChem_SID': self.check_pubchem_for_identifier
    }

    # Obtain our identifier, name, definition, and InChIKey from ChEBI / PubChem.
    try:
        identifier_and_data = database_dispatch_dictionary[chemical['source']](chemical, process_key)
        self.log.debug("identifier_and_data is {}".format(identifier_and_data))
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
        chemical['source'] = 'PubChem'
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
        self.log.debug('No InChIKey found for entry: {}'.format(chemical['identifier']))

    # Check whether the name intended to be used in FlyBase matches
    # the name returned from the database.
    if self.has_data('CH1a'):
        plain_text = sgml_to_plain_text(self.process_data['CH1a']['data'][FIELD_VALUE])
        if chebi.name.lower() != plain_text.lower():
            self.log.debug('ChEBI name does not match name specified for FlyBase: {} -> {}'.format(chebi.name, plain_text))
        else:
            self.log.debug('Queried name \'{}\' matches name used in proforma \'{}\''.format(chebi.name, self.process_data['CH1a']['data'][FIELD_VALUE]))

    # Check whether the identifier_name supplied by the curator matches
    # the name returned from the database.
    if chemical['name']:
        plain_text = sgml_to_plain_text(chemical['name'])
        self.log.error(f"BEFORE {chemical['name']} AFTER {plain_text}")
        if chebi.name.lower() != plain_text.lower():
            message = 'ChEBI name does not match name specified in identifier field: {} -> {}'.\
                format(chebi.name, chemical['name'])
            self.log.debug(message)

    chemical['name'] = chebi.name
    chemical['inchikey'] = chebi.inchikey
    chemical['description'] = chebi.description
    chemical['synonyms'] = chebi.synonyms
    chemical['PubID'] = self.chebi_pub_id
    chemical['DBObject'] = self.session.query(Db). \
        filter(Db.name == chemical['source']).one()
    return True


def add_alt_synonym(self):
    """Add synonym of the alternative chemical id.

    Use the current feature/name and the paper it belongs to
    either pubchem or chebi.
    """
    if self.new_chemical_entry:
        organism, plain_name, sgml = synonym_name_details(self.session, self.process_data['CH1a']['data'][FIELD_VALUE])
        cvterm = self.cvterm_query('synonym type', 'fullname')
        pub_id = self.chemical_information['PubID']

        new_synonym, _ = get_or_create(self.session, Synonym, type_id=cvterm,
                                       synonym_sgml=plain_name,
                                       name=plain_name)
        fs, _ = get_or_create(self.session, FeatureSynonym, feature_id=self.feature.feature_id,
                              pub_id=pub_id, synonym_id=new_synonym.synonym_id)


def add_description_from_pubchem(self, chemical):
    """Add description from pubchem."""
    if not chemical['description']:
        pubchem = ExternalLookup.lookup_by_name('pubchem', chemical['name'])
        if pubchem.error:
            self.log.error(pubchem.error)
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
        self.log.error(pubchem.error)
        message = "Error looking up {} for {}. Error is {}".\
            format(chemical['source'], chemical['accession'], pubchem.error)
        self.critical_error(self.process_data[process_key]['data'], message)
        return False

    if self.has_data('CH1a'):
        plain_text = sgml_to_plain_text(self.process_data['CH1a']['data'][FIELD_VALUE])
        pubchem.name = str(pubchem.name)
        if pubchem.name.lower() != plain_text.lower():
            self.log.debug('PubChem name does not match name specified for FlyBase: {} -> {}'.format(pubchem.name, plain_text))
        else:
            self.log.debug('Queried name \'{}\' matches name used in proforma \'{}\''.format(pubchem.name, plain_text))

    # Check whether the identifier_name supplied by the curator matches
    # the name returned from the database.
    if chemical['name']:
        plain_text = sgml_to_plain_text(self.process_data['CH1a']['data'][FIELD_VALUE])
        if pubchem.name.lower() != plain_text.lower():
            message = 'PubChem name does not match name specified in identifier field: {} -> {}'.\
                format(pubchem.name, chemical['name'])
            self.log.debug(message)
    if chemical['source'] == 'PubChem_SID':
        chemical['source'] = 'PubChem'
    chemical['name'] = pubchem.name
    chemical['inchikey'] = pubchem.inchikey
    if not chemical['description']:
        chemical['description'] = pubchem.description
    chemical['synonyms'] = pubchem.synonyms[0:10]  # Top 10 will do.
    chemical['PubID'] = self.pubchem_pub_id
    chemical['DBObject'] = self.session.query(Db). \
        filter(Db.name == chemical['source']).one()

    return True


def add_inchikey_to_featureprop(self):
    """Associates the inchikey from PubChem to a feature via featureprop.

    :return:
    """
    if not self.chemical_information['inchikey']:
        return

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
        for item in chemical['synonyms']:
            for lowercase in [True, False]:
                name = item[:255]  # Max 255 chars
                if lowercase:
                    name = name.lower()
                sgml = sgml_to_unicode(name)[:255]  # MAx 255 chars
                if name in seen_it:
                    continue
                self.log.debug("Adding synonym {}".format(name))

                new_synonym, _ = get_or_create(self.session, Synonym, type_id=symbol_cv_id,
                                               synonym_sgml=sgml,
                                               name=name)
                seen_it.add(name)
                fs, _ = get_or_create(self.session, FeatureSynonym, feature_id=self.feature.feature_id,
                                      pub_id=pub_id, synonym_id=new_synonym.synonym_id)
                fs.is_current = False

    self.log.debug("Adding new synonym entry for {}.".format(chemical['identifier']))

    if alt:  # If alternative then already done.
        return
    if self.has_data('CH1a'):
        name = sgml_to_plain_text(self.process_data['CH1a']['data'][FIELD_VALUE])
        sgml = sgml_to_unicode(self.process_data['CH1a']['data'][FIELD_VALUE])
        name = sgml
    else:
        name = chemical['name'][:255]  # removes .lower()
        sgml = sgml_to_unicode(name)
        name = sgml

    new_synonym, _ = get_or_create(self.session, Synonym, type_id=symbol_cv_id,
                                   synonym_sgml=sgml,
                                   name=name)

    fs, _ = get_or_create(self.session, FeatureSynonym, feature_id=self.feature.feature_id,
                          pub_id=pub_id, synonym_id=new_synonym.synonym_id)
    fs.is_current = True
