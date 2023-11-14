"""

:synopsis:  lookup chemical in pubchem or chebi.

:moduleauthor: Ian Longden <ilongden@morgan.harvard.edu>,

"""
import traceback
from urllib.error import HTTPError
from chado_object.feature.chado_feature import ChadoFeatureObject

from harvdev_utils.production import (
    Feature,
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
    ExternalLookup
)
from harvdev_utils.char_conversions import (
    sgml_to_unicode, sgml_to_plain_text, greek_to_sgml
)
from chado_object.feature.chado_feature import FIELD_VALUE


def run_checks(self: ChadoFeatureObject) -> None:
    # Run various checks, some will give critical errors.
    # others will give warnings.
    for index, chemical in enumerate(self.chemical_id_data):
        # Check that chemical ids have not been used before
        feat = self.session.query(Feature).\
            join(FeatureDbxref).\
            join(Dbxref).\
            join(Db).filter(Feature.is_obsolete.is_(False),
                            Db.name == chemical['source'],
                            Dbxref.accession == chemical['accession']).one_or_none()
        if feat:
            message = f"{chemical['source']}:{chemical['accession']} has already been applied to {feat.uniquename} '{feat.name}'"
            self.critical_error(self.process_data['CH3a']['data'][index], message)

        # If not new
        if not self.new_chemical_entry:
            # check if we already have an entry in the database
            dbxref = self.session.query(Dbxref).\
                join(Db).\
                join(FeatureDbxref).filter(Db.name == chemical['source'],
                                           FeatureDbxref.feature_id == self.feature.feature_id).one_or_none()
            if dbxref and 'CH3a' not in self.bang_c:  # already has an entry ?
                chemical['exists_already'] = True
                if chemical['accession'] == dbxref.accession:
                    self.warning_error(self.process_data['CH3a']['data'][index], "Already in the database, No need to re add it")
                else:
                    message = f"Already has a {chemical['source']} attached and has a different value of {dbxref.accession}"
                    message += f" to the one stated here {chemical['accession']}"
                    self.critical_error(self.process_data['CH3a']['data'][index], message)

        # check CH1a is a known synonym or give a warning
        found = False
        check_name = self.feature.name.lower()
        if check_name == str(chemical['name']).lower():
            return
        for syn in chemical['synonyms']:
            if syn.lower() == check_name:
                found = True
        if not found:
            message = f"{self.process_data['CH3a']['data'][index][FIELD_VALUE]} synonyms list, Does not contain {self.feature.name}. Possible typo?"
            self.warning_error(self.process_data['CH1a']['data'], message)


def process_chemical(self: ChadoFeatureObject, key: str) -> None:
    # So we have a new chemical, lets get the data for this.

    # data is stored in self.chemical_id_data.
    identifier_found = False
    try:
        identifier_found = self.validate_fetch_identifier_at_external_db('CH3a')
    except HTTPError as e:
        message = f"Problem looking up identifier: {e}"
        self.critical_error(self.process_data[key]['data'][0], message)
    except Exception as error:
        message = f"Gen error: Problem looking up identifier: {error} {type(error)}"
        self.critical_error(self.process_data[key]['data'][0], message)
        self.critical_error(self.process_data[key]['data'][0], traceback.print_exc())

    if not identifier_found:
        return

    # So we have the chemical ids now. So we want to do various checks.
    self.run_checks()

    for chemical_information in self.chemical_id_data:
        # self.alt_comparison()  # TODO
        self.add_dbxref(chemical_information)

        # Add the identifier as a synonym and other synonyms
        chemical_information['synonyms'].append(f"{chemical_information['source']}:{chemical_information['accession']}")
        self.process_synonyms_from_external_db(chemical_information)

        # Add the description as a featureprop.
        self.add_description_to_featureprop(chemical_information)

        # Add the inchikey as a featureprop.
        self.add_inchikey_to_featureprop(chemical_information)

        # Add pub link to Chebi or pubchem amd current pub
        feature_pub, _ = get_or_create(self.session, FeaturePub,
                                       feature_id=self.feature.feature_id,
                                       pub_id=chemical_information['PubID'])

    feature_pub, _ = get_or_create(self.session, FeaturePub,
                                   feature_id=self.feature.feature_id,                                   pub_id=self.pub.pub_id)


