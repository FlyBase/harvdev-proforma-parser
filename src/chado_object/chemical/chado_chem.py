"""

:synopsis: The "chem" ChadoObject.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>,
               Ian Longden <ianlongden@morgan.harvard.edu>

"""
from typing import Union
from harvdev_utils.production import (
    Feature, Featureprop,
    FeatureSynonym, Synonym
)
from chado_object.feature.chado_feature import ChadoFeatureObject, FIELD_VALUE
from harvdev_utils.chado_functions import (
    get_or_create,
    get_cvterm,
    synonym_name_details
)

from harvdev_utils.char_conversions import (
    sgml_to_unicode
)
# from .chado_base import FIELD_VALUE

# from datetime import datetime
import os
import logging

log = logging.getLogger(__name__)


class ChadoChem(ChadoFeatureObject):
    """Process the Chemical Proforma."""
    from chado_object.chemical.chemical_merge import (
        merge
    )

    from chado_object.chemical.chado_get_create import (
        get_or_create_chemical,
        check_for_dbxref,
        check_existing_already,
        fetch_by_FBch_and_check,
        chemical_feature_lookup
    )

    from chado_object.chemical.chemical_lookup import (
        add_alt_synonym,
        process_chemical,
        alt_comparison,
        add_alternative_info,
        add_dbxref,
        add_inchikey_to_featureprop,
        look_up_static_references,
        validate_fetch_identifier_at_external_db,
        check_chebi_for_identifier,
        check_pubchem_for_identifier,
        add_description_from_pubchem,
        process_synonyms_from_external_db
    )

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
        self.feature: Union[Feature, None] = None        # The chemical object, to get feature_id use self.chemical.feature_id.
        self.chebi_pub_id = None    # Used for attributing chemical curation.
        self.pubchem_pub_id = None  # Used for attributing chemical curation.

        # yaml file defines what to do with each field. Follow the light
        self.type_dict = {'featureprop': self.load_featureprop,
                          'synonym': self.load_synonym_chem,
                          'ignore': self.ignore,
                          'value': self.ignore,
                          'rename': self.rename,
                          'chemical_lookup': self.process_chemical,
                          'disspub': self.dissociate_from_pub}

        self.delete_dict = {'ignore': self.ignore_delete,
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
        if self.process_data['CH1f']['data'][FIELD_VALUE] == "new":
            self.new_chemical_entry = True
        else:
            self.new_chemical_entry = False
        self.log = log

    def ignore(self: ChadoFeatureObject, key: str):
        """Ignore."""
        pass

    def ignore_delete(self: ChadoFeatureObject, key: str, bangc: bool = True):
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

        # merging is a whole differnt thing so lets do that seperately.
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

        # timestamp = datetime.now().strftime('%c')
        # curated_by_string = 'Curator: %s;Proforma: %s;timelastmodified: %s' % (
        #    self.curator_fullname, self.filename_short, timestamp)
        # log.debug('Curator string assembled as:')
        # log.debug('%s' % curated_by_string)
        return self.feature

    def dissociate_pub(self):
        if self.has_data('CH1f') and self.process_data['CH1f']['data'][FIELD_VALUE] == 'new':
            message = "Cannot dissociate pub with CH1f as 'new'."
            self.critical_error(self.process_data['CH1f']['data'], message)
            return None
        self.dissociate_from_pub('CH3g')

    def get_external_chemical_pub_id(self):
        """Get pub id for Chemical."""
        return self.chemical_information['PubID']

    def delete_featureprop(self, key, bangc=True):
        """Delete the featureprop."""
        prop_cv_id = self.cvterm_query(self.process_data[key]['cv'], self.process_data[key]['cvterm'])

        fps = self.session.query(Featureprop).join(Feature).\
            filter(Feature.feature_id == self.feature.feature_id,
                   Featureprop.type_id == prop_cv_id).all()
        count = 0
        for fp in fps:
            count += 1
            log.debug(f"Deleting {fp}.")
            self.session.delete(fp)
        if not count:
            message = "No current {} field specified in chado so cannot bangc it".format(key)
            self.critical_error(self.process_data[key]['data'], message)

    def change_featurepropvalue(self, key, bangc=True):
        """Change the featureprop value."""
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

    def split_identifier_and_name(self, identifier_unprocessed, process_key):
        """Strip away the name if one is supplied with the identifier."""
        identifier = None
        identifier_name = None
        identifier_unprocessed = sgml_to_unicode(identifier_unprocessed)
        if ';' in identifier_unprocessed:
            self.log.debug('Semicolon found, splitting identifier: {}'.format(identifier_unprocessed))
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

    def rename(self, key):
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
        _, plain_name, sgml = synonym_name_details(self.session, name)
        synonym, _ = get_or_create(self.session, Synonym, type_id=cvterm.cvterm_id, name=plain_name, synonym_sgml=sgml)

        fs, _ = get_or_create(self.session, FeatureSynonym, feature_id=self.feature.feature_id, synonym_id=synonym.synonym_id,
                              pub_id=self.pub.pub_id)