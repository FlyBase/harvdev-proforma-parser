"""
:synopsis: Merging gene code.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>, Ian Longden <ilongden@morgan.harvard.edu>
"""
from harvdev_utils.production import (
    FeatureGrpmember, FeatureHumanhealthDbxref
)
from harvdev_utils.chado_functions import (
    get_or_create
)

import logging
log = logging.getLogger(__name__)


def transfer_grpmembers(self, gene):
    """Transfer feature grpmembers."""
    for feat_gm in self.session.query(FeatureGrpmember).filter(FeatureGrpmember.feature_id == gene.feature_id):
        feat_gm.feature_id = self.feature.feature_id


def transfer_hh_dbxrefs(self, gene):
    """Transfer feature humanhealth_dbxref data."""
    for feat_hh_d in self.session.query(FeatureHumanhealthDbxref).filter(FeatureHumanhealthDbxref.feature_id == gene.feature_id):
        get_or_create(self.session, FeatureHumanhealthDbxref, feature_id=self.feature.feature_id, humanhealth_dbxref_id=feat_hh_d.humanhealth_dbxref_id,
                      pub_id=feat_hh_d.pub_id)


def merge(self, key):
    """Merge gene list into new gene."""
    # change the pub
    self.feature.pub_id = self.pub.pub_id

    # genes = self.get_merge_genes(key)
    genes = self.get_merge_features(key, feat_type='gene')
    for gene in genes:
        log.debug("Gene to be merged is {}".format(gene))
        gene.is_obsolete = True
        # Transfer synonyms
        self.transfer_synonyms(gene)
        # Transfer cvterms
        self.transfer_cvterms(gene)
        # Transfer dbxrefs
        self.transfer_dbxrefs(gene)
        # Transfer grpmembers
        self.transfer_grpmembers(gene)
        # humanhealth_dbxrefs
        self.transfer_hh_dbxrefs(gene)
        # transfer papers
        self.transfer_papers(gene)
        # transfer featureprop and featureproppubs
        self.transfer_props(gene)
