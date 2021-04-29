"""Gane and Allele merging methods.

:synopsis: merge features.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>, Ian Longden <ilongden@morgan.harvard.edu>

NOTE: transfer methods do not transfer but merely copy to the new feature.
      Old features are made obsolete that is all.
"""
from chado_object.chado_base import FIELD_VALUE
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from harvdev_utils.chado_functions import (
    get_or_create,
    feature_symbol_lookup,
    synonym_name_details
)
from harvdev_utils.production import (
    FeatureDbxref, Featureloc, FeatureSynonym, FeatureCvterm, FeatureCvtermprop,
    FeatureRelationship, FeatureRelationshipPub,
    FeatureRelationshipprop, FeatureRelationshippropPub
)
import logging
log = logging.getLogger(__name__)


def process_feat_relation_dependents(self, old_feat_rela, new_feat_rela):
    """Add feature relationship (_pub, prop, prop_pub).

    Args:
        old_feat_rela: <FeatureRelationship> old featurerelatiosnhip to copy from
        new_feat_rela: <FeatureRelationship> to be copied too.

    The following are related to the feature relationship so need to be transferered.

    public | feature_relationship_pub                                        | table    | postgres
    public | feature_relationshipprop                                        | table    | postgres
    public | feature_relationshipprop_pub                                    | table    | postgres

    """
    # _pub
    frpubs = self.session.query(FeatureRelationshipPub).\
        filter(FeatureRelationshipPub.feature_relationship_id == old_feat_rela.feature_relationship_id)
    for frpub in frpubs:
        get_or_create(
            self.session, FeatureRelationshipPub,
            feature_relationship_id=new_feat_rela.feature_relationship_id,
            pub_id=frpub.pub_id)
    # prop
    frprops = self.session.query(FeatureRelationshipprop).\
        filter(FeatureRelationshipprop.feature_relationship_id == old_feat_rela.feature_relationship_id)
    for old_frprop in frprops:
        new_frprop, _ = get_or_create(
            self.session, FeatureRelationshipprop,
            feature_relationship_id=new_feat_rela.feature_relationship_id,
            type_id=old_frprop.type_id,
            value=old_frprop.value)
        # prop_pub
        old_frp_pubs = self.session.query(FeatureRelationshippropPub).\
            filter(FeatureRelationshippropPub.feature_relationshipprop_id == old_frprop.feature_relationshipprop_id)
        for old_frp_pub in old_frp_pubs:
            get_or_create(
                self.session, FeatureRelationshippropPub,
                feature_relationshipprop_id=new_frprop.feature_relationshipprop_id,
                pub_id=new_frprop.pub_id)


def transfer_feature_relationships(self, feat):
    """Transfer Feature Relationships.

    Args:
        feat: <Feature> old feature to copy from
    Copied to self.feature (the new feature)

    public | feature_relationship                                            | table    | postgres
    public | feature_relationship_pub                                        | table    | postgres
    public | feature_relationshipprop                                        | table    | postgres
    public | feature_relationshipprop_pub                                    | table    | postgres

    """
    for old_feat_is_object in (True, False):
        if old_feat_is_object:
            filter_spec = (FeatureRelationship.object_id == feat.feature_id,)
        else:
            filter_spec = (FeatureRelationship.subject_id == feat.feature_id,)

        old_feat_relas = self.session.query(FeatureRelationship).filter(*filter_spec)
        for old_feat_rela in old_feat_relas:
            if old_feat_is_object:
                object_id = self.feature.feature_id
                subject_id = old_feat_rela.subject_id
            else:
                subject_id = self.feature.feature_id
                object_id = old_feat_rela.object_id
            new_feat_rela, _ = get_or_create(
                self.session, FeatureRelationship,
                subject_id=subject_id, object_id=object_id,
                value=old_feat_rela.value, type_id=old_feat_rela.type_id)
            self.process_feat_relation_dependents(old_feat_rela, new_feat_rela)


def transfer_cvterms(self, feat):
    """Transfer feature cvterms.

    Args:
        feat: <Feature> old feature to copy from
    Copied to self.feature (the new feature)
    """
    for feat_cvterm in self.session.query(FeatureCvterm).filter(FeatureCvterm.feature_id == feat.feature_id):
        new_cv, _ = get_or_create(self.session, FeatureCvterm, feature_id=self.feature.feature_id, cvterm_id=feat_cvterm.cvterm_id,
                                  pub_id=feat_cvterm.pub_id)
        for cvprop in self.session.query(FeatureCvtermprop).filter(FeatureCvtermprop.feature_cvterm_id == feat_cvterm.feature_cvterm_id):
            get_or_create(self.session, FeatureCvtermprop, feature_cvterm_id=new_cv.feature_cvterm_id,
                          type_id=cvprop.type_id, value=cvprop.value)


