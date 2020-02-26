"""
:synopsis: Merging gene code.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>, Ian Longden <ilongden@morgan.harvard.edu>
"""
from chado_object.chado_base import FIELD_VALUE
from harvdev_utils.production import (
    FeatureDbxref, Featureloc
)
# from harvdev_utils.chado_functions import get_or_create, get_cvterm, DataError
from chado_object.utils.feature import (
    feature_symbol_lookup
)
from chado_object.utils.synonym import synonym_name_details
from sqlalchemy.orm.exc import NoResultFound

import logging
log = logging.getLogger(__name__)


def transfer_dbxrefs(self, gene):
    """Transfer dbxref from gene to self.gene."""
    dbxrefs = self.session.query(FeatureDbxref).filter(FeatureDbxref.feature_id == gene.feature_id)
    for dbxref in dbxrefs:
        # add to self.gene
        pass


def get_merge_genes(self, key):
    """Get genes to be merged.

    Get genes to be merged and do some checks.

    Returns: list of valid gene objects to be merged.

    Raise: Critical errors on:-
        If G1g = 'y' then G1a (self.gene now) MUST be in G1f list.
        Non valid symbol.
        Gene has featureloc
    """
    genes = []
    found = False
    # Check gene from G1a (self.gene) is in the list to be merged
    for merge_gene_symbol_tuple in self.process_data[key]['data']:
        merge_gene_symbol = merge_gene_symbol_tuple[FIELD_VALUE]
        organism, plain_name, sgml = synonym_name_details(self.session, merge_gene_symbol)
        try:
            gene = feature_symbol_lookup(self.session, 'gene', merge_gene_symbol, organism_id=organism.organism_id)
            genes.append(gene)
        except NoResultFound:
            message = "Unable to find Gene with symbol {}.".format(merge_gene_symbol)
            self.critical_error(merge_gene_symbol_tuple, message)
            continue
        if self.gene.name == gene.name:
            found = True
        # Not allowed to merge genes with featureloc
        if self.session.query(Featureloc).filter(Featureloc.feature_id == gene.feature_id).one_or_none():
            message = "{} Gene has featureloc which is not allowed in merges".format(merge_gene_symbol)
            self.critical_error(merge_gene_symbol_tuple, message)
    if self.process_data['G1g']['data'][FIELD_VALUE] == 'y' and not found:
        message = "G1a {} must be in G1f list when G1g is set to y".format(self.process_data['G1a']['data'][FIELD_VALUE])
        self.critical_error(self.process_data[key]['data'][0], message)
    return genes


def merge(self, key):
    """Merge gene list into new gene."""
    genes = self.get_merge_genes(key)
    for gene in genes:
        log.debug("Gene to be merged is {}".format(gene))
        gene.is_obsolete = True
        # Transfer dbxrefs
        self.transfer_dbxrefs(gene)
        # Transfer synonyms
        self.tranfer_synonyms(gene)
