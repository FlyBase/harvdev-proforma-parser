"""

:synopsis: The "chem" ChadoObject.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>,
               Ian Longden <ianlongden@morgan.harvard.edu>

"""
import logging
import os
from typing import Union, Tuple

from chado_object.feature.chado_feature import FIELD_VALUE, ChadoFeatureObject
from harvdev_utils.chado_functions import (
    get_cvterm,
    get_or_create,
    synonym_name_details)
from harvdev_utils.char_conversions import sgml_to_unicode, sgml_to_plain_text
from harvdev_utils.production import (
    Feature,
    Featureprop,
    FeatureSynonym,
    Pub,
    Synonym)

log = logging.getLogger(__name__)


class ChadoChem(ChadoFeatureObject):
    """Process the Chemical Proforma."""
    from chado_object.chemical.chado_get_create import (
        check_existing_already,
        check_for_dbxref,
        chemical_feature_lookup,
        fetch_by_FBch_and_check,
        get_or_create_chemical)
    from chado_object.chemical.chemical_lookup import (
        add_dbxref,
        add_description_from_pubchem,
        add_inchikey_to_featureprop,
        check_chebi_for_identifier,
        check_pubchem_for_identifier,
        look_up_static_references,
        process_chemical,
        run_checks,
        process_synonyms_from_external_db,
        validate_fetch_identifier_at_external_db)
    from chado_object.chemical.chemical_merge import merge

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
        self.pub: Union[Pub, None] = None             # All other proforma need a reference to a pub
        self.feature: Union[Feature, None] = None     # The chemical object, to get feature_id use self.chemical.feature_id.
        self.chebi_pub_id: int = 0                    # Used for attributing chemical curation.
        self.pubchem_pub_id: int = 0                  # Used for attributing chemical curation.

        # yaml file defines what to do with each field. Follow the light
        self.type_dict = {'featureprop': self.load_featureprop,
                          'synonym': self.load_synonym_chem,
                          'ignore': self.ignore,
                          'value': self.ignore,
                          'rename': self.rename,
                          'chemical_lookup': self.process_chemical,
                          'disspub': self.dissociate_from_pub,
                          'obsolete': self.make_obsolete}

        self.delete_dict = {'ignore': self.ignore_delete,
                            'synonym': self.rename_synonym,
                            'featureprop': self.delete_featureprop,
                            'chemical_lookup': self.delete_chem_ids,
                            'value': self.change_featurepropvalue}

        # Chemical storage dictionary.
        # This array of dictionarys contains all the information required to create a new FBch.
        self.chemical_id_data = []

        self.type_name = 'chemical entity'

        ############################################################
        # Get processing info and data to be processed.
        # Please see the yml/chemical.yml file for more details
        ############################################################
        yml_file = os.path.join(os.path.dirname(__file__), '../yml/chemical.yml')

        # Populated self.process_data with all possible keys.
        self.process_data = self.load_reference_yaml(yml_file, params)

        #####################################################
        # Checking whether we're working with a new chemical.
        #####################################################
        self.new_chemical_entry: bool = False
        if self.process_data['CH1f']['data'][FIELD_VALUE] == "new":
            self.new_chemical_entry = True

        self.log = log

    def ignore(self: ChadoFeatureObject, key: str) -> str:
        """Ignore."""
        pass

    def ignore_delete(self: ChadoFeatureObject, key: str, bangc: bool = True) -> None:
        """Ignore."""
        pass

    def delete_chem_ids(self: ChadoFeatureObject, key: str, bangc: bool = True) -> None:
        """ Delete the chemical chebi/pubchem entries for this entry
        So we want to remove ALL dbxrefs for ChEBI and Pubchem for this feature.
        Remove the synonyms wrt to the "Chemical" papers for those.
        Remove feature props inchikey, is_variant.
        """
        pass  # TODO

    def sanity_checks(self: ChadoFeatureObject, references: dict) -> None:
        """Sanity checks that are not easily done in cerberos"""

        # Must have a reference.
        try:
            self.pub = references['ChadoPub']
        except KeyError:
            message = "Unable to find publication."
            self.critical_error(self.process_data['CH1a']['data'], message)

        # If new chemical,  CH3a MUST be set
        # UNLESS we are merging.
        if not self.has_data('CH1g'):  # NOT merging
            if self.has_data('CH1f') and self.process_data['CH1f']['data'][FIELD_VALUE] == 'new':  # Its new
                if not self.has_data('CH3a'):  # CH3a NOT defined
                    self.critical_error(self.process_data['CH1f']['data'], "CH3a MUST be set for new chemicals")

        # Sometimes FBch are accidentally input here, so give error if found.
        for field_key in ['CH1a', 'CH1b']:
            if self.has_data(field_key):
                if type(self.process_data[field_key]['data']) == list:
                    for item in self.process_data[field_key]['data']:
                        if item[FIELD_VALUE].startswith('FBch'):
                            self.critical_error(self.process_data[field_key]['data'][0], "Cannot start with FBch")
                else:
                    if self.process_data[field_key]['data'][FIELD_VALUE].startswith('FBch'):
                        self.critical_error(self.process_data[field_key]['data'], "Cannot start with FBch")

    def load_content(self, references):
        """Process the proforma fields."""

        self.sanity_checks(references)

        # merging is a whole different thing so lets do that seperately.
        # and then exit.
        if self.has_data('CH1g'):
            self.merge()
            return

        self.get_or_create_chemical()
        if not self.feature:
            log.info("CHEM/FEAT NO FEATURE???")
            return

        # Dissociate pub ONLY
        if self.has_data('CH3g'):
            self.dissociate_pub()
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

        if self.new_chemical_entry and self.chemical_id_data:
            self.add_full_name_for_chem_paper(self.chemical_id_data[0])
        return self.feature

    def add_full_name_for_chem_paper(self: ChadoFeatureObject, chemical_information):
        """Add synonym of the alternative chemical id.

        Use the current feature/name and the paper it belongs to
        either pubchem or chebi.
        """
        if self.new_chemical_entry and chemical_information['PubID']:
            organism, plain_name, sgml = synonym_name_details(self.session, self.process_data['CH1a']['data'][FIELD_VALUE], nosup=True)
            cvterm = self.cvterm_query('synonym type', 'fullname')
            pub_id = chemical_information['PubID']

            new_synonym, _ = get_or_create(self.session, Synonym, type_id=cvterm,
                                           synonym_sgml=sgml,
                                           name=plain_name)
            fs, _ = get_or_create(self.session, FeatureSynonym, feature_id=self.feature.feature_id,
                                  pub_id=pub_id, synonym_id=new_synonym.synonym_id)

    def dissociate_pub(self: ChadoFeatureObject):
        if self.has_data('CH1f') and self.process_data['CH1f']['data'][FIELD_VALUE] == 'new':
            message = "Cannot dissociate pub with CH1f as 'new'."
            self.critical_error(self.process_data['CH1f']['data'], message)
            return None
        self.dissociate_from_pub('CH3g')

    def get_external_chemical_pub_id(self: ChadoFeatureObject):
        """Get pub id for Chemical."""
        return self.chemical_information['PubID']

    def change_featurepropvalue(self: ChadoFeatureObject, key, bangc=True):
        """Change the featureprop value."""
        prop_cv_id = self.cvterm_query(self.process_data['CH3b']['cv'], self.process_data['CH3b']['cvterm'])

        if self.feature:
            fp, is_new = get_or_create(self.session, Featureprop, feature_id=self.feature.feature_id,
                                       type_id=prop_cv_id)
        else:
            message = "Coding error, no Feature is defined yet!!"
            self.critical_error(self.process_data[key]['data'], message)

        if is_new:
            message = "No current value specified in chado so cannot bangc it"
            self.critical_error(self.process_data[key]['data'], message)
        else:
            fp.value = self.process_data[key]['data'][FIELD_VALUE]
        self.process_data[key]['data'] = None
        self.process_data['CH3b']['data'] = None

    def load_synonym_chem(self: ChadoFeatureObject, key: str):
        """Load the synonym.
        """
        self.load_synonym(key, unattrib=False)

    def rename_synonym(self: ChadoFeatureObject, key: str, bangc=True):
        """Rename the synonym."""
        if not self.has_data(key):
            message = "Bangc MUST have a value."
            self.critical_error(self.process_data[key]['data'], message)
            return
        self.load_synonym_chem(key)
        self.process_data[key]['data'] = None

    def process_synonym(self: ChadoFeatureObject, key: str):
        """ Load the synonym IF it is new
        """
        if self.new_chemical_entry:
            self.load_synonym(key, unattrib=False)

    def add_description_to_featureprop(self: ChadoFeatureObject, chemical_information: dict):
        """Associate the description from PubChem to a feature via featureprop."""
        log.debug('Adding PubChem description to featureprop.')

        description_cvterm_id = self.cvterm_query('property type', 'description')

        get_or_create(self.session, Featureprop, feature_id=self.feature.feature_id,
                      type_id=description_cvterm_id, value=chemical_information['description'])

    def split_identifier_and_name(self: ChadoFeatureObject, identifier_unprocessed, process_key) -> Tuple:
        """Strip away the name if one is supplied with the identifier. """
        identifier_db = ''
        identifier_acc = ''
        identifier_name = ''
        error_msg = ''
        identifier_unprocessed = sgml_to_plain_text(identifier_unprocessed)

        identifier_split_list = identifier_unprocessed.split(';')
        try:
            identifier = identifier_split_list.pop(0).strip()
            identifier_name = identifier_split_list.pop(0).strip()
        except IndexError:
            error_msg = "Error splitting identifier and name using semicolon. {}".format(identifier_unprocessed)
        if identifier_split_list:  # If the list is not empty by this point, raise an error.
            error_msg = "Error splitting identifier and name using semicolon. {}".format(identifier_unprocessed)
            return '', '', '', error_msg

        identifier_split_list = identifier.split(':')
        try:
            identifier_db = identifier_split_list.pop(0).strip()
            identifier_acc = identifier_split_list.pop(0).strip()
        except IndexError:
            error_msg = "Error splitting db and acc using colon. {}".format(identifier)
        if identifier_split_list:  # If the list is not empty by this point, raise an error.
            error_msg = "Error splitting db and acc using colon. {}".format(identifier)
            return '', '', '', error_msg

        return identifier_db, identifier_acc, identifier_name, error_msg

    def rename(self: ChadoFeatureObject, key: str):
        if not self.feature:
            return
        name = sgml_to_unicode(self.process_data[key]['data'][FIELD_VALUE])
        self.feature.name = name
        cvterm = get_cvterm(self.session, 'synonym type', 'fullname')
        fss = self.session.query(FeatureSynonym).\
            join(Synonym).\
            filter(FeatureSynonym.feature_id == self.feature.feature_id,
                   FeatureSynonym.is_current.is_(True),
                   Synonym.type_id == cvterm.cvterm_id)
        for fs in fss:
            fs.is_current = False
        _, plain_name, sgml = synonym_name_details(self.session, name, nosup=True)
        synonym, _ = get_or_create(self.session, Synonym, type_id=cvterm.cvterm_id, name=plain_name, synonym_sgml=sgml)

        fs, _ = get_or_create(self.session, FeatureSynonym, feature_id=self.feature.feature_id, synonym_id=synonym.synonym_id,
                              pub_id=self.pub.pub_id)

    def make_obsolete(self: ChadoFeatureObject, key: str) -> None:
        """Make the chemical record obsolete.

        Args:
            key (string): Proforma field key
        """
        if self.feature:
            self.feature.is_obsolete = True
        else:
            self.critical_error(self.process_data[key]['data'], "Coding error feature is not defined.")
