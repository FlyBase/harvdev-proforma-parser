from harvdev_utils.production import (
    Feature, Cvterm, Cv,
    HumanhealthFeature, HumanhealthFeatureprop
)
import logging
from ..chado_base import FIELD_VALUE, SET_BANG
from error.error_tracking import CRITICAL_ERROR
from harvdev_utils.chado_functions import get_or_create

log = logging.getLogger(__name__)


def process_feature(self, params):
    """
    General rountine for adding humanhealth features.
    params should contain:-
        name: feature.name
        feature_code: FB(xx), (xx, see process_featureprop for more info)
        tuple: one related tuple to help give better errors
    """

    feature = self.session.query(Feature).\
        filter(Feature.name == params['name'],
               Feature.uniquename.like("FB{}%".format(params['feature_code']))).one_or_none()
    if not feature:
        error_message = "Name {} not found in feature table with unique name starting with FB{}".\
            format(params['name'], params['feature_code'])
        self.error_track(params['tuple'], error_message, CRITICAL_ERROR)
        return None
    hh_feature, _ = get_or_create(self.session, HumanhealthFeature,
                                  feature_id=feature.feature_id,
                                  pub_id=self.pub.pub_id,
                                  humanhealth_id=self.humanhealth.humanhealth_id)
    log.debug("Created hh feat {} id is {}".format(feature.name, hh_feature.humanhealth_feature_id))
    return hh_feature


def process_featureprop(self, params):
    """
         General rountine for adding humanhealth dbxrefs and their props
         params should contain:-
         name:         name of the feature (feature.name)
         feature_code: FBxx, pass the xx here.
         cvname:       cv name for prop
         cvterm:       cvterm name for prop
         tuple:        one related tuple to help give better errors

         NOTE: feature code needed as names are not unique i.e.
         select f.uniquename, f.name from feature f where f.name = E'Hsap\\PTEN';
            uniquename   |   name
         ----------------+-----------
          FBgn0028728    | Hsap\\PTEN
          FBog0000209256 | Hsap\\PTEN

         Do i also need to look up synonyms???
    """
    hh_feature = self.process_feature(params)

    if not hh_feature:
        return None

    cvterm = self.session.query(Cvterm).join(Cv).\
        filter(Cv.name == params['cvname'],
               Cvterm.name == params['cvterm']).\
        one_or_none()
    if not cvterm:
        error_message = "cvterm {} with cv of {} failed lookup".format(params['cvterm'], params['cvname'])
        self.error_track(params['tuple'], error_message, CRITICAL_ERROR)
        return None

    hhfp, _ = get_or_create(self.session, HumanhealthFeatureprop,
                            humanhealth_feature_id=hh_feature.humanhealth_feature_id,
                            type_id=cvterm.cvterm_id)
    log.debug("Created hh_feat_prop hh_feat_id is {}".format(hhfp, hh_feature.humanhealth_feature_id))

    if 'propval' in params:
        hhfp.value = params['propval']
    return hhfp


def load_featureprop(self, key):
    """
    load the hh_feature and hh_featureprop
    """
    params = {'cvterm': self.process_data[key]['cvterm'],
              'cvname': self.process_data[key]['cv'],
              'feature_code': self.process_data[key]['feature_code']}
    # can be a list or single, so make them all a list to save code dupliction
    if type(self.process_data[key]['data']) is not list:
        data_list = []
        data_list.append(self.process_data[key]['data'])
    else:
        data_list = self.process_data[key]['data']

    for item in data_list:
        log.debug("{}: {} {}".format(key, item, type(item)))
        params['tuple'] = item
        params['name'] = item[FIELD_VALUE]
        self.process_featureprop(params)


def process_featurepropset(self, set_key, data_set):  # noqa: C901
    """
    8a featureprop, 8c different featureprop but to the feature specified in 8a.
    8d dissociate 8a
    """

    valid_key = None  # need a valid key incase something is wrong to report line number etc
    for key in data_set.keys():
        if type(data_set[key]) is list:
            if data_set[key][0][FIELD_VALUE]:
                valid_key = 1
        elif data_set[key][FIELD_VALUE]:
            valid_key = key
    if not valid_key:  # Whole thing is blank so ignore. This is okay
        return

    feature_key = set_key + 'a'
    params = {'cvterm': self.process_data[set_key]['a_cvterm'],
              'cvname': self.process_data[set_key]['a_cv'],
              'name': data_set[feature_key][FIELD_VALUE],
              'tuple': data_set[feature_key],
              'feature_code': self.process_data[set_key]['feature_code']}

    dis_key = set_key + 'd'
    if dis_key in data_set and data_set[dis_key][FIELD_VALUE].upper() == 'Y':
        self.bangd_featureprop(params)
        return

    self.process_featureprop(params)

    orth_com_key = set_key + 'c'
    params['cvterm'] = self.process_data[set_key]['c_cvterm']
    params['cvname'] = self.process_data[set_key]['c_cv']

    if orth_com_key in data_set:
        for item in data_set[orth_com_key]:  # List of comments/propvals
            if item[SET_BANG]:
                params['bang_type'] = item[SET_BANG]
                params['propval'] = item[FIELD_VALUE]
                self.delete_featureprop_only(params)
            elif item[FIELD_VALUE] != '':
                params['propval'] = item[FIELD_VALUE]
                self.process_featureprop(params)