def add_dbxref(self: ChadoFeatureObject, chemical: dict) -> None:
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


def look_up_static_references(self: ChadoFeatureObject) -> None:
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


def validate_fetch_identifier_at_external_db(self: ChadoFeatureObject, process_key: str) -> bool:
    """Fetch and validate externaldb.

    process_key: Key to use to get data , should be CH3a.

    Identifiers and names for ChEBI / PubChem entries are processed at their respective db.
    However, InChIKey entries and definitions always come from PubChem.
    This is because PubChem cites ChEBI (as well as other external definitions) whereas
    ChEBI does not provide this service.
    """

    database_dispatch_dictionary = {
        'CHEBI': self.check_chebi_for_identifier,
        'PubChem': self.check_pubchem_for_identifier,
        'PubChem_SID': self.check_pubchem_for_identifier
    }

    all_okay = True
    for index, item in enumerate(self.process_data[process_key]['data']):
        chemical = {
            'accession': None,
            'source': None,
            'name': None,
            'description': None,
            'inchikey': None,
            'synonyms': None,
            'DBObject': None,
            'PubID': None,
            'exists_already': False
        }
        identifier_unprocessed = item[FIELD_VALUE]
        identifier_unprocessed = sgml_to_unicode(identifier_unprocessed)
        chemical['source'], chemical['accession'], chemical['name'], error_msg = self.split_identifier_and_name(identifier_unprocessed, process_key)
        if error_msg:
            message = "Wrong format should be 'DBNAME:number ; text'"
            self.critical_error(self.process_data[process_key]['data'][index], message)
            all_okay = False
            continue

        self.log.debug(f"Found db {chemical['source']}: {chemical['accession']} and identifier_name: {chemical['name']}")

        # Obtain our identifier, name, definition, and InChIKey from ChEBI / PubChem.
        try:
            identifier_and_data = database_dispatch_dictionary[chemical['source']](chemical, process_key, index)
            self.log.debug("identifier_and_data is {}".format(identifier_and_data))
        except KeyError as e:
            self.critical_error(self.process_data[process_key]['data'][index],
                                'Database name not recognized from identifier: {}. {}'.format(chemical['source'], e))
            all_okay = False
            continue
        except HTTPError as e:
            self.critical_error(self.process_data[process_key]['data'][index],
                                'Server side Error : {}. {}'.format(chemical['source'], e))
            all_okay = False
            continue

        if identifier_and_data is False:  # Errors are already declared in the sub-functions.
            all_okay = False
            continue
        # If we're at this stage, we have all our data for PubChem BUT
        # for a ChEBI query we need to go to PubChem for the definition.
        if chemical['source'] != 'PubChem':
            # Set the identifier name to the result queried from ChEBI.
            err = self.add_description_from_pubchem(chemical)
            if err:
                self.warning_error(self.process_data[process_key]['data'][index], err)
        elif chemical['source'] == 'PubChem_SID':
            chemical['source'] = 'PubChem'
        self.chemical_id_data.append(chemical)
    return all_okay


