import logging
from chado_object.chado_base import FIELD_VALUE
from harvdev_utils.chado_functions import (get_or_create)
from harvdev_utils.production import (Feature, Featureprop, FeaturepropPub, FeaturePub,
                                      FeatureRelationship, FeatureRelationshipPub, Featureloc)
log = logging.getLogger(__name__)


def get_breakpoint(self, key):
    break_name = "{}:bk{}".format(self.feature.name, self.process_data[key]['data'][FIELD_VALUE])
    cvterm_id = self.cvterm_query(self.process_data[key]['feat_cv'],
                                  self.process_data[key]['feat_cvterm'])
    feature, _ = get_or_create(self.session, Feature,
                               type_id=cvterm_id,
                               uniquename=break_name,
                               organism_id=self.feature.organism.organism_id,
                               name=break_name)
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
        fl.strand = position['strand']


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
    for new_key in ['A90h', 'A90j', 'A90c']:
        if new_key == 'A90c':
            value = "{}_r{}:{}..{}".format(position['arm'].name, position['release'], position['start']-1, position['end'])
        elif new_key in self.process_data:
            value = self.process_data[new_key]['data'][FIELD_VALUE]
        else:
            # error
            pass
        prop_cv_id = self.cvterm_query(self.process_data[new_key]['prop_cv'],
                                       self.process_data[new_key]['prop_cvterm'])
        fp, is_new = get_or_create(self.session, Featureprop, feature_id=feature.feature_id,
                                   type_id=prop_cv_id, value=value)
        get_or_create(self.session, FeaturepropPub, featureprop_id=fp.featureprop_id, pub_id=self.pub.pub_id)


def process_A90(self, key):
    # create/get break point
    feature = self.get_breakpoint('A90a')

    # get postional data
    position = self.get_position(key_prefix='A90',
                                 name_key='a',
                                 pos_key='b',
                                 rel_key='c',
                                 strand_key=None,
                                 create=True)
    if 'arm' not in position:
        return
    log.debug("position is {}".format(position))

    # add feature relationship
    self.add_bk_feat_relationship(key, feature)

    # add featureloc
    self.add_featloc(key, position, feature)

    # add props
    self.add_props(key, feature, position)
