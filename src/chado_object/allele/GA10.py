"""GA10 processing.

This is complex so was split out from allele.py.
"""
import logging
import re
from harvdev_utils.chado_functions import (
    get_or_create, get_cvterm, feature_symbol_lookup
)
from chado_object.utils.feature_synonym import fs_add_by_synonym_name_and_type

from harvdev_utils.production import (
    Feature, FeatureRelationshipPub, FeatureRelationship,
    FeatureRelationshipprop, FeatureRelationshippropPub,
    FeaturePub,
    Featureprop, FeaturepropPub, FeatureSynonym,
    Pub, Synonym
)
from harvdev_utils.chado_functions.organism import get_organism
from chado_object.chado_base import FIELD_VALUE
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from harvdev_utils.chado_functions import synonym_name_details
log = logging.getLogger(__name__)


def get_GA10_cvterms(self, key):
    """Get cvterms needed for G10.

    Args:
        key (string): key/field of proforma to get pub for.

    """
    cvterms = {}

    cvterms['rel_cvterm'] = get_cvterm(self.session, self.process_data[key]['cv'], self.process_data[key]['cvterm'])
    if not cvterms['rel_cvterm']:
        message = "Unable to find cvterm '{}' for Cv '{}'.".format(self.process_data[key]['cvterm'], self.process_data[key]['cv'])
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

    # GA10a has fewer cvterms as no prop
    if key == 'GA10a':
        return cvterms

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

    return cvterms


def get_feature(self, key, item, cvterms):
    """Get feature, may need to create it.

    Args:
        key (string): key/field of proforma to get pub for.
        item (tuple): proforma tuple (key, value, line, bangc).
        cvterms (dict): Dictionary of cvterms already looked up.
    """
    name2code = {'transposable_element_insertion_site': 'ti',
                 'transgenic_transposable_element': 'tp',
                 'insertion_site': 'ti',
                 'engineered_region': 'tp'
                 }

    is_new_feature = False
    name = item[FIELD_VALUE]
    fields = re.search(r"NEW:(\S+)", name)
    if fields:
        if fields.group(1):
            name = fields.group(1)
            is_new_feature = True

    fb_type_name = self.process_data[key]['feat_type']

    if fb_type_name == 'transgenic_transposable_element':
        organism = get_organism(self.session, genus='synthetic', species='construct')
    else:
        organism, _, _ = synonym_name_details(self.session, name)

    if name.startswith('TI'):
        fb_type_name = self.process_data[key]['TI_feat_type']
        if key == 'GA10a':
            organism = get_organism(self.session, genus='synthetic', species='construct')

    fb_code = name2code[fb_type_name]
    fb_type = get_cvterm(self.session, 'SO', fb_type_name)
    if is_new_feature:
        uniquename = 'FB{}:temp_0'.format(fb_code)
        feature, is_new = get_or_create(self.session, Feature, name=name,
                                        type_id=fb_type.cvterm_id, uniquename=uniquename,
                                        organism_id=organism.organism_id)
        if not is_new:
            message = "Feature has NEW: but is not"
            self.critical_error(item, message)
            return
        # add FeaturePub
        get_or_create(self.session, FeaturePub, feature_id=feature.feature_id, pub_id=self.pub.pub_id)
    else:
        try:
            feature = feature_symbol_lookup(self.session, fb_type_name, name, ignore_org=True)
        except NoResultFound:
            message = "Unable to find Feature with symbol {} Add 'NEW:' if it is to be created.".format(name)
            message += f" Using type='{fb_type_name}' name='{name}' ignore_org=True"
            self.critical_error(item, message)
            return
        except MultipleResultsFound:
            message = "Found more than feature with this symbol {}.".format(name)
            self.critical_error(item, message)
            return

    self.synonyms_GA10(key, name, feature, is_new_feature, cvterms)
    return feature


def synonyms_GA10(self, key, name, feature, is_new_feature, cvterms):
    """Add GA10 synonyms as needed.

    Args:
        key (string): key/field of proforma to get pub for.
        name (string): synonym name.
        feature (FeatureObject): Feature to have synonyms added.
        is_new_feature: True if able feature is newly created.
        cvterms (dict): Dictionary of cvterms already looked up.
    """
    if 'synonym_field' in self.process_data[key] and self.has_data(self.process_data[key]['synonym_field']):
        syn_key = self.process_data[key]['synonym_field']
        if self.has_data(syn_key):
            for syn_data in self.process_data[syn_key]['data']:
                syn_name = syn_data[FIELD_VALUE]
                _, syn_plain_name, syn_sgml = synonym_name_details(self.session, syn_name)
                fs_add_by_synonym_name_and_type(self.session, feature.feature_id,
                                                syn_plain_name, self.process_data[syn_key]['cv'],
                                                self.process_data[syn_key]['cvterm'], self.pub.pub_id,
                                                synonym_sgml=syn_sgml, is_current=self.process_data[syn_key]['is_current'], is_internal=False)

    # After other synonyms in case we it is duplicated as a synonym here and we want to keep it current
    if is_new_feature:
        _, plain_name, sgml = synonym_name_details(self.session, name)
        syn_pub = self.session.query(Pub).filter(Pub.uniquename == self.process_data[key]['syn_pub']).one_or_none()
        if not syn_pub:
            self.critical_error(self.process_data[key]['data'], 'Pub {} does not exist in the database.'.format(self.process_data[key]['syn_pub']))
            return

        synonym, _ = get_or_create(self.session, Synonym, type_id=cvterms['syn_type'].cvterm_id, name=plain_name, synonym_sgml=sgml)

        fs, _ = get_or_create(self.session, FeatureSynonym, feature_id=feature.feature_id, synonym_id=synonym.synonym_id,
                              pub_id=syn_pub.pub_id)
        fs.is_current = True
        fs.is_internal = False


