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
    Cvtermprop, Feature, FeatureRelationship, FeatureRelationshipPub, Featureprop,
    FeaturepropPub, FeatureCvterm, FeatureCvtermprop, FeatureSynonym,
    Pub, Synonym
)
from harvdev_utils.chado_functions import (
    DataError, CodingError, feature_name_lookup, synonym_name_details, feature_symbol_lookup,
    get_feature_and_check_uname_symbol
)
from datetime import datetime
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
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
        self.unattrib_pub = None
        self.new = None

    def get_unattrib_pub(self):
        """Get the unattributed pub."""
        if not self.unattrib_pub:
            self.unattrib_pub, _ = get_or_create(self.session, Pub, uniquename='unattributed')
        return self.unattrib_pub

    def _get_feature(self, so_name, symbol_key, unique_bit):
        """Get the feature."""
        cvterm = get_cvterm(self.session, 'SO', so_name)
        if not cvterm:
            message = "Unable to find cvterm '{}' for Cv 'SO'.".format(so_name)
            self.critical_error(self.process_data[symbol_key]['data'], message)
            return None
        organism, plain_name, sgml = synonym_name_details(self.session, self.process_data[symbol_key]['data'][FIELD_VALUE])
        self.feature, is_new = get_or_create(self.session, Feature, name=plain_name,
                                             type_id=cvterm.cvterm_id, uniquename='FB{}:temp_0'.format(unique_bit),
                                             organism_id=organism.organism_id)
        if is_new:
            self.feature.new = True
        else:
            self.feature.new = False

    def load_feature(self, feature_type='gene'):
        """Get feature.

        from feature type get to the key i.e. 'G' for gene, 'GA' for allele, 'A' for aberation.
        So many proforma use similar keys but just differ in the start bit.
        i.e. G1b, GA1b, A1b.

        So for now lets have a general routine for processing the loading of the feature.
        NOTE: this will only work for those that have the same end field key bits matching
        If we get too many that do not work this way then we may have to pass each key separately.
        """
        CODE = 0
        UNIQUE = 1
        SO = 2
        supported_features = {'gene': ['G', 'gn', 'gene'],
                              'allele': ['GA', 'al', 'gene'],  # new SO will be allele
                              'aberration': ['A', 'ti', 'transposon']}

        if feature_type not in supported_features:
            message = "Unsupported feature type '{}' used in load_feature call. Coding error.".format(feature_type)
            self.critical_error(self.process_data['{}1a'.format(feature_type)]['data'], message)

        symbol_key = '{}1a'.format(supported_features[feature_type][CODE])
        merge_key = '{}1f'.format(supported_features[feature_type][CODE])
        id_key = '{}1h'.format(supported_features[feature_type][CODE])
        current_key = '{}1g'.format(supported_features[feature_type][CODE])

        if self.has_data(merge_key):  # if feature merge we want to create a new feature even if one exist already
            self._get_feature(supported_features[feature_type][SO], symbol_key, supported_features[feature_type][UNIQUE])
            return

        if self.has_data(id_key):
            self.feature = None
            try:
                self.feature = get_feature_and_check_uname_symbol(self.session,
                                                                  self.process_data[id_key]['data'][FIELD_VALUE],
                                                                  self.process_data[symbol_key]['data'][FIELD_VALUE],
                                                                  type_name=supported_features[feature_type][SO])
            except DataError as e:
                self.critical_error(self.process_data[id_key]['data'], e.error)

            return self.feature

        if self.process_data[current_key]['data'][FIELD_VALUE] == 'y':  # Should exist already
            #  organism, plain_name, sgml = synonym_name_details(self.session, self.process_data['G1a']['data'][FIELD_VALUE])
            try:
                self.feature = feature_symbol_lookup(self.session, supported_features[feature_type][SO], self.process_data[symbol_key]['data'][FIELD_VALUE])
            except MultipleResultsFound:
                message = "Multiple {}'s with symbol {}.".format(feature_type, self.process_data[symbol_key]['data'][FIELD_VALUE])
                log.info(message)
                self.critical_error(self.process_data[symbol_key]['data'], message)
                return
            except NoResultFound:
                message = "Unable to find {} with symbol {}.".format(feature_type, self.process_data[symbol_key]['data'][FIELD_VALUE])
                self.critical_error(self.process_data[symbol_key]['data'], message)
                return
        else:
            self._get_feature(supported_features[feature_type][SO], symbol_key, supported_features[feature_type][UNIQUE])
            # add default symbol
            self.load_synonym(symbol_key)

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

    def load_synonym(self, key, unattrib=True):
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
        pubs = [pub_id]
        if unattrib:
            unattrib_pub_id = self.get_unattrib_pub().pub_id
            if pub_id != unattrib_pub_id:
                pubs.append(unattrib_pub_id)

        # remove the current symbol if is_current is set and yaml says remove old is_current
        if 'remove_old' in self.process_data[key] and self.process_data[key]['remove_old']:
            fs_remove_current_symbol(self.session, self.feature.feature_id, cv_name, cvterm_name, pub_id)

        # add the new synonym
        if type(self.process_data[key]['data']) is list:
            for item in self.process_data[key]['data']:
                for pub_id in pubs:
                    fs = fs_add_by_synonym_name_and_type(self.session, self.feature.feature_id,
                                                         item[FIELD_VALUE], cv_name, cvterm_name, pub_id,
                                                         synonym_sgml=None, is_current=False, is_internal=False)
            if fs and is_current:
                fs.is_current = True
        else:
            for pub_id in pubs:
                fs_add_by_synonym_name_and_type(self.session, self.feature.feature_id,
                                                self.process_data[key]['data'][FIELD_VALUE], cv_name, cvterm_name, pub_id,
                                                synonym_sgml=None, is_current=is_current, is_internal=False)

            if is_current and cvterm_name == 'symbol':
                self.feature.name = sgml_to_plain_text(self.process_data[key]['data'][FIELD_VALUE])

    def load_feature_cvterm(self, key):
        """Add feature cvterm."""
        if type(self.process_data[key]['data']) is list:
            items = self.process_data[key]['data']
        else:
            items = [self.process_data[key]['data']]

        cv_name = self.process_data[key]['cv']
        for item in items:
            cvterm_name = item[FIELD_VALUE]
            try:
                cvterm = get_cvterm(self.session, cv_name, cvterm_name)
            except CodingError:
                message = "Unable to find cvterm {} for Cv {}.".format(cvterm_name, cv_name)
                self.critical_error(item, message)
                return None

            if 'cvterm_namespace' in self.process_data[key]:
                try:
                    self.session.query(Cvtermprop).\
                        filter(Cvtermprop.cvterm_id == cvterm.cvterm_id,
                               Cvtermprop.value == self.process_data[key]['cvterm_namespace']).one()
                except NoResultFound:
                    message = "Cvterm '{}' Not in the required namespace of '{}'".\
                        format(cvterm.name, self.process_data[key]['cvterm_namespace'])
                    self.critical_error(item, message)

            # create feature_cvterm
            feat_cvt, _ = get_or_create(self.session, FeatureCvterm,
                                        feature_id=self.feature.feature_id,
                                        cvterm_id=cvterm.cvterm_id,
                                        pub_id=self.pub.pub_id)

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

        cv_name = self.process_data[key]['prop_cv']
        cvterm_name = self.process_data[key]['prop_cvterm']
        props_cvterm = get_cvterm(self.session, cv_name, cvterm_name)
        if not props_cvterm:
            message = "Unable to find cvterm {} for Cv {}.".format(cvterm_name, cv_name)
            self.critical_error(items[0], message)
            return None

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

            if 'cvterm_namespace' in self.process_data[key]:
                try:
                    self.session.query(Cvtermprop).\
                        filter(Cvtermprop.cvterm_id == cvterm.cvterm_id,
                               Cvtermprop.value == self.process_data[key]['cvterm_namespace']).one()
                except NoResultFound:
                    message = "Cvterm '{}' Not in the required namespace of '{}'".\
                        format(cvterm.name, self.process_data[key]['cvterm_namespace'])
                    self.critical_error(item, message)

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

    def load_feature_relationship(self, key, special=None):
        """Add Feature Relationship.

        yml options:
           cv:
           cvterm:
        """
        if not self.has_data(key):
            return
        if type(self.process_data[key]['data']) is list:
            items = self.process_data[key]['data']
        else:
            items = [self.process_data[key]['data']]

        cv_name = self.process_data[key]['cv']
        cvterm_name = self.process_data[key]['cvterm']
        feat_type = None
        if 'feat_type' in self.process_data[key]:
            feat_type = self.process_data[key]['feat_type']
        cvterm = get_cvterm(self.session, cv_name, cvterm_name)
        if not cvterm:
            message = "Unable to find cvterm {} for Cv {}.".format(cvterm_name, cv_name)
            self.critical_error(self.process_data[key]['data'], message)
            return None

        for item in items:
            name = item[FIELD_VALUE]
            if not special:
                obj_feat = feature_name_lookup(self.session, name, type_name=feat_type)
            else:
                obj_feat = feature_name_lookup(self.session, name, type_name=feat_type)
            log.debug("LOOKUP {}: obj feat = {}".format(name, obj_feat))
            fr, _ = get_or_create(self.session, FeatureRelationship,
                                  subject_id=self.feature.feature_id,
                                  object_id=obj_feat.feature_id,
                                  type_id=cvterm.cvterm_id)

            frp, _ = get_or_create(self.session, FeatureRelationshipPub,
                                   feature_relationship_id=fr.feature_relationship_id,
                                   pub_id=self.pub.pub_id)

            if 'add_unattributed_paper' in self.process_data[key] and self.process_data[key]['add_unattributed_paper']:
                unattrib_pub_id = self.get_unattrib_pub().pub_id
                frp, _ = get_or_create(self.session, FeatureRelationshipPub,
                                       feature_relationship_id=fr.feature_relationship_id,
                                       pub_id=unattrib_pub_id)

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
        if not bangc:
            self.delete_specific_fp(key)
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
            # self.session.delete(fpp)

    def delete_specific_fp(self, key, bangc=False):
        """Delete specific featureprop."""
        prop_cv_id = self.cvterm_query(self.process_data[key]['cv'], self.process_data[key]['cvterm'])

        # can be list or single item so make it always a list.
        if type(self.process_data[key]['data']) is list:
            items = self.process_data[key]['data']
        else:
            items = [self.process_data[key]['data']]

        for item in items:
            # get featureprop pubs and delete them
            value = item[FIELD_VALUE]
            fpps = self.session.query(FeaturepropPub).join(Featureprop).\
                filter(FeaturepropPub.pub_id == self.pub.pub_id,
                       Featureprop.feature_id == self.feature.feature_id,
                       Featureprop.type_id == prop_cv_id,
                       Featureprop.value == value)
            count = 0
            for fpp in fpps:
                fp = fpp.featureprop
                self.session.delete(fp)
                self.session.delete(fpp)
                count += 1
            if not count:
                message = "Bangd failed no feature prop pub with value {}".format(value)
                self.critical_error(item, message)
        self.process_data[key]['data'] = None

    def delete_specific_fcp(self, key):
        """Delete feature cvterm based ob feature and cvterm prop."""
        if key == 'G30':
            if not self.alter_check_g30(key):
                return
        if type(self.process_data[key]['data']) is list:
            items = self.process_data[key]['data']
        else:
            items = [self.process_data[key]['data']]
        # Use cvtermprop to get those to delete.
        pcvterm = get_cvterm(self.session, self.process_data[key]['prop_cv'], self.process_data[key]['prop_cvterm'])

        if not pcvterm:
            message = "Unable to find cvterm {} for Cv {}.".format(self.process_data[key]['prop_cv'], self.process_data[key]['prop_cvterm'])
            self.critical_error(items[0], message)
            return

        for item in items:
            try:
                cvterm = get_cvterm(self.session, self.process_data[key]['cv'], item[FIELD_VALUE])
                if not cvterm:
                    message = "Unable to find cvterm {} for Cv {}.".format(self.process_data[key]['prop_cv'], self.process_data[key]['prop_cvterm'])
                    self.critical_error(items[0], message)
                    return
                fcp = self.session.query(FeatureCvtermprop).join(FeatureCvterm).\
                    filter(FeatureCvtermprop.type_id == pcvterm.cvterm_id,
                           FeatureCvterm.feature_id == self.feature.feature_id,
                           FeatureCvterm.pub_id == self.pub.pub_id,
                           FeatureCvterm.cvterm_id == cvterm.cvterm_id).one()
            except NoResultFound:
                self.critical_error(item, "Unable to find value '{}'.".format(item[FIELD_VALUE]))
                continue
            self.session.delete(fcp.feature_cvterm)
        self.process_data[key]['data'] = None

    def delete_feature_cvtermprop(self, key, bangc=False):
        """Delete all feature_cvtermprop for a specific prop.

        If prop_value is False then the value is used as the
        cvterm else it presumes the value is prop value and
        the cvterm is given.
        Could have gone for if cvterm is not defined etc but
        this way is more explicit.
        """
        if not bangc:
            self.delete_specific_fcp(key)
            return

        # Use cvtermprop to get those to delete.
        cvterm = get_cvterm(self.session, self.process_data[key]['prop_cv'], self.process_data[key]['prop_cvterm'])

        if not cvterm:
            message = "Unable to find cvterm {} for Cv {}.".format(self.process_data[key]['prop_cv'], self.process_data[key]['prop_cvterm'])
            self.critical_error(self.process_data[key]['data'][0], message)
            return None

        fcps = self.session.query(FeatureCvtermprop).join(FeatureCvterm).\
            filter(FeatureCvtermprop.type_id == cvterm.cvterm_id,
                   FeatureCvterm.feature_id == self.feature.feature_id,
                   FeatureCvterm.pub_id == self.pub.pub_id)
        count = 0
        # NOTE: NEED TO test old proforma to see what happens exactly.
        for fcp in fcps:
            fc = fcp.feature_cvterm
            self.session.delete(fc)
            count += 1
        if not count:
            message = "Bangc failed no feature cvterm props for this pub"
            self.critical_error(self.process_data[key]['data'][0], message)

    def delete_specific_fr(self, key, items):
        """Delete specific feature relationships."""
        cv_name = self.process_data[key]['cv']
        cvterm_name = self.process_data[key]['cvterm']
        feat_type = None
        if 'feat_type' in self.process_data[key]:
            feat_type = self.process_data[key]['feat_type']
        cvterm = get_cvterm(self.session, cv_name, cvterm_name)
        if not cvterm:
            message = "Unable to find cvterm {} for Cv {}.".format(cvterm_name, cv_name)
            self.critical_error(self.process_data[key]['data'], message)
            return None
        log.debug("LOOKUP {}: cvterm".format(cvterm))
        for item in items:
            name = item[FIELD_VALUE]
            obj_feat = feature_name_lookup(self.session, name, type_name=feat_type)
            log.debug("LOOKUP {}: obj feat = {}".format(name, obj_feat))
            try:
                log.debug("LOOKUP si {}, oi {}, pi {}, ti {}".format(self.feature.feature_id, obj_feat.feature_id, self.pub.pub_id, cvterm.cvterm_id))
                frp = self.session.query(FeatureRelationshipPub).join(FeatureRelationship).\
                    filter(FeatureRelationship.subject_id == self.feature.feature_id,
                           FeatureRelationship.object_id == obj_feat.feature_id,
                           FeatureRelationshipPub.pub_id == self.pub.pub_id,
                           FeatureRelationship.type_id == cvterm.cvterm_id).one()
                self.session.delete(frp.feature_relationship)
            except NoResultFound:
                message = "No relationship found. So cannot delete it"
                self.critical_error(item, message)
        self.process_data[key]['data'] = None

    def delete_feature_relationship(self, key, bangc=False):
        """Delete the feature relationship."""
        if type(self.process_data[key]['data']) is list:
            items = self.process_data[key]['data']
        else:
            items = [self.process_data[key]['data']]
        if not bangc:
            self.delete_specific_fr(key, items)
            return
        cv_name = self.process_data[key]['cv']
        cvterm_name = self.process_data[key]['cvterm']
        cvterm = get_cvterm(self.session, cv_name, cvterm_name)
        if not cvterm:
            message = "Unable to find cvterm {} for Cv {}.".format(cvterm_name, cv_name)
            self.critical_error(self.process_data[key]['data'], message)
            return None
        log.debug("LOOKUP: deleting FR for all {} in pub {} cvterm {}".format(self.feature, self.pub.uniquename, cvterm))
        fcps = self.session.query(FeatureRelationshipPub).join(FeatureRelationship).\
            filter(FeatureRelationship.subject_id == self.feature.feature_id,
                   FeatureRelationshipPub.pub_id == self.pub.pub_id,
                   FeatureRelationship.type_id == cvterm.cvterm_id)
        count = 0
        for fcp in fcps:
            count += 1
            log.debug("LOOKUP: deleting feat rel {}".format(fcp.feature_relationship))
            self.session.delete(fcp.feature_relationship)
        if not count:
            message = "Bangc failed no feature relationships for this pub and cvterm"
            self.critical_error(items[0], message)

    def delete_synonym(self, key, bangc=False):
        """Delete synonym.

        Well actually set is_current to false for this entry.
        """
        if type(self.process_data[key]['data']) is not list:
            data_list = []
            data_list.append(self.process_data[key]['data'])
        else:
            data_list = self.process_data[key]['data']

        if bangc:
            # hh_syn has only one cvterm related to it so no need to specify.
            self.session.query(FeatureSynonym).\
                filter(FeatureSynonym.pub_id == self.pub.pub_id,
                       FeatureSynonym.is_current == False,  # noqa: E712
                       FeatureSynonym.pub_id == self.pub.pub_id,
                       FeatureSynonym.feature_id == self.feature.feature_id).delete()
        else:
            for data in data_list:
                synonyms = self.session.query(Synonym).\
                    filter(Synonym.name == data[FIELD_VALUE])
                syn_count = 0
                f_syn_count = 0
                for syn in synonyms:
                    syn_count += 1
                    f_syns = self.session.query(FeatureSynonym).\
                        filter(FeatureSynonym.humanhealth_id == self.feature.feature_id,
                               FeatureSynonym.synonym_id == syn.synonym_id,
                               FeatureSynonym.is_current == False,  # noqa: E712
                               FeatureSynonym.pub_id == self.pub.pub_id)
                    for f_syn in f_syns:
                        f_syn_count += 1
                        self.session.delete(f_syn)

                if not syn_count:
                    self.critical_error(data, 'Synonym {} Does not exist.'.format(data[FIELD_VALUE]))
                    continue
                elif not f_syn_count:
                    self.critical_error(data, 'Synonym {} Does not exist for this Feature that is not current.'.format(data[FIELD_VALUE]))
                    continue
