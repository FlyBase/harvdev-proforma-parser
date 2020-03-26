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
    FeatureRelationship, FeatureRelationshipPub, Featureprop, Pub
)
from chado_object.utils.feature import (
    feature_name_lookup
)
import logging
log = logging.getLogger(__name__)


class ChadoFeatureObject(ChadoObject):
    """ChadoFeature object."""

    # from chado_object.feature.feature_synonym import (
    #    load_synonym
    # )
    def __init__(self, params):
        """Initialise the ChadoGene Object."""
        log.debug('Initializing ChadoFeatureObject.')

        # Initiate the parent.
        super(ChadoFeatureObject, self).__init__(params)
        self.feature = None

    def get_pub_id_for_synonym(self, key):
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
        """Load Synonym."""
        # Chemicals can be listed more than once
        # But are only loaded once. We do not allow synoym changes
        # for these repeated chemicals. !c Should be used in this case

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
                log.info("FEAT Adding synonym {} for {}".format(item[FIELD_VALUE], self.feature.name))
                fs_add_by_synonym_name_and_type(self.session, self.feature.feature_id,
                                                item[FIELD_VALUE], cv_name, cvterm_name, pub_id,
                                                synonym_sgml=None, is_current=is_current, is_internal=False)
        else:
            log.info("FEAT Adding synonym {} for {}".format(self.process_data[key]['data'][FIELD_VALUE], self.feature.name))
            fs_add_by_synonym_name_and_type(self.session, self.feature.feature_id,
                                            self.process_data[key]['data'][FIELD_VALUE], cv_name, cvterm_name, pub_id,
                                            synonym_sgml=None, is_current=is_current, is_internal=False)

            if is_current and cvterm_name == 'symbol':
                self.feature.name = sgml_to_plain_text(self.process_data[key]['data'][FIELD_VALUE])

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
                              subject_id=self.feature.feature_id,
                              object_id=obj_feat.feature_id,
                              type_id=cvterm.cvterm_id)

        frp, _ = get_or_create(self.session, FeatureRelationshipPub,
                               feature_relationship_id=fr.feature_relationship_id,
                               pub_id=self.pub.pub_id)

    def load_featureprop(self, key):
        """Load featureprop."""
        if not self.has_data(key):
            return
        cv_name = self.process_data[key]['cv']
        cvterm_name = self.process_data[key]['cvterm']
        cvterm = get_cvterm(self.session, cv_name, cvterm_name)
        if not cvterm:
            message = "Unable to find cvterm {} for Cv {}.".format(cvterm_name, cv_name)
            self.critical_error(self.process_data[key]['data'], message)
            return None

        prop, _ = get_or_create(self.session, Featureprop, value=self.process_data[key]['data'][FIELD_VALUE],
                                type_id=cvterm.cvterm_id, feature_id=self.feature.feature_id)
        if not prop:
            message = "Unable to create Featue prop??? Sorry wierd one!!"
            self.critical_error(self.process_data[key]['data'], message)
