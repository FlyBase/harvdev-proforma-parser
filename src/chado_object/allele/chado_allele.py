"""
:synopsis: The "Allele" ChadoObject.

:overview: Cut down version fo Allele to start with to enable DIV Proforma to work.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>, Ian Longden <ilongden@morgan.harvard.edu>
"""

import logging
import os
from sqlalchemy.orm.exc import NoResultFound

# from harvdev_utils.chado_functions import get_or_create
from harvdev_utils.production import (
    FeatureRelationship, FeatureRelationshipPub
)
from chado_object.chado_base import FIELD_VALUE, ChadoObject
from chado_object.utils.feature import (
    feature_symbol_lookup, feature_name_lookup
)
from harvdev_utils.chado_functions import get_or_create, get_cvterm
from chado_object.utils.synonym import synonym_name_details
log = logging.getLogger(__name__)


class ChadoAllele(ChadoObject):
    """Process the Disease Implicated Variation (DIV) Proforma."""

    def __init__(self, params):
        """Initialise the chado object."""
        log.debug('Initializing ChadoDiv object.')

        # Initiate the parent.
        super(ChadoAllele, self).__init__(params)

        self.proforma_start_line_number = params.get('proforma_start_line_number')
        self.set_values = params.get('set_values')
        self.new = False

        # yaml file defines what to do with each field. Follow the light
        self.type_dict = {'feature_relationship': self.load_feature_relationship,
                          'ignore': self.ignore}
        self.proforma_start_line_number = params.get('proforma_start_line_number')

        ###########################################################
        # Values queried later, placed here for reference purposes.
        ############################################################
        self.pub = None
        self.allele = None
        self.gene = None

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
        if not self.allele:  # problem getting gene, lets finish
            return
        # bang c first as this supersedes all things
        if self.bang_c:
            self.bang_c_it()
        if self.bang_d:
            self.bang_d_it()

        for key in self.process_data:
            log.debug("Processing {}".format(self.process_data[key]['data']))
            self.type_dict[self.process_data[key]['type']](key)

        # timestamp = datetime.now().strftime('%c')
        # curated_by_string = 'Curator: %s;Proforma: %s;timelastmodified: %s' % (self.curator_fullname, self.filename_short, timestamp)
        # log.debug('Curator string assembled as:')
        # log.debug('%s' % (curated_by_string))
        return self.allele

    def get_allele(self):
        """Get initial allele and check."""
        self.allele = None
        if self.process_data['GA1g']['data'][FIELD_VALUE] == 'y':  # Should exist already
            organism, plain_name, sgml = synonym_name_details(self.session, self.process_data['GA1a']['data'][FIELD_VALUE])
            try:
                # Alleles are genes.
                self.allele = feature_symbol_lookup(self.session, 'gene', self.process_data['GA1a']['data'][FIELD_VALUE], organism_id=organism.organism_id)
            except NoResultFound:
                message = "Unable to find Allele with symbol {}.".format(self.process_data['GA1a']['data'][FIELD_VALUE])
                self.critical_error(self.process_data['GA1a']['data'], message)
                return

    def ignore(self, key):
        """Ignore."""
        pass

    def load_feature_relationship(self, key):
        """Add Feature Relationship."""
        if not self.has_data(key):
            return

        cv_name = self.process_data[key]['cv']
        cvterm_name = self.process_data[key]['cvterm']
        cvterm = get_cvterm(self.session, cv_name, cvterm_name)
        if not cvterm:
            message = "Unable to find cvterm {} for Cv {}.".format(cvterm_name, cv_name)
            self.critical_error(self.process_data[key]['data'], message)
            return None

        name = self.process_data[key]['data'][FIELD_VALUE]
        obj_feat = feature_name_lookup(self.session, name, type_name='div')
        fr, _ = get_or_create(self.session, FeatureRelationship,
                              subject_id=self.allele.feature_id,
                              object_id=obj_feat.feature_id,
                              type_id=cvterm.cvterm_id)

        frp, _ = get_or_create(self.session, FeatureRelationshipPub,
                               feature_relationship_id=fr.feature_relationship_id,
                               pub_id=self.pub.pub_id)
