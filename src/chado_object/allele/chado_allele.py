"""
:synopsis: The "Allele" ChadoObject.

:overview: Cut down version of Allele to start with to enable DIV Proforma to work.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>
               Ian Longden <ianlongden@morgan.harvard.edu>
"""

import logging
import os

# from sqlalchemy.sql.functions import ReturnTypeFromArgs
from harvdev_utils.chado_functions import (
    get_or_create, get_cvterm
)
from harvdev_utils.char_conversions import sub_sup_to_sgml, sgml_to_unicode

from chado_object.utils.go import process_DO_line
from chado_object.feature.chado_feature import ChadoFeatureObject
from harvdev_utils.production import (
    Feature, FeatureRelationshipPub, FeatureRelationship,
    FeaturePub, FeatureCvterm, FeatureCvtermprop,
    Featureprop, FeaturepropPub, Featureloc
)
from chado_object.chado_base import FIELD_VALUE
from sqlalchemy.orm.exc import NoResultFound

from harvdev_utils.production.production import Cvterm, FeatureSynonym, Synonym
log = logging.getLogger(__name__)


class ChadoAllele(ChadoFeatureObject):
    """Process the Disease Implicated Variation (DIV) Proforma."""

    from chado_object.allele.GA10 import (
        GA10_feat_rel, process_GA10a, process_GA10g, get_GA10_cvterms,
        tp_part_process, get_feature, synonyms_GA10
    )

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
                          'merge': self.merge,
                          'cvterm': self.load_feature_cvterm,
                          'DOcvtermprop': self.load_do,
                          'feature_relationship': self.load_feature_relationship,
                          'GA90': self.GA90_process,
                          'GA10_feature_relationship': self.GA10_feat_rel,
                          'featureprop': self.load_featureprop,
                          'GA12a_featureprop': self.GA12a_featureprop,
                          'synonym': self.load_synonym,
                          'ignore': self.ignore,
                          'libraryfeatureprop': self.load_lfp,
                          'rename': self.rename,
                          'dis_pub': self.dis_pub,
                          'make_obsolete': self.make_obsolete,
                          'pheno_cvterm': self.not_done,
                          'notdone': self.not_done}
        self.delete_dict = {'featureprop': self.delete_featureprop,
                            'GA12a_featureprop': self.GA12a_featureprop_delete,
                            'synonym': self.delete_synonym,
                            'ignore': self.ignore_bang}

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

    def not_done(self, key):
        # Remove once GA35 done.
        # Will be done once transposon have been sorted out.
        if type(self.process_data[key]['data']) is list:
            self.critical_error(self.process_data[key]['data'][0], "Not programmed yet")
        else:
            self.critical_error(self.process_data[key]['data'], "Not programmed yet")

    def checks(self, references):  # noqa
        """Check for Allele required data.

        Args:
            references: <dict> previous reference proforma

        return:
            True/False depending on wether the checks passed or not
        """
        # warning for failed symbol in @@ lookups
        self.at_symbol_check_all()

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
            if not self.has_data('GA32b'):  # Diss pub does not need gene
                message = "Unable to find gene. Normally Allele should have a gene before."
                self.warning_error(self.process_data['GA1a']['data'], message)
                okay = False

        # cerberus not good at testing for values just fields so we need to do some extra checks here.
        if self.has_data('GA2c'):
            if not self.has_data('GA2a'):
                message = "When GA2c is set then GA2a must be set aswell"
                self.critical_error(self.process_data['GA2c']['data'], message)
                okay = False

        # cerburus should be dealing with this but it appears not to be.
        # so lets check manually if GA90a does not exist then none of the others should
        if 'GA90k' in self.bang_c:
            return okay
        if not self.has_data('GA90a'):
            for postfix in 'bcdefghijk':
                postkey = 'GA90{}'.format(postfix)
                if self.has_data(postkey):
                    self.critical_error(self.process_data[postkey]['data'], "Cannot set {} without GA90a".format(postkey))
                    okay = False

        # also of GA90 a is set then b and c are required.
        if self.has_data('GA90a'):
            for postfix in 'bc':
                postkey = 'GA90{}'.format(postfix)
                if not self.has_data(postkey):
                    self.critical_error(self.process_data['GA90a']['data'], "Required to set {} with GA90a specified".format(postkey))
                    okay = False
        return okay

    def load_content(self, references):
        """Process the data.

        Args:
            references: <dict> previous reference proforma objects
        return:
            <Feature object> Allele feature object.
        """
        if not self.checks(references):
            return None

        self.get_allele()
        if not self.feature:  # problem getting allele, lets finish
            return None

        # feature pub if not dissociate pub
        if not self.has_data('GA32b'):
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

    def merge(self, key):
        """Merge alleles."""
        log.debug(self.feature)
        # change the pub
        self.feature.pub_id = self.pub.pub_id

        alleles = self.get_merge_features(key, feat_type='allele')
        for allele in alleles:
            log.debug("Allele to be merged is {}".format(allele))
            allele.is_obsolete = True
            # Transfer synonyms
            self.transfer_synonyms(allele)
            # Transfer cvterms
            self.transfer_cvterms(allele)
            # Transfer dbxrefs
            self.transfer_dbxrefs(allele)
            # transfer relationships
            self.transfer_feature_relationships(allele)
            # transfer papers
            self.transfer_papers(allele)
            # transfer featureprop and featureproppubs
            self.transfer_props(allele)

    def get_allele(self):
        """Get initial allele and check."""
        # NOTE: new 'SO' will be 'allele' when it come in
        self.load_feature(feature_type='allele')

    def ignore(self, key):
        """Ignore."""
        pass

    def ignore_bang(self, key, bangc):
        """Ignore."""
        pass

    def add_cvtermprops(self, key, do_dict):
        """Add props.

        Args:
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

            # Get max rank 0 if there are none.
            rank = 0
            fcps = self.session.query(FeatureCvtermprop).\
                filter(FeatureCvtermprop.feature_cvterm_id == feat_cvt.feature_cvterm_id,
                       FeatureCvtermprop.type_id == cvtermprop.cvterm_id)
            for fcp in fcps:
                if fcp.rank > rank:
                    rank = fcp.rank
            rank += 1
            fcp = FeatureCvtermprop(feature_cvterm_id=feat_cvt.feature_cvterm_id,
                                    value=do_dict[prop_key],
                                    rank=rank,
                                    type_id=cvtermprop.cvterm_id)
            self.session.add(fcp)

    def rename(self, key):
        """Rename 'fullname' synonym.

        Lookup fullname synonym foir the alelle ansd make sure one of them is the one
        given in GA2c this should be the current 'fullname' synonym before this step.
        If it is not then lets give an error.
        If it is then set all 'fullname's to be is_current False.
        Add new synonym given by GA2a and make is is_current True
        with the 'unattributed' pub.
        """

        # Lets look it up and set to is_current False if found
        syn_sgml = sgml_to_unicode(sub_sup_to_sgml((self.process_data[key]['data'][FIELD_VALUE])))
        fss = self.session.query(FeatureSynonym).\
            join(Synonym, Synonym.synonym_id == FeatureSynonym.synonym_id).\
            join(Cvterm, Synonym.type_id == Cvterm.cvterm_id).\
            filter(FeatureSynonym.feature_id == self.feature.feature_id,
                   Cvterm.name == 'fullname',
                   Synonym.synonym_sgml == syn_sgml)
        found = False
        for fs in fss:
            if fs.is_current:
                fs.is_current = False
                found = True
        if not found:
            mess = "{} is not a fullname synonym for {}, so cannot use it to rename".\
                format(self.process_data[key]['data'][FIELD_VALUE], self.feature.name)
            self.critical_error(self.process_data[key]['data'], mess)
            return

        # Use GA2a field value and pass to synonym processing
        self.process_data[key]['data'] = (key, self.process_data['GA2a']['data'][FIELD_VALUE],
                                          self.process_data[key]['data'][2], False)
        self.load_synonym(key, unattrib=True)

    def load_do(self, key):
        """Load DO.

        Args:
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

        Args:
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

        if 'GA90k' in self.bang_c:
            try:
                f = self.session.query(Feature).filter(Feature.uniquename == self.process_data[key]['data'][FIELD_VALUE]).one()
            except NoResultFound:
                message = "Feature name {} not found.".format(self.process_data[key]['data'][FIELD_VALUE])
                self.critical_error(self.process_data['GA90k']['data'], message)
            f.type_id = feat_type_cvterm.cvterm_id
            return f, False
        feature, is_new = get_or_create(self.session, Feature, name=name,
                                        type_id=feat_type_cvterm.cvterm_id, uniquename=name,
                                        organism_id=self.feature.organism.organism_id)

        if is_new and not new_allowed:
            message = "Feature of type {} and name {} not found and create_new_feat not set.".format(feat_type_cvterm.name, name)
            self.critical_error(self.process_data[key]['data'], message)
            return None, is_new

        # add feature pub
        get_or_create(self.session, FeaturePub, feature_id=feature.feature_id, pub_id=self.pub.pub_id)

        return feature, is_new

    def process_GA90_bci(self, feature, is_new):
        """Process GA90 b, c and i.

        Args:
            feature: <Feature object> feature defined by GA90a
            is_new: <bool> wether this was new or not.
        """
        # position = self.get_GA90_position()
        position = self.get_position(key_prefix='GA90', name_key='a', pos_key='b', rel_key='c', strand_key='i', create=True)
        if not position['arm']:
            return
        if not position['strand']:
            position['strand'] = 0
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

        Args:
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
        if is_new:
            if not self.has_data('GA90b'):
                mess = "GA90b must be defined for new Lesions"
                self.critical_error(self.process_data[key]['data'], mess)
                return
        # bang as not new, so there may not be any new location data
        elif not (self.has_data('GA90b') and self.has_data('GA90c')):
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

    def GA12a_featureprop(self, key):
        """GA12a add featureprop."""
        if not self.has_data(key):
            return
        for item in self.process_data[key]['data']:
            cvterm = None
            for idx, allowed in enumerate(self.process_data[key]['allowed_starts']):
                if (item[FIELD_VALUE].startswith(allowed)):
                    cvterm_name = self.process_data[key]['allowed_cvterms'][idx]
                    cvterm = get_cvterm(self.session, self.process_data[key]['cv'], cvterm_name)
            if not cvterm:
                self.critical_error("Must start with one of {}".format(self.process_data[key]['allowed_starts']))
                continue
            fp, is_new = get_or_create(self.session, Featureprop, feature_id=self.feature.feature_id,
                                       type_id=cvterm.cvterm_id, value=item[FIELD_VALUE])
            fpp, is_new = get_or_create(self.session, FeaturepropPub, featureprop_id=fp.featureprop_id, pub_id=self.pub.pub_id)

    def GA12a_featureprop_delete(self, key, bangc=False):
        """Delete GA12 feature props."""
        for name in self.process_data[key]['allowed_cvterms']:
            self.process_data[key]['cvterm'] = name
            self.delete_featureprop(key, bangc=bangc)