def process_hh8(self, set_key):
    """
    8a featureprop, 8c different featureprop but to the feature specified in 8a.
    8d dissociate 8a
    """

    for data_set in self.set_values[set_key]:
        self.process_featurepropset(set_key, data_set)


#############################################
# Deletion. bangc/bangd routines
#############################################


def delete_featureprop_only(self, params):
    """
    Delete the prop only and not the hh_feature
    """
    # Get feature
    feature = self.session.query(Feature).\
        filter(Feature.name == params['name'],
               Feature.uniquename.like("FB{}%".format(params['feature_code']))).one_or_none()
    if not feature:
        error_message = "Name {} not found in feature table with unique name starting with FB{}".\
            format(params['name'], params['feature_code'])
        self.error_track(params['tuple'], error_message, CRITICAL_ERROR)
        return None

    # Get humanhealth_feature
    hhf = self.session.query(HumanhealthFeature).\
        filter(HumanhealthFeature.feature_id == feature.feature_id,
               HumanhealthFeature.humanhealth_id == self.humanhealth.humanhealth_id).one_or_none()
    if not hhf:
        error_message = "No relationship between {} and {} so cannot bang{} it.".\
            format(params['name'], self.humanhealth.name, params['bang_type'])
        self.error_track(params['tuple'], error_message, CRITICAL_ERROR)
        return None

    if params['bang_type'] == 'd':  # delete specific prop value
        hhfp = self.session.query(HumanhealthFeatureprop).\
                   filter(HumanhealthFeatureprop.humanhealth_feature_id == hhf.humanhealth_feature_id,
                          HumanhealthFeatureprop.value == params['propval']).one_or_none()
        if not hhfp:
            error_message = "No relationship between {} and {} with comment '{}' so cannot bangd it.".\
                format(params['name'], self.humanhealth.name, params['propval'])
            self.error_track(params['tuple'], error_message, CRITICAL_ERROR)
            return None
        self.session.delete(hhfp)
    else:  # delete all props and if we have a new one add it.
        log.debug("Removing hh feat prop for {}".format(feature.name))
        log.debug("params are {}".format(params))
        self.session.query(HumanhealthFeatureprop).\
            filter(HumanhealthFeatureprop.humanhealth_feature_id == hhf.humanhealth_feature_id).delete()
        if 'propval' in params and params['propval'] != '':
            self.process_featureprop(params)


def delete_featureprop(self, key, bangc):
    params = {'cvterm': self.process_data[key]['cvterm'],
              'cvname': self.process_data[key]['cv'],
              'feature_code': self.process_data[key]['feature_code']}

    if type(self.process_data[key]['data']) is not list:
        data_list = []
        data_list.append(self.process_data[key]['data'])
    else:
        data_list = self.process_data[key]['data']

    for item in data_list:
        log.debug("{}: {} {}".format(key, item, type(item)))
        params['tuple'] = item
        params['name'] = item[FIELD_VALUE]
        if bangc:
            self.bangc_featureprop(params)
        else:
            self.bangd_featureprop(params)
            self.process_data[key]['data'] = None


def bangc_featureprop(self, params):
    """
    Delete ALL hh_features for specific cvterm and hh.
    """
    cvterm = self.session.query(Cvterm).join(Cv).\
        filter(Cv.name == params['cvname'],
               Cvterm.name == params['cvterm']).\
        one_or_none()
    if not cvterm:
        error_message = "cvterm {} with cv of {} failed lookup".format(params['cvterm'], params['cvname'])
        self.error_track(params['tuple'], error_message, CRITICAL_ERROR)
        return None
    self.session.query(HumanhealthFeature).\
        filter(HumanhealthFeatureprop.type_id == cvterm.cvterm_id,
               HumanhealthFeature.humanhealth_id == self.humanhealth.humanhealth_id).delete()


def bangd_featureprop(self, params):
    cvterm = self.session.query(Cvterm).join(Cv).\
        filter(Cv.name == params['cvname'],
               Cvterm.name == params['cvterm']).\
        one_or_none()
    if not cvterm:
        error_message = "cvterm {} with cv of {} failed lookup".format(params['cvterm'], params['cvname'])
        self.error_track(params['tuple'], error_message, CRITICAL_ERROR)
        return None

    feature = self.session.query(Feature).\
        filter(Feature.name == params['name'],
               Feature.uniquename.like("FB{}%".format(params['feature_code']))).one_or_none()
    if not feature:
        error_message = "Name {} not found in feature table with unique name starting with FB{}".\
            format(params['name'], params['feature_code'])
        self.error_track(params['tuple'], error_message, CRITICAL_ERROR)
        return None

    hh_feats = self.session.query(HumanhealthFeature).\
        join(HumanhealthFeatureprop, HumanhealthFeature.humanhealth_feature_id == HumanhealthFeatureprop.humanhealth_feature_id).\
        filter(HumanhealthFeatureprop.type_id == cvterm.cvterm_id,
               HumanhealthFeature.humanhealth_id == self.humanhealth.humanhealth_id,
               HumanhealthFeature.feature_id == feature.feature_id)
    for hh_feat in hh_feats:
        self.session.delete(hh_feat)
