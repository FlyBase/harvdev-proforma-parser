"""
:synopsis: The geneproduct ChadoObject.

:moduleauthor: Gil dos Santos <dossantos@morgan.harvard.edu>
"""
import logging
import os


from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound


from chado_object.chado_base import FIELD_VALUE
from chado_object.feature.chado_feature import ChadoFeatureObject
from harvdev_utils.char_conversions import sgml_to_plain_text

from chado_object.utils.feature_synonym import fs_remove_current_symbol

from harvdev_utils.chado_functions import (
    get_feature_and_check_uname_symbol, CodingError,
    DataError, feature_symbol_lookup, get_or_create)
from harvdev_utils.production import (
    Feature,
    FeatureCvterm,
    FeaturePub,
    FeatureRelationship)
log = logging.getLogger(__name__)


class ChadoGeneProduct(ChadoFeatureObject):
    """ChadoGeneProduct object."""

    def __init__(self, params):
        """Initialize the ChadoGeneProduct Object."""
        log.debug('Initializing ChadoGeneProduct object.')

        # Initiate the parent.
        super(ChadoGeneProduct, self).__init__(params)

        ##########################################
        # Set up how to process each type of input
        ##########################################
        self.type_dict = {
            'synonym': self.geneproduct_load_synonym,
            'ignore': self.ignore
        }
        # self.delete_dict = {'synonym': self.delete_synonym,
        #                     'cvtermprop': self.delete_feature_cvtermprop,
        #                     'featureprop': self.delete_featureprop,
        #                     'featurerelationship': self.delete_feature_relationship
        #                     }
        self.proforma_start_line_number = params.get('proforma_start_line_number')

        ###########################################################
        # Values queried later, placed here for reference purposes.
        ############################################################
        self.pub = None
        self.type_name = ""
        # self.set_values = params.get('set_values')

        ############################################################
        # Get processing info and data to be processed.
        # Please see the yml/publication.yml file for more details
        ############################################################
        yml_file = os.path.join(os.path.dirname(__file__), '../yml/geneproduct.yml')
        # Populated self.process_data with all possible keys.
        self.process_data = self.load_reference_yaml(yml_file, params)
        self.log = log

    def load_content(self, references: dict):
        """Process the data.

        Args:
            references: <dict> previous reference proforma
        Returns:
            <Feature object> A feature object.
        """
        try:
            self.pub = references['ChadoPub']
        except KeyError:
            message = "Unable to find publication."
            self.critical_error(self.process_data['F1a']['data'], message)
            return None

        self.get_geneproduct()
        if not self.feature:  # problem getting geneproduct, lets finish
            return None

        # bang c first as this supersedes all things
        if self.bang_c:
            self.bang_c_it()
        if self.bang_d:
            self.bang_d_it()

        if self.set_values:
            self.process_sets()

        for key in self.process_data:
            if key not in self.set_values.keys():
                if 'type' not in self.process_data[key]:
                    self.critical_error(self.process_data[key]['data'],
                                        "No sub to deal type '{}' yet!! Report to HarvDev".format(key))
                self.type_dict[self.process_data[key]['type']](key)

    def get_geneproduct(self):  # noqa
        """Get or create the gene product feature."""
        symbol_key = 'F1a'
        id_key = 'F1f'
        feature_type = None
        if self.has_data('F3'):
            type_name = self.process_data['F3']['data'][FIELD_VALUE]

        if not self.feature and self.has_data(id_key) and self.process_data[id_key]['data'][FIELD_VALUE] != "new":
            self.feature = None
            try:
                self.feature = get_feature_and_check_uname_symbol(self.session,
                                                                  self.process_data[id_key]['data'][FIELD_VALUE],
                                                                  self.process_data[symbol_key]['data'][FIELD_VALUE])
                self.is_new = False
            except DataError as e:
                self.critical_error(self.process_data[id_key]['data'], e.error)
            return

        # BOB: How is "is_new" set to True (specified in F1f)?
        # BOB: How do we confirm that there is not an existing feature with same name and type?

    def geneproduct_load_synonym(self, key):
        if self.has_data(key):
            add_okay = True
            for item in self.process_data[key]['data']:
                if item[FIELD_VALUE] == self.process_data['F1a']['data'][FIELD_VALUE]:
                    add_okay = False
            if add_okay:
                self.load_synonym(key)

    def ignore(self, key: str):
        """Ignore, done by initial setup.

        Args:
            key (string): Proforma field key
                NOT used, but is passed automatically.
        """
        pass