def check_chebi_for_identifier(self: ChadoFeatureObject, chemical: dict, process_key: str, index: int) -> bool:
    """Check for chebi identifier.

    Returns: True if data is successfully found.
             False if there are any issues.
    """
    try:
        chebi = ExternalLookup.lookup_chebi(chemical['accession'], synonyms=True)
    except HTTPError as e:
        message = f"Problem ChEBI lookup, server problems? {e}"
        self.critical_error(self.process_data[process_key]['data'][index], message)
        return False
    if not chebi:
        self.critical_error(self.process_data[process_key]['data'][index], chebi.error)
        return False

    if not chebi.inchikey:
        self.log.debug(f"No InChIKey found for entry: {chemical['source']}:{chemical['accession']}")

    # Check whether the name intended to be used in FlyBase matches
    # the name returned from the database.
    if self.has_data('CH1a'):
        plain_text = sgml_to_plain_text(self.process_data['CH1a']['data'][FIELD_VALUE])
        if chebi.name.lower() != plain_text.lower():
            self.log.warning('ChEBI name does not match name specified for FlyBase: {} -> {}'.format(chebi.name, plain_text))
        else:
            self.log.debug('Queried name \'{}\' matches name used in proforma \'{}\''.format(chebi.name, self.process_data['CH1a']['data'][FIELD_VALUE]))

    # Check whether the identifier_name supplied by the curator matches
    # the name returned from the database.
    if chemical['name']:
        plain_text = sgml_to_plain_text(greek_to_sgml(chemical['name']))
        if sgml_to_plain_text(chebi.name.lower()) != plain_text.lower():
            message = 'ChEBI name does not match name specified in identifier field: {} != {}'.\
                format(chebi.name, plain_text)
            self.warning_error(self.process_data[process_key]['data'][index], message)

    chemical['name'] = chebi.name
    chemical['inchikey'] = chebi.inchikey
    chemical['description'] = chebi.description
    chemical['synonyms'] = chebi.synonyms
    chemical['PubID'] = self.chebi_pub_id
    chemical['DBObject'] = self.session.query(Db). \
        filter(Db.name == chemical['source']).one()
    return True


def add_description_from_pubchem(self: ChadoFeatureObject, chemical: dict) -> bool:
    """Add description from pubchem."""
    mess = ''
    if not chemical['description']:
        pubchem = ExternalLookup.lookup_by_name('pubchem', chemical['name'])
        if pubchem.error:
            mess = pubchem.error
        else:
            chemical['description'] = pubchem.description
    return mess


def check_pubchem_for_identifier(self: ChadoFeatureObject, chemical: dict, process_key: str, index: int) -> bool:
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
        self.critical_error(self.process_data[process_key]['data'][index], message)
        return False

    # Check whether the identifier_name supplied by the curator matches
    # the name returned from the database.
    if chemical['name']:
        plain_text = sgml_to_plain_text(self.process_data['CH1a']['data'][FIELD_VALUE])
        if chemical['source'] != 'PubChem_SID' and pubchem.name.lower() != plain_text.lower():
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


def add_inchikey_to_featureprop(self: ChadoFeatureObject, chemical_information: dict) -> None:
    """Associates the inchikey from PubChem to a feature via featureprop.

    :return:
    """
    if not chemical_information['inchikey']:
        return

    description_cvterm_id = self.cvterm_query('property type', 'inchikey')

    get_or_create(self.session, Featureprop, feature_id=self.feature.feature_id,
                  type_id=description_cvterm_id, value=chemical_information['inchikey'])


def process_synonyms_from_external_db(self: ChadoFeatureObject, chemical: dict, alt: bool = False) -> None:
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
                try:
                    sgml = sgml_to_unicode(name)
                    name = sgml_to_plain_text(greek_to_sgml(name))
                except KeyError:
                    # So got special char we do not know what to do with,
                    # So we will ignore it for now and just give a warning.
                    self.log.warning(f"Problem doing conversion, unknown char being ignored from external db: name = {name}")
                    continue
                if lowercase:
                    name = name.lower()
                if name in seen_it:
                    continue

                new_synonym, _ = get_or_create(self.session, Synonym, type_id=symbol_cv_id,
                                               synonym_sgml=sgml,
                                               name=name)
                seen_it.add(name)
                fs, _ = get_or_create(self.session, FeatureSynonym, feature_id=self.feature.feature_id,
                                      pub_id=pub_id, synonym_id=new_synonym.synonym_id)
                fs.is_current = False


    if alt:  # If alternative then already done.
        return
    if self.has_data('CH1a'):
        name = sgml_to_plain_text(self.process_data['CH1a']['data'][FIELD_VALUE])
        sgml = sgml_to_unicode(self.process_data['CH1a']['data'][FIELD_VALUE])

    new_synonym, _ = get_or_create(self.session, Synonym, type_id=symbol_cv_id,
                                   synonym_sgml=sgml,
                                   name=name)

    fs, _ = get_or_create(self.session, FeatureSynonym, feature_id=self.feature.feature_id,
                          pub_id=pub_id, synonym_id=new_synonym.synonym_id)
    fs.is_current = True
