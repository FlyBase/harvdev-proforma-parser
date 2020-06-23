"""
:synopsis: The Base Feature Object.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>, Ian Longden <ilongden@morgan.harvard.edu>
"""
from chado_object.chado_base import ChadoObject, FIELD_VALUE
from harvdev_utils.chado_functions import get_or_create, get_cvterm
from chado_object.utils.feature_synonym import fs_add_by_synonym_name_and_type

from chado_object.utils.feature_synonym import fs_remove_current_symbol
from harvdev_utils.char_conversions import sgml_to_plain_text

from harvdev_utils.production import (
    FeatureRelationship, FeatureRelationshipPub, Featureprop,
    FeaturepropPub, FeatureCvterm, FeatureCvtermprop,
    Pub
)
from harvdev_utils.chado_functions import (
    feature_name_lookup
)
from datetime import datetime
import logging
log = logging.getLogger(__name__)


class ChadoFeatureObject(ChadoObject):
    """ChadoFeature object."""

    from chado_object.feature.feature_chado_check import (
        check_only_certain_fields_allowed,
        check_at_symbols_exist, check_bad_starts
    )

    def __init__(self, params):
        """Initialise the ChadoFeature Object."""
        log.debug('Initializing ChadoFeatureObject.')

        # Initiate the parent.
        super(ChadoFeatureObject, self).__init__(params)
        self.feature = None

    def get_pub_id_for_synonym(self, key):
        """Get pub_id for a synonym."""
        if self.has_data('G1f'):
            pub, _ = get_or_create(self.session, Pub, uniquename='unattributed')
            return pub.pub_id
        if self.has_data('CH1f'):
            if 'pub' in self.process_data[key] and self.process_data[key]['pub'] == 'current':
                pub_id = self.pub.pub_id
            else:
                # is this chebi or pubchem
                pub_id = self.get_external_chemical_pub_id(key)
            return pub_id
        return self.pub.pub_id

    def load_synonym(self, key):
        """Load Synonym.

        yml options:
           cv:
           cvterm:
           is_current:
           remove_old: <optional> defaults to False
        NOTE:
          If is_current set to True and cvterm is symbol thensgml to plaintext is done.
        """
        cv_name = self.process_data[key]['cv']
        cvterm_name = self.process_data[key]['cvterm']
        is_current = self.process_data[key]['is_current']
        pub_id = self.get_pub_id_for_synonym(key)

        # remove the current symbol if is_current is set and yaml says remove old is_current
        if 'remove_old' in self.process_data[key] and self.process_data[key]['remove_old']:
            fs_remove_current_symbol(self.session, self.feature.feature_id, cv_name, cvterm_name, pub_id)

        # add the new synonym
        if type(self.process_data[key]['data']) is list:
            for item in self.process_data[key]['data']:
                fs = fs_add_by_synonym_name_and_type(self.session, self.feature.feature_id,
                                                     item[FIELD_VALUE], cv_name, cvterm_name, pub_id,
                                                     synonym_sgml=None, is_current=False, is_internal=False)
            if fs and is_current:
                fs.is_current = True
        else:
            fs_add_by_synonym_name_and_type(self.session, self.feature.feature_id,
                                            self.process_data[key]['data'][FIELD_VALUE], cv_name, cvterm_name, pub_id,
                                            synonym_sgml=None, is_current=is_current, is_internal=False)

            if is_current and cvterm_name == 'symbol':
                self.feature.name = sgml_to_plain_text(self.process_data[key]['data'][FIELD_VALUE])

    def load_feature_cvterm(self, key):
        """Add feature_cvterm."""
        cvterm = get_cvterm(self.session,
                            self.process_data[key]['cv'],
                            self.process_data[key]['cvterm'])
        # create feature_cvterm
        feat_cvt, _ = get_or_create(self.session, FeatureCvterm,
                                    feature_id=self.feature.feature_id,
                                    cvterm_id=cvterm.cvterm_id,
                                    pub_id=self.pub.pub_id)
        return feat_cvt

    def load_feature_cvtermprop(self, key):
        """Add feature_cvtermprop.

        If prop_value is False then the value is used as the
        cvterm else it presumes the value is prop value and
        the cvterm is given.
        Could have gone for if cvterm is not defined etc but
        this way is more explicit.
        """
        if type(self.process_data[key]['data']) is list:
            items = self.process_data[key]['data']
        else:
            items = [self.process_data[key]['data']]

        cv_name = self.process_data[key]['cv']
        for item in items:
            prop_value = None
            if self.process_data[key]['prop_value']:
                cvterm_name = self.process_data[key]['cvterm']
                prop_value = item[FIELD_VALUE]
            else:
                # for new ones they are seperated by ';'  x ; y
                # i.e.
                cvterm_name = item[FIELD_VALUE]

            cvterm = get_cvterm(self.session, cv_name, cvterm_name)
            if not cvterm:
                message = "Unable to find cvterm {} for Cv {}.".format(cvterm_name, cv_name)
                self.critical_error(item, message)
                return None

            cv_name = self.process_data[key]['prop_cv']
            cvterm_name = self.process_data[key]['prop_cvterm']
            props_cvterm = get_cvterm(self.session, cv_name, cvterm_name)
            if not props_cvterm:
                message = "Unable to find cvterm {} for Cv {}.".format(cvterm_name, cv_name)
                self.critical_error(item, message)
                return None

            # create feature_cvterm
            feat_cvt, _ = get_or_create(self.session, FeatureCvterm,
                                        feature_id=self.feature.feature_id,
                                        cvterm_id=cvterm.cvterm_id,
                                        pub_id=self.pub.pub_id)

            # create feature_cvtermprop
            get_or_create(self.session, FeatureCvtermprop,
                          feature_cvterm_id=feat_cvt.feature_cvterm_id,
                          value=prop_value,
                          type_id=props_cvterm.cvterm_id)

    def load_feature_relationship(self, key):
        """Add Feature Relationship.

        yml options:
           cv:
           cvterm:
        """
        if not self.has_data(key):
            return

        cv_name = self.process_data[key]['cv']
        cvterm_name = self.process_data[key]['cvterm']
        feat_type = self.process_data[key]['feat_type']
        cvterm = get_cvterm(self.session, cv_name, cvterm_name)
        if not cvterm:
            message = "Unable to find cvterm {} for Cv {}.".format(cvterm_name, cv_name)
            self.critical_error(self.process_data[key]['data'], message)
            return None

        if type(self.process_data[key]['data']) is list:
            for item in self.process_data[key]['data']:
                name = item[FIELD_VALUE]
                obj_feat = feature_name_lookup(self.session, name, type_name=feat_type)
                log.debug("LOOKUP {}: obj feat = {}".format(name, obj_feat))
                fr, _ = get_or_create(self.session, FeatureRelationship,
                                      subject_id=self.feature.feature_id,
                                      object_id=obj_feat.feature_id,
                                      type_id=cvterm.cvterm_id)

                frp, _ = get_or_create(self.session, FeatureRelationshipPub,
                                       feature_relationship_id=fr.feature_relationship_id,
                                       pub_id=self.pub.pub_id)
        else:
            name = self.process_data[key]['data'][FIELD_VALUE]
            obj_feat = feature_name_lookup(self.session, name, type_name=feat_type)
            fr, _ = get_or_create(self.session, FeatureRelationship,
                                  subject_id=self.feature.feature_id,
                                  object_id=obj_feat.feature_id,
                                  type_id=cvterm.cvterm_id)

            frp, _ = get_or_create(self.session, FeatureRelationshipPub,
                                   feature_relationship_id=fr.feature_relationship_id,
                                   pub_id=self.pub.pub_id)

    def load_featureproplist(self, key, prop_cv_id):
        """Load a feature props that are in a list.

        list so obviously more than value allowed.
        """
        for item in self.process_data[key]['data']:
            fp, is_new = get_or_create(self.session, Featureprop, feature_id=self.feature.feature_id,
                                       type_id=prop_cv_id, value=item[FIELD_VALUE])
            get_or_create(self.session, FeaturepropPub, featureprop_id=fp.featureprop_id, pub_id=self.pub.pub_id)

    def load_featureprop(self, key):
        """Store the feature prop.

        If there is a value then it will have a 'value' in the yaml
        pointing to the field that is holding the value.

        yml options:
           cv:
           cvterm:
           value:    <optional>, key to value field.
           only_one: <optional>, defaults to False.
        """
        if not self.has_data(key):
            return
        value = None
        prop_cv_id = self.cvterm_query(self.process_data[key]['cv'], self.process_data[key]['cvterm'])

        if type(self.process_data[key]['data']) is list:
            self.load_featureproplist(key, prop_cv_id)
            return
        if 'only_one' in self.process_data[key] and self.process_data[key]['only_one']:
            fp, is_new = get_or_create(self.session, Featureprop, feature_id=self.feature.feature_id,
                                       type_id=prop_cv_id)
            if 'value' in self.process_data[key] and self.process_data[key]['value'] != 'YYYYMMDD':
                value = self.process_data[self.process_data[key]['value']]['data'][FIELD_VALUE]
            elif 'value' in self.process_data[key]:
                value = datetime.today().strftime('%Y%m%d')
        elif ('value' in self.process_data[key] and self.has_data(self.process_data[key]['value'])):
            value = self.process_data[self.process_data[key]['value']]['data'][FIELD_VALUE]
            fp, is_new = get_or_create(self.session, Featureprop, feature_id=self.feature.feature_id,
                                       type_id=prop_cv_id, value=value)
        else:
            message = "Coding error. only_one or value must be specified if not a list."
            self.critical_error(self.process_data[self.process_data[key]['value']]['data'], message)

        if is_new:
            fp.value = value
        elif fp.value:
            message = "Already has a value. Use bangc to change it"
            self.critical_error(self.process_data[self.process_data[key]['value']]['data'], message)

        # create feature prop pub
        get_or_create(self.session, FeaturepropPub, featureprop_id=fp.featureprop_id, pub_id=self.pub.pub_id)

    def delete_featureprop(self, key, bangc=False):
        """Delete the feature prop and fp pubs.

        If there is a value then it will have a 'value' in the yaml
        pointing to the field that is holding the value.

        yml options:
           cv:
           cvterm:

        """
        if not self.has_data(key):
            return
        prop_cv_id = self.cvterm_query(self.process_data[key]['cv'], self.process_data[key]['cvterm'])

        # get featureprop pubs
        fpps = self.session.query(FeaturepropPub).join(Featureprop).\
            filter(FeaturepropPub.pub_id == self.pub.pub_id,
                   Featureprop.feature_id == self.feature.feature_id,
                   Featureprop.type_id == prop_cv_id)
        for fpp in fpps:
            fp = fpp.featureprop
            self.session.delete(fp)
            self.session.delete(fpp)
