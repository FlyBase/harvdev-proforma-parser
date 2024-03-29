import logging
from chado_object.chado_base import FIELD_VALUE
from harvdev_utils.chado_functions import (get_or_create)
from harvdev_utils.production import (Feature, Featureprop, FeaturepropPub, FeaturePub,
                                      FeatureRelationship, FeatureRelationshipPub, Featureloc)
log = logging.getLogger(__name__)


def get_breakpoint(self, key, new_allowed=True):
    break_name = "{}:bk{}".format(self.feature.name, self.process_data[key]['data'][FIELD_VALUE])
    cvterm_id = self.cvterm_query(self.process_data[key]['feat_cv'],
                                  self.process_data[key]['feat_cvterm'])
    feature, is_new = get_or_create(self.session, Feature,
                                    type_id=cvterm_id,
                                    uniquename=break_name,
                                    organism_id=self.feature.organism.organism_id,
                                    name=break_name)
    if not new_allowed and is_new:
        self.critical_error(self.process_data[key]['data'],
                            f"Bang operation failed!! As NO feature '{break_name}' found.")
        return None

    # add feature pub
    get_or_create(self.session, FeaturePub, feature_id=feature.feature_id, pub_id=self.pub.pub_id)
    return feature


def add_featloc(self, key, position, feature):
    # ADD featureloc
    if position['addfeatureloc']:
        fl, is_new = get_or_create(self.session, Featureloc,
                                   srcfeature_id=position['arm'].feature_id,
                                   feature_id=feature.feature_id,
                                   locgroup=0)
        fl.fmin = position['start'] - 1  # interbase in chado
        fl.fmax = position['end']
        # fl.strand = position['strand'] NO strand info allowed for here.
        # At least for A17 may need to code better later if some allow it.


def add_bk_feat_relationship(self, key, feature):
    cvterm_id = self.cvterm_query(self.process_data[key]['cv'], self.process_data[key]['cvterm'])

    fr, _ = get_or_create(self.session, FeatureRelationship,
                          subject_id=feature.feature_id,
                          object_id=self.feature.feature_id,
                          type_id=cvterm_id)
    frp, _ = get_or_create(self.session, FeatureRelationshipPub,
                           feature_relationship_id=fr.feature_relationship_id,
                           pub_id=self.pub.pub_id)


def add_props(self, key, feature, position):
    for new_key in ['A90h', 'A90j', 'A90b']:
        if new_key == 'A90b':
            value = "{}_r{}:{}..{}".format(position['arm'].name, position['release'], position['start']-1, position['end'])
            log.debug("strand is {}".format(position['strand']))
            if position['strand']:
                message = "strand is set to {} But will be ignored".format(position['strand'])
                self.warning_error(self.process_data[new_key]['data'], message)
        elif new_key in self.process_data:
            value = self.process_data[new_key]['data'][FIELD_VALUE]
        else:
            # error
            pass
        if new_key in self.process_data:
            prop_cv_id = self.cvterm_query(self.process_data[new_key]['prop_cv'],
                                           self.process_data[new_key]['prop_cvterm'])
            fp, is_new = get_or_create(self.session, Featureprop, feature_id=feature.feature_id,
                                       type_id=prop_cv_id, value=value)
            get_or_create(self.session, FeaturepropPub, featureprop_id=fp.featureprop_id, pub_id=self.pub.pub_id)


def process_A90(self, key):
    # create/get break point
    feature = self.get_breakpoint('A90a')

    if not feature:
        return
    # get postional data
    position = self.get_position(key_prefix='A90',
                                 name_key='a',
                                 pos_key='b',
                                 rel_key='c',
                                 strand_key=None,
                                 create=True)
    if not position['arm']:
        return
    log.debug("position is {}".format(position))

    # add feature relationship
    self.add_bk_feat_relationship(key, feature)

    # add featureloc
    self.add_featloc(key, position, feature)

    # add props
    self.add_props(key, feature, position)
