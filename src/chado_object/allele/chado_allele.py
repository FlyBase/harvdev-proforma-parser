"""
:synopsis: The "Allele" ChadoObject.

:overview: Cut down version of Allele to start with to enable DIV Proforma to work.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>, Ian Longden <ilongden@morgan.harvard.edu>
"""

import logging
import os
import re
from harvdev_utils.chado_functions import (
    get_or_create, get_cvterm, feature_symbol_lookup
)
from chado_object.utils.feature_synonym import fs_add_by_synonym_name_and_type

from chado_object.utils.go import process_DO_line
from chado_object.feature.chado_feature import ChadoFeatureObject
from harvdev_utils.production import (
    Feature, FeatureRelationshipPub, FeatureRelationship,
    FeaturePub, FeatureCvterm, FeatureCvtermprop,
    Featureprop, FeaturepropPub, Featureloc, FeatureSynonym,
    Pub, Synonym
)
from chado_object.chado_base import FIELD_VALUE
from sqlalchemy.orm.exc import NoResultFound
from harvdev_utils.chado_functions import synonym_name_details
from harvdev_utils.production.production import FeatureRelationshipprop, FeatureRelationshippropPub
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
        self.type_dict = {'cvtermprop': self.load_feature_cvtermprop,
                          'cvterm': self.load_feature_cvterm,
                          'DOcvtermprop': self.load_do,
                          'feature_relationship': self.load_feature_relationship,
                          'GA90': self.GA90_process,
                          'GA10_feature_relationship': self.GA10_feat_rel,
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

    def checks(self, references):
        """Check for Allele required data.

        params:
            references: <dict> previous reference proforma

        return:
            True/False depending on wether the checks passed or not
        """
        okay = True
        try:
            self.pub = references['ChadoPub']
        except KeyError:
            message = "Unable to find publication."
            self.critical_error(self.process_data['GA1a']['data'], message)
            okay = False
        try:
            self.gene = references['ChadoGene']
        except KeyError:
            message = "Unable to find gene. Normally Allele should have a gene before."
            self.warning_error(self.process_data['GA1a']['data'], message)
            okay = False

        # cerburus should be dealing with this but it appears not to be.
        # so lets check manually if GA90a does not exist then none of the others should
        if not self.has_data('GA90a'):
            for postfix in 'bcdefghijk':
                postkey = 'GA90{}'.format(postfix)
                if self.has_data(postkey):
                    self.critical_error(self.process_data[postkey]['data'], "Cannot set {} without GA90a".format(postkey))
                    okay = False
        return okay

    def load_content(self, references):
        """Process the data.

        params:
            references: <dict> previous reference proforma objects
        return:
            <Feature object> Allele feature object.
        """
        if not self.checks(references):
            return None

        self.get_allele()
        if not self.feature:  # problem getting allele, lets finish
            return None

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
        """Add props.

        params:
            key: <string> Proforma field key
            do_dict: <dict> dictionary of do cvterms.
        """
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
        """Load DO.

        params:
            key: <string> proforma field key.
        """
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

    def get_GA90a(self, key):
        """Get feature defned by GA90 A and K.

        key: <string> the field name i.e here GA90a

        return:
           feature: <feature object> feature of type GA90k, name GA90a
           is_new: <bool> Wether the feature is noe or not.
        """
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
                    'strand': 1,
                    'addfeatureloc': True}
        # check with BEV can we have GA90a without a position?

        key = 'GA90b'

        if not self.has_data(key):
            # posible error message if not allowed without this.
            message = r'MUST have a position GA90 b and c'
            self.critical_error(self.process_data['GA90a']['data'], message)
            return position

        pattern = r"""
        ^\s*          # possible spaces
        (\S+)         # arm
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
            pattern = r"""
            ^\s*          # possible spaces
            (\S+)         # arm
            :             # chrom separator
            (\d+)         # start pos
            /s+           # possible spaces
            $             # end
            """
            s_res = re.search(pattern, self.process_data[key]['data'][FIELD_VALUE], re.VERBOSE)
            if s_res:  # matches the pattern above
                arm_name = s_res.group(1)
                position['start'] = int(s_res.group(2))
                position['end'] = position['start']
            else:
                message = r'Incorrect format should be chrom:\d+..\d+'
                self.critical_error(self.process_data[key]['data'], message)
                return position

        # get rel data
        # If release specified and not equal to current assembly then
        # flag for the featurelovc to not be created.
        default_release = os.getenv('ASSEMBLY_RELEASE', '6')
        if 'GA90c' in self.process_data:
            position['release'] = self.process_data['GA90c']['data'][FIELD_VALUE]
        if 'release' not in position:
            position['release'] = default_release
        else:
            if position['release'] != default_release:
                self.warning_error(self.process_data['GA90c']['data'], "Release {} will not display in Location".format(position['release']))
                position['addfeatureloc'] = False

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
        """Process GA90 b, c and i.

        params:
            feature: <Feature object> feature defined by GA90a
            is_new: <bool> wether this was new or not.
        """
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
        if position['addfeatureloc']:
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

        params:
            key: <string> proforma field key. (here it will be GA90a)
        """
        if not self.has_data(key):
            return

        cvterm = get_cvterm(self.session, self.process_data[key]['cv'], self.process_data[key]['cvterm'])
        if not cvterm:
            message = "Unable to find cvterm {} for Cv {}.".format(self.process_data[key]['cvterm'], self.process_data[key]['cv'])
            self.critical_error(self.process_data[key]['data'], message)
            return

        feature, is_new = self.get_GA90a(key)
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
        # So for each of the featureprop fields GA90d -> GA90j
        # call the load_featureprop function.
        allele = self.feature
        self.feature = feature
        for postfix in "defghj":  # straight forward featureprops
            self.load_featureprop("GA90{}".format(postfix))
        self.feature = allele

    def get_GA10_cvterms(self, key):
        """Get cvterms needed for G10."""
        cvterms = {}

        cvterms['rel_cvterm'] = get_cvterm(self.session, self.process_data[key]['cv'], self.process_data[key]['cvterm'])
        if not cvterms['rel_cvterm']:
            message = "Unable to find cvterm '{}' for Cv '{}'.".format(self.process_data[key]['cvterm'], self.process_data[key]['cv'])
            self.critical_error(self.process_data[key]['data'], message)
            return None

        cvterms['prop_cvterm'] = get_cvterm(self.session, self.process_data[key]['prop_cv'], self.process_data[key]['prop_cvterm'])
        if not cvterms['prop_cvterm']:
            message = "Unable to find cvterm '{}' for Cv '{}'.".format(self.process_data[key]['prop_cvterm'], self.process_data[key]['prop_cv'])
            self.critical_error(self.process_data[key]['data'], message)
            return None

        cvterms['tp_cvterm'] = get_cvterm(self.session, self.process_data[key]['tp_cv'], self.process_data[key]['tp_cvterm'])
        if not cvterms['tp_cvterm']:
            message = "Unable to find cvterm '{}' for Cv '{}'.".format(self.process_data[key]['tp_cvterm'], self.process_data[key]['tp_cv'])
            self.critical_error(self.process_data[key]['data'], message)
            return None

        cvterms['feat_type'] = get_cvterm(self.session, 'SO', self.process_data[key]['feat_type'])
        if not cvterms['feat_type']:
            message = "Unable to find cvterm '{}' for Cv 'SO'.".format(self.process_data[key]['cvterm'])
            self.critical_error(self.process_data[key]['data'], message)
            return None

        cvterms['syn_type'] = get_cvterm(self.session, self.process_data[key]['syn_cv'], self.process_data[key]['syn_cvterm'])
        if not cvterms['syn_type']:
            message = "Unable to find cvterm '{}' for Cv '{}'.".format(self.process_data[key]['syn_cvterm'], self.process_data[key]['syn_cv'])
            self.critical_error(self.process_data[key]['data'], message)
            return None

        return cvterms

    def get_feature(self, key, item, cvterms):
        """Get feature, may neeed to create it."""
        name2code = {'transposable_element_insertion_site': 'ti',
                     'transgenic_transposable_element': 'tp'}
        is_new_feature = False
        name = item[FIELD_VALUE]
        fields = re.search(r"NEW:(\S+)", name)
        if fields:
            if fields.group(1):
                name = fields.group(1)
                is_new_feature = True

        organism, plain_name, sgml = synonym_name_details(self.session, name)
        uniquename = 'FB{}:temp_0'.format(name2code[self.process_data[key]['feat_type']])
        feature, is_new = get_or_create(self.session, Feature, name=name,
                                        type_id=cvterms['feat_type'].cvterm_id, uniquename=uniquename,
                                        organism_id=organism.organism_id)
        if is_new_feature != is_new:
            if is_new_feature:
                message = ""
            else:
                message = ""
            self.critical_error(self.process_data[key]['data'], message)
            return None

        if 'synonym_field' in self.process_data[key] and self.has_data(self.process_data[key]['synonym_field']):
            syn_key = self.process_data[key]['synonym_field']
            if self.has_data(syn_key):
                for syn_data in self.process_data[syn_key]['data']:
                    syn_name = syn_data[FIELD_VALUE]
                    organism, syn_plain_name, syn_sgml = synonym_name_details(self.session, syn_name)
                    fs_add_by_synonym_name_and_type(self.session, feature.feature_id,
                                                    syn_plain_name, self.process_data[syn_key]['cv'],
                                                    self.process_data[syn_key]['cvterm'], self.pub.pub_id,
                                                    synonym_sgml=syn_sgml, is_current=self.process_data[syn_key]['is_current'], is_internal=False)

        # After other synoinyms in case we it is duplicsated as a synonym here and we want to keep it current
        if is_new_feature:
            syn_pub = self.session.query(Pub).filter(Pub.uniquename == self.process_data[key]['syn_pub']).one_or_none()
            if not syn_pub:
                self.critical_error(self.process_data[key]['data'], 'Pub {} does not exist in the database.'.format(self.process_data[key]['syn_pub']))
                return

            synonym, _ = get_or_create(self.session, Synonym, type_id=cvterms['syn_type'].cvterm_id, name=plain_name, synonym_sgml=sgml)

            fs, _ = get_or_create(self.session, FeatureSynonym, feature_id=feature.feature_id, synonym_id=synonym.synonym_id,
                                  pub_id=syn_pub.pub_id)
            fs.is_current = True
            fs.is_internal = False
            log.debug("BOB: {} ".format(feature))
            log.debug("BOB: fs= {}".format(fs))
            log.debug("BOB: syn {}".format(fs.synonym))
        else:
            log.debug("BOB: NOT NEW")
        return feature

    def tp_part_process(self, key, item, cvterms, ti_object):
        """Process tp and allele part of name."""
        pattern = r"""
                    NEW:* # Ignore NEW: at the start if it has it.
                    (\S+    # Pre '{' part of tp name
                    [{]+    # tp part with '{'
                    \S+     # Non white space name bit of tp
                    [}]+)   # tp ends with  '}'
                    (\S+)   # Non white space allele name
                    """
        fields = re.search(pattern, item[FIELD_VALUE], re.VERBOSE)
        if fields:
            if fields.group(1):
                tp_part_name = fields.group(1)
                allele_part_name = fields.group(2)
        else:
            self.warning_error(item, "format error ti does not start {...}")
            return

        # Does the allele part have the same name as the allele
        try:
            allele_part = feature_symbol_lookup(self.session, None, allele_part_name)
            if self.feature.feature_id != allele_part.feature_id:
                message = "Allele part of name '{}' does NOT match the allele {} given in the allele proforma".\
                    format(allele_part_name, self.feature.name)
                self.warning_error(item, message)
        except NoResultFound:
            self.warning_error(item, "Could not find Allele '{}' for the allele part of the ti")

        try:
            tp_part = feature_symbol_lookup(self.session, None, tp_part_name)
        except NoResultFound:
            self.warning_error(item, "Could not find tp '{}' for the tp part of the ti".format(tp_part_name))
            return

        # Create/get tp ti relationship
        tp_ti, _ = get_or_create(self.session, FeatureRelationship,
                                 subject_id=ti_object.feature_id,
                                 object_id=tp_part.feature_id,
                                 type_id=cvterms['tp_cvterm'].cvterm_id)

        frp, _ = get_or_create(self.session, FeatureRelationshipPub,
                               feature_relationship_id=tp_ti.feature_relationship_id,
                               pub_id=self.pub.pub_id)

    def GA10_feat_rel(self, key):
        """Create feature relationship.

        Check if 'NEW:' , if so create before continuing.
        """
        if not self.has_data(key):
            return
        cvterms = self.get_GA10_cvterms(key)
        if not cvterms:
            return

        if type(self.process_data[key]['data']) is list:
            items = self.process_data[key]['data']
        else:
            items = [self.process_data[key]['data']]

        for item in items:
            ti_feature = self.get_feature(key, item, cvterms)
            if not ti_feature:
                continue

            self.tp_part_process(key, item, cvterms, ti_feature)

            # Add feat relationship for new_feat to allele (self.feature)
            ti_allele, _ = get_or_create(self.session, FeatureRelationship,
                                         subject_id=self.feature.feature_id,
                                         object_id=ti_feature.feature_id,
                                         type_id=cvterms['rel_cvterm'].cvterm_id)

            frp, _ = get_or_create(self.session, FeatureRelationshipPub,
                                   feature_relationship_id=ti_allele.feature_relationship_id,
                                   pub_id=self.pub.pub_id)

            # add feature relationshipproppub to allele
            frprop, _ = get_or_create(self.session, FeatureRelationshipprop,
                                      feature_relationship_id=ti_allele.feature_relationship_id,
                                      value=self.process_data[key]['prop_value'],
                                      type_id=cvterms['prop_cvterm'].cvterm_id)
            frp_proppub, _ = get_or_create(self.session, FeatureRelationshippropPub,
                                           feature_relationshipprop_id=frprop.feature_relationshipprop_id,
                                           pub_id=self.pub.pub_id)

            # Add feat relationship for new_feat to gene
            tp_gene, _ = get_or_create(self.session, FeatureRelationship,
                                       subject_id=self.gene.feature_id,
                                       object_id=ti_feature.feature_id,
                                       type_id=cvterms['rel_cvterm'].cvterm_id)

            frp, _ = get_or_create(self.session, FeatureRelationshipPub,
                                   feature_relationship_id=tp_gene.feature_relationship_id,
                                   pub_id=self.pub.pub_id)
