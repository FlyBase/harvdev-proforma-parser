"""
:synopsis: The "Allele" ChadoObject.

:overview: Cut down version of Allele to start with to enable DIV Proforma to work.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>, Ian Longden <ilongden@morgan.harvard.edu>
"""

import logging
import os
from harvdev_utils.chado_functions import (
    get_or_create
)
from chado_object.utils.go import process_DO_line
from chado_object.feature.chado_feature import ChadoFeatureObject
from harvdev_utils.production import (
    FeaturePub, FeatureCvterm, FeatureCvtermprop
)
from harvdev_utils.chado_functions import (
    get_cvterm
)
from chado_object.chado_base import FIELD_VALUE
from sqlalchemy.orm.exc import NoResultFound
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
        self.type_dict = {'cvterm': self.load_feature_cvterm,
                          'DOcvtermprop': self.load_do,
                          'feature_relationship': self.load_feature_relationship,
                          'featureprop': self.load_featureprop,
                          'synonym': self.load_synonym,
                          'ignore': self.ignore}
        self.delete_dict = {'featureprop': self.delete_featureprop,
                            'synonym': self.delete_synonym,
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

        # feature relationship to gene
        self.process_data['GENE']['data'] = [('GENE', self.gene.name, 0, False)]
        self.load_feature_relationship('GENE')  # We have a special key in the yml file called 'GENE'
        del self.process_data['GENE']

        # bang c first as this supersedes all things
        if self.bang_c:
            self.bang_c_it()
        if self.bang_d:
            self.bang_d_it()

        for key in self.process_data:
            log.debug("Processing {}".format(self.process_data[key]))
            self.type_dict[self.process_data[key]['type']](key)

        return self.feature

    def get_allele(self):
        """Get initial allele and check."""
        # NOTE: new 'SO' will be 'allele' when it come in
        self.load_feature(feature_type='allele')

    def ignore(self, key):
        """Ignore."""
        pass

    def add_cvtermprops(self, key, do_dict):
        """Add props."""
        # create feature_cvterm
        feat_cvt, _ = get_or_create(self.session, FeatureCvterm,
                                    feature_id=self.feature.feature_id,
                                    cvterm_id=do_dict['docvterm'].cvterm_id,
                                    pub_id=self.pub.pub_id)

        for prop_key in self.process_data[key]['prop_cvterms']:
            try:
                cvtermprop = get_cvterm(self.session, self.process_data[key]['prop_cv'], prop_key)
            except NoResultFound:
                message = "Unable to find cvterm {} for Cv {}.".format(prop_key, self.process_data[key]['cv'])
                self.critical_error((1, 2, 3), message)
                return None

            # create feature_cvtermprop
            get_or_create(self.session, FeatureCvtermprop,
                          feature_cvterm_id=feat_cvt.feature_cvterm_id,
                          value=do_dict[prop_key],
                          type_id=cvtermprop.cvterm_id)

    def load_do(self, key):
        """Load DO."""
        do_dict = {}
        for item in self.process_data[key]['data']:
            do_dict = process_DO_line(
                self.session,
                item[FIELD_VALUE],
                self.process_data[key]['cv'],
                self.process_data[key]['allowed_qualifiers'],
                self.process_data[key]['allowed_symbols'],
                self.process_data[key]['allowed_codes'])

            if do_dict['error']:
                for err in do_dict['error']:
                    self.critical_error(item, err)
                continue
            self.add_cvtermprops(key, do_dict)
