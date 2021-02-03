"""
:synopsis: The "Allele" ChadoObject.

:overview: Cut down version of Allele to start with to enable DIV Proforma to work.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>, Ian Longden <ilongden@morgan.harvard.edu>
"""

import logging
import os
import re
from harvdev_utils.chado_functions import (
    get_or_create
)
from chado_object.utils.go import process_DO_line
from chado_object.feature.chado_feature import ChadoFeatureObject
from harvdev_utils.production import (
    Feature, FeatureRelationshipPub, FeatureRelationship,
    FeaturePub, FeatureCvterm, FeatureCvtermprop,
    Featureprop, FeaturepropPub, Featureloc
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
                          'GA90': self.GA90_process,
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
        self.type_name = 'allele'

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

    def get_ga90a(self, key):
        """Get feature defned by GA90 A and K."""
        feature = None
        is_new = False
        feat_type_cvterm = self.get_feat_type_cvterm(key)
        if not feat_type_cvterm:
            self.critical_error(self.process_data[key]['data'][FIELD_VALUE], "Unable to find feature type cvterm.")
            return feature, is_new

        new_allowed = False
        if 'create_new_feat' in self.process_data[key] and self.process_data[key]['create_new_feat']:
            new_allowed = True
        name = self.process_data[key]['data'][FIELD_VALUE]
        if not name.startswith(self.feature.name):
            self.critical_error(self.process_data[key]['data'], "GA90a value '{}' does not start with name of the allele '{}'".format(self.feature.name, name))
            return feature, is_new
        feature, is_new = get_or_create(self.session, Feature, name=name,
                                        type_id=feat_type_cvterm.cvterm_id, uniquename=name,
                                        organism_id=self.feature.organism.organism_id)
        if is_new and not new_allowed:
            message = "Feature of type {} and name {} not found and create_new_feat not set.".format(feat_type_cvterm.name, name)
            self.critical_error(self.process_data[key]['data'], message)
            return None, is_new
        return feature, is_new

    def get_GA90_position(self):
        """Get GA90 position data."""
        position = {'arm': None,
                    'strand': 1}
        key = 'GA90b'
        pattern = r"""
        ^(\S+)        # arm
        :             # chrom separator
        (\d+)         # start pos
        [.]{2}        # double dots
        (\d+)         # end pos
        """
        s_res = re.search(pattern, self.process_data[key]['data'][FIELD_VALUE], re.VERBOSE)

        if s_res:  # matches the pattern above
            arm_name = s_res.group(1)
            position['start'] = int(s_res.group(2))
            position['end'] = int(s_res.group(3))
        else:
            message = r'Incorrect format should be chrom:\d+..\d+'
            self.critical_error(self.process_data[key]['data'], message)
            return position

        # get rel data
        position['release'] = self.process_data['GA90c']['data'][FIELD_VALUE]
        if not position['release']:
            message = "Release required to add "
            self.critical_error(self.process_data['GA90c']['data'], message)
            return position

        # get the strand
        if self.has_data('GA90i'):
            if self.process_data['GA90i']['data'][FIELD_VALUE] == '-':
                position['strand'] = -1

        # convert arm name to feature
        arm_type_id = self.cvterm_query(self.process_data[key]['arm_cv'], self.process_data[key]['arm_cvterm'])
        position['arm'], is_new = get_or_create(self.session, Feature, name=arm_name, type_id=arm_type_id)
        if is_new or not position['arm']:
            message = "Could not get {} feature with cvterm {} and cv {}".\
                format(arm_name, self.process_data[key]['arm_cvterm'], self.process_data[key]['arm_cv'])
            self.critical_error(self.process_data[key]['data'], message)
        return position

    def process_GA90_bci(self, feature, is_new):
        """Process GA90 b, c and i."""
        position = self.get_GA90_position()
        if not position['arm']:
            return
        #  reported_genomic_loc featureprop
        log.debug("position is {}".format(position))
        value = "{}_r{}:{}..{}".format(position['arm'].name, position['release'], position['start'], position['end'])
        key = 'GA90b'
        prop_cv_id = self.cvterm_query(self.process_data[key]['cv'], self.process_data[key]['cvterm'])

        fp, is_new = get_or_create(self.session, Featureprop, feature_id=feature.feature_id,
                                   type_id=prop_cv_id, value=value)
        get_or_create(self.session, FeaturepropPub, featureprop_id=fp.featureprop_id, pub_id=self.pub.pub_id)

        # ADD featureloc
        fl, is_new = get_or_create(self.session, Featureloc,
                                   srcfeature_id=position['arm'].feature_id,
                                   feature_id=feature.feature_id,
                                   locgroup=0)
        fl.fmin = position['start'] - 1  # interbase in chado
        fl.fmax = position['end']
        fl.strand = position['strand']

    def GA90_process(self, key):
        """Create feature if needed and feature relationship.

        Process all G90a-k here.

        Get type from field defined in 'type_field_in' if set
        Allowed to create new feature given in 'create_new_feat'

        """
        if not self.has_data(key):
            return

        cvterm = get_cvterm(self.session, self.process_data[key]['cv'], self.process_data[key]['cvterm'])
        if not cvterm:
            message = "Unable to find cvterm {} for Cv {}.".format(self.process_data[key]['cvterm'], self.process_data[key]['cv'])
            self.critical_error(self.process_data[key]['data'], message)
            return

        feature, is_new = self.get_ga90a(key)
        if not feature:
            return
        fr, _ = get_or_create(self.session, FeatureRelationship,
                              subject_id=feature.feature_id,
                              object_id=self.feature.feature_id,
                              type_id=cvterm.cvterm_id)

        frp, _ = get_or_create(self.session, FeatureRelationshipPub,
                               feature_relationship_id=fr.feature_relationship_id,
                               pub_id=self.pub.pub_id)

        if 'add_unattributed_paper' in self.process_data[key] and self.process_data[key]['add_unattributed_paper']:
            unattrib_pub_id = self.get_unattrib_pub().pub_id
            frp, _ = get_or_create(self.session, FeatureRelationshipPub,
                                   feature_relationship_id=fr.feature_relationship_id,
                                   pub_id=unattrib_pub_id)

        self.process_GA90_bci(feature, is_new)

        # load_featureprop adds props to self.feature but we want to add it to the feature in GA90a
        # so set that and reset afterwards.
        allele = self.feature
        self.feature = feature
        for postfix in "defghj":  # straight forward featureprops
            self.load_featureprop("GA90{}".format(postfix))
        self.feature = allele