def transfer_dbxrefs(self, feat):
    """Transfer dbxref from feat to self.feature.

    Args:
        feat: <Feature> old feature to copy from
    Copied to self.feature (the new feature)

    If dbxref is from a Flybase db then we want move it to the merge
    feat and set is_current to False.

    Else we want to copy the dbxref.
    """
    # copy feature's dbxref to dbxref table
    featdbx, _ = get_or_create(self.session, FeatureDbxref, dbxref_id=feat.dbxref_id, feature_id=self.feature.feature_id)
    featdbx.is_current = False

    for featdbx in self.session.query(FeatureDbxref).filter(FeatureDbxref.feature_id == feat.feature_id):
        fd, _ = get_or_create(self.session, FeatureDbxref,
                              dbxref_id=featdbx.dbxref.dbxref_id, feature_id=self.feature.feature_id)
        fd.is_current = featdbx.is_current


def transfer_synonyms(self, feat):
    """Create new feature synonyms and make is_current True.

    Args:
        feat: <Feature> old feature to copy from
    Copied to self.feature (the new feature)
    """
    for feat_syn in self.session.query(FeatureSynonym).filter(FeatureSynonym.feature_id == feat.feature_id):
        fs, _ = get_or_create(self.session, FeatureSynonym, synonym_id=feat_syn.synonym_id, feature_id=self.feature.feature_id,
                              pub_id=feat_syn.pub_id)
        if feat.name != self.feature.name:
            fs.is_current = False


def multiple_check(self, feats, feat_type, merge_feat_symbol, merge_feat_symbol_tuple, organism):
    """Check if multiple values is okay.

    Make sure the synonym os found only once. It may exist again as a 'temp' but this is okay,
    as that means it is a newly created synonym and the old one will be removed at the end.

    Args:
        feats: <list of Features> old features to check
        feat_type: <str> feature type name
        merge_feat_symbol: <str> symbol name
        merge_feat_symbol_tuple: <tuple> proforma (field, value, bangc)
        organism: <Organism> orgainsm to use
    """
    message = "Multiple results found for type: '{}' name: '{}'".format(feat_type, merge_feat_symbol)
    features = feature_symbol_lookup(self.session, feat_type, merge_feat_symbol,
                                     organism_id=organism.organism_id, check_unique=False)
    count = -1
    for feature in features:
        # For merging we have new temp gene/allele and the original with possibly the same synonym
        if 'temp' not in feature.uniquename:
            count += 1
            message += "\n\tfound: {}".format(feature)
            feats.append(feature)
            feat = feature
    if count:
        self.critical_error(merge_feat_symbol_tuple, message)
    return feat


def get_merge_features(self, key, feat_type='gene'):
    """Get gene/allele's to be merged.

    Get genes/allels to be merged and do some checks.

    Args:
        key: <str> proforma merge key (i.e. GA1f, G1f)
        feat_type: <str> feature type
    Returns:
        list of valid feature objects to be merged.

    Raise: Critical errors on:-
        If G[A]1g = 'y' then G[A]1a (self.feature now) MUST be in G[A]1f list.
        Non valid symbol.
        More than one featureloc
    """
    feats = []
    found = False
    featloc_count = 0
    # Check gene from G[A]1a (self.feature) is in the list to be merged
    for merge_feat_symbol_tuple in self.process_data[key]['data']:
        merge_feat_symbol = merge_feat_symbol_tuple[FIELD_VALUE]
        organism, plain_name, sgml = synonym_name_details(self.session, merge_feat_symbol)
        try:
            feat = feature_symbol_lookup(self.session, feat_type, merge_feat_symbol, organism_id=organism.organism_id)
            feats.append(feat)
        except NoResultFound:
            message = "Unable to find {} with symbol {}.".format(feat_type, merge_feat_symbol)
            self.critical_error(merge_feat_symbol_tuple, message)
            continue
        except MultipleResultsFound:
            feat = self.multiple_check(feats, feat_type, merge_feat_symbol, merge_feat_symbol_tuple, organism)
        if self.feature.name == feat.name:
            found = True
        # Not allowed to merge feats with featureloc
        if self.session.query(Featureloc).filter(Featureloc.feature_id == feat.feature_id).one_or_none():
            featloc_count += 1

    if self.session.query(Featureloc).filter(Featureloc.feature_id == self.feature.feature_id).one_or_none():
        featloc_count += 1
    if featloc_count > 1:
        message = "More than one {} has featureloc which is not allowed in merges.".format(feat_type)
        self.critical_error(merge_feat_symbol_tuple, message)

    g_key = "{}g".format(key[:-1])
    if self.process_data[g_key]['data'][FIELD_VALUE] == 'y' and not found:
        a_key = "{}a".format(key[:-1])
        f_key = "{}f".format(key[:-1])
        message = "{} {} must be in {} list when {} is set to y".\
            format(a_key, self.process_data[a_key]['data'][FIELD_VALUE], f_key, g_key)
        self.critical_error(self.process_data[key]['data'][0], message)
    return feats
