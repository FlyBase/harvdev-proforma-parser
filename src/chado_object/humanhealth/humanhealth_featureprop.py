from harvdev_utils.production import (
    Feature, Cvterm, Cv,
    HumanhealthFeature, HumanhealthFeatureprop
)
import logging
from ..chado_base import FIELD_VALUE
from error.error_tracking import CRITICAL_ERROR
from harvdev_utils.chado_functions import get_or_create

log = logging.getLogger(__name__)


def process_feature(self, params):
    """
    General rountine for adding humanhealth dbxrefs.
    params should contain:-
        name: feature.name
        feature_code: FB(xx), (xx, see process_featureprop for more info)
        tuple: one related tuple to help give better errors
          eature_type: type of feature to find. i.e. gene
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
        log.critical("cvterm {} with cv of {} failed lookup".format(params['cvterm'], params['cvname']))
        return None

    hhfp, _ = get_or_create(self.session, HumanhealthFeatureprop,
                            humanhealth_feature_id=hh_feature.humanhealth_feature_id,
                            type_id=cvterm.cvterm_id)
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
