"""Gane and Allele merging methods."""
from chado_object.chado_base import FIELD_VALUE
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from harvdev_utils.chado_functions import (
    get_or_create,
    feature_symbol_lookup,
    synonym_name_details
)
from harvdev_utils.production import (
    FeatureDbxref, Featureloc, FeatureSynonym, FeatureCvterm
)
import logging
log = logging.getLogger(__name__)


def transfer_cvterms(self, feat):
    """Transfer feature cvterms."""
    for feat_cvterm in self.session.query(FeatureCvterm).filter(FeatureCvterm.feature_id == feat.feature_id):
        get_or_create(self.session, FeatureCvterm, feature_id=self.feature.feature_id, cvterm_id=feat_cvterm.cvterm_id,
                      pub_id=feat_cvterm.pub_id)


def transfer_dbxrefs(self, feat):
    """Transfer dbxref from feat to self.feature.

    If dbxref is from a Flybase db then we want move it to the merge
    feat and set is_current to False.

    Else we want to copy the dbxref.
    """
    # copy feature's dbxref to dbxref table
    featdbx, _ = get_or_create(self.session, FeatureDbxref, dbxref_id=feat.dbxref_id, feature_id=self.feature.feature_id)
    featdbx.is_current = False

    for featdbx in self.session.query(FeatureDbxref).filter(FeatureDbxref.feature_id == feat.feature_id):
        fd, _ = get_or_create(self.session, FeatureDbxref, dbxref_id=featdbx.dbxref.dbxref_id, feature_id=self.feature.feature_id)
        fd.is_current = True


def transfer_synonyms(self, feat):
    """Create new feature synonyms and make is_current True."""
    for feat_syn in self.session.query(FeatureSynonym).filter(FeatureSynonym.feature_id == feat.feature_id):
        fs, _ = get_or_create(self.session, FeatureSynonym, synonym_id=feat_syn.synonym_id, feature_id=self.feature.feature_id,
                              pub_id=feat_syn.pub_id)
        if feat.name != self.feature.name:
            fs.is_current = False


def multiple_check(self, feats, feat_type, merge_feat_symbol, merge_feat_symbol_tuple, organism):
    """Check if multiple values is okay."""
    message = "Multiple results found for type: '{}' name: '{}'".format(feat_type, merge_feat_symbol)
    features = feature_symbol_lookup(self.session, feat_type, merge_feat_symbol,
                                     organism_id=organism.organism_id, check_unique=False)
    count = -1
    for feature in features:
        if 'temp' in feature.uniquename:  # For merging we have new teml gene/allele and the original with possibly the same synonym
            count += 1
            message += "\n\tfound: {}".format(feature)
        else:
            feats.append(feature)
            feat = feature
    if count:
        self.critical_error(merge_feat_symbol_tuple, message)
    return feat


def get_merge_features(self, key, feat_type='gene'):
    """Get gene/allele's to be merged.

    Get genes/allels to be merged and do some checks.

    Returns: list of valid feature objects to be merged.

    Raise: Critical errors on:-
        If G[A]1g = 'y' then G[A]1a (self.feature now) MUST be in G[A]1f list.
        Non valid symbol.
        More than one featureloc
    """
    feats = []
    found = False
    featlock_count = 0
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
            featlock_count += 1

    if self.session.query(Featureloc).filter(Featureloc.feature_id == self.feature.feature_id).one_or_none():
        featlock_count += 1
    if featlock_count > 1:
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
