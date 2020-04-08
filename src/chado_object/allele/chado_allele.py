"""
:synopsis: The "Allele" ChadoObject.

:overview: Cut down version of Allele to start with to enable DIV Proforma to work.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>, Ian Longden <ilongden@morgan.harvard.edu>
"""

import logging
import os
from sqlalchemy.orm.exc import NoResultFound
from harvdev_utils.chado_functions import (
    get_or_create, feature_symbol_lookup
)
from chado_object.feature.chado_feature import ChadoFeatureObject, FIELD_VALUE
from harvdev_utils.production import (
    FeaturePub
)

log = logging.getLogger(__name__)


class ChadoAllele(ChadoFeatureObject):
    """Process the Disease Implicated Variation (DIV) Proforma."""

    def __init__(self, params):
        """Initialise the chado object."""
        log.debug('Initializing ChadoAllele object.')

        # Initiate the parent.
        super(ChadoAllele, self).__init__(params)

        self.proforma_start_line_number = params.get('proforma_start_line_number')
        self.set_values = params.get('set_values')
        self.new = False

        # yaml file defines what to do with each field. Follow the light
        self.type_dict = {'feature_relationship': self.load_feature_relationship,
                          'featureprop': self.load_featureprop,
                          'ignore': self.ignore}
        self.proforma_start_line_number = params.get('proforma_start_line_number')

        ###########################################################
        # Values queried later, placed here for reference purposes.
        ############################################################
        self.pub = None
        self.feature = None
        self.gene = None
        self.type_name = 'gene'

        ############################################################
        # Get processing info and data to be processed.
        # Please see the yml/publication.yml file for more details
        ############################################################
        yml_file = os.path.join(os.path.dirname(__file__), '../yml/allele.yml')
        # Populated self.process_data with all possible keys.
        self.process_data = self.load_reference_yaml(yml_file, params)
        # self.genus = "Drosophila"
        # self.species = "melanogaster"

    def load_content(self, references):
        """Process the data."""
        try:
            self.pub = references['ChadoPub']
        except KeyError:
            message = "Unable to find publication."
            self.critical_error(self.process_data['GA1a']['data'], message)
            return None
        try:
            self.gene = references['ChadoGene']
        except KeyError:
            message = "Unable to find gene. Normally Allele should have a gene before."
            self.warning_error(self.process_data['GA1a']['data'], message)
            return None

        self.get_allele()
        if not self.feature:  # problem getting gene, lets finish
            return

        # feature pub
        get_or_create(self.session, FeaturePub, feature_id=self.feature.feature_id, pub_id=self.pub.pub_id)

        # bang c first as this supersedes all things
        if self.bang_c:
            self.bang_c_it()
        if self.bang_d:
            self.bang_d_it()

        for key in self.process_data:
            log.debug("Processing {}".format(self.process_data[key]['data']))
            self.type_dict[self.process_data[key]['type']](key)

        return self.feature

    def get_allele(self):
        """Get initial allele and check."""
        self.feature = None
        if self.process_data['GA1g']['data'][FIELD_VALUE] == 'y':  # Should exist already
            # organism, plain_name, sgml = synonym_name_details(self.session, self.process_data['GA1a']['data'][FIELD_VALUE])
            try:
                # Alleles are genes.
                self.feature = feature_symbol_lookup(self.session, self.type_name,
                                                     self.process_data['GA1a']['data'][FIELD_VALUE])
            except NoResultFound:
                message = "Unable to find Allele with symbol {}.".format(self.process_data['GA1a']['data'][FIELD_VALUE])
                self.critical_error(self.process_data['GA1a']['data'], message)
                return

    def ignore(self, key):
        """Ignore."""
        pass