def tp_part_process(self, item, cvterms, ti_object):
    """Process tp and allele part of name.

    Args:
        item (tuple): proforma tuple (key, value, line, bangc).
        cvterms (dict): Dictionary of cvterms already looked up.
        ti_object (Feature Object): TI feature object
    """
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
        # need diff oranism for TI.
        organism_id = None
        if tp_part_name.startswith('TI'):
            organism_id = get_organism(self.session, genus='synthetic', species='construct').organism_id
        tp_part = feature_symbol_lookup(self.session, None, tp_part_name, organism_id=organism_id)
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

    Args:
        key (string): key/field of proforma to get pub for.
    """
    if not self.has_data(key):
        return
    if key == 'GA10g':
        self.process_GA10g(key)
        return

    cvterms = self.get_GA10_cvterms(key)
    if not cvterms:
        return

    if type(self.process_data[key]['data']) is list:
        items = self.process_data[key]['data']
    else:
        items = [self.process_data[key]['data']]

    for item in items:
        tx_feature = self.get_feature(key, item, cvterms)
        if not tx_feature:
            continue

        if key == 'GA10a':
            self.process_GA10a(cvterms, tx_feature)
            continue

        # Else GA10[ce]
        self.tp_part_process(item, cvterms, tx_feature)

        # Add feat relationship for new_feat to allele (self.feature)
        ti_allele, _ = get_or_create(self.session, FeatureRelationship,
                                     subject_id=self.feature.feature_id,
                                     object_id=tx_feature.feature_id,
                                     type_id=cvterms['rel_cvterm'].cvterm_id)

        frp, _ = get_or_create(self.session, FeatureRelationshipPub,
                               feature_relationship_id=ti_allele.feature_relationship_id,
                               pub_id=self.pub.pub_id)

        # add feature relationshipproppub to allele
        rank = 0
        seen = None
        frps = self.session.query(FeatureRelationshipprop).\
            filter(FeatureRelationshipprop.feature_relationship_id == ti_allele.feature_relationship_id,
                   FeatureRelationshipprop.type_id == cvterms['prop_cvterm'].cvterm_id)
        for frp in frps:
            if frp.value == self.process_data[key]['prop_value']:
                seen = frp
            if frp.rank > rank:
                rank = frp.rank
        rank += 1

        if not seen:
            frp = FeatureRelationshipprop(feature_relationship_id=ti_allele.feature_relationship_id,
                                          rank=rank,
                                          value=self.process_data[key]['prop_value'],
                                          type_id=cvterms['prop_cvterm'].cvterm_id)
            self.session.add(frp)
            # Now get it to update the _id for this
            frp = self.session.query(FeatureRelationshipprop).\
                filter(FeatureRelationshipprop.feature_relationship_id == ti_allele.feature_relationship_id,
                       FeatureRelationshipprop.rank == rank,
                       FeatureRelationshipprop.type_id == cvterms['prop_cvterm'].cvterm_id).one()
        else:
            self.warning_error(item, f"Feature relationshipprop with value {self.process_data[key]['prop_value']} already exists ignoring.")
            frp = seen

        frp_proppub, _ = get_or_create(self.session, FeatureRelationshippropPub,
                                       feature_relationshipprop_id=frp.feature_relationshipprop_id,
                                       pub_id=self.pub.pub_id)

        # Add feat relationship for new_feat to gene
        tp_gene, _ = get_or_create(self.session, FeatureRelationship,
                                   subject_id=self.gene.feature_id,
                                   object_id=tx_feature.feature_id,
                                   type_id=cvterms['rel_cvterm'].cvterm_id)

        frp, _ = get_or_create(self.session, FeatureRelationshipPub,
                               feature_relationship_id=tp_gene.feature_relationship_id,
                               pub_id=self.pub.pub_id)


def process_GA10g(self, key):
    """Process GA10g.

    Args:
        key (string): key/field of proforma to get pub for.
    """
    if self.process_data[key]['data'][FIELD_VALUE] == '+':
        fp_cvterm = get_cvterm(self.session, self.process_data[key]['fp_cv'], self.process_data[key]['fp_cvterm'])
        if not fp_cvterm:
            message = "Unable to find cvterm '{}' for Cv '{}'.".format(self.process_data[key]['fp_cvterm'], self.process_data[key]['fp_cv'])
            self.critical_error(self.process_data[key]['data'], message)
            return None
        fp, is_new = get_or_create(self.session, Featureprop, feature_id=self.feature.feature_id,
                                   type_id=fp_cvterm.cvterm_id, value=self.process_data[key]['fp_value'])
        get_or_create(self.session, FeaturepropPub, featureprop_id=fp.featureprop_id, pub_id=self.pub.pub_id)
    else:
        # lookup feature
        self.load_feature_relationship(key)


def process_GA10a(self, cvterms, ti_feature):
    """Add ti relatioships.

    Args:
        cvterms (dict): Dictionary of cvterms already looked up.
        ti_feature (Feature Object): TI feature object
    """
    # Add feat relationship for new_feat to allele (self.feature)
    ti_allele, _ = get_or_create(self.session, FeatureRelationship,
                                 subject_id=self.feature.feature_id,
                                 object_id=ti_feature.feature_id,
                                 type_id=cvterms['rel_cvterm'].cvterm_id)

    frp, _ = get_or_create(self.session, FeatureRelationshipPub,
                           feature_relationship_id=ti_allele.feature_relationship_id,
                           pub_id=self.pub.pub_id)

    # feature pub
    get_or_create(self.session, FeaturePub, feature_id=ti_feature.feature_id, pub_id=self.pub.pub_id)
