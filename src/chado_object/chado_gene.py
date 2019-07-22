"""
.. module:: chado_gene
   :synopsis: The "gene" ChadoObject.

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
from .chado_base import ChadoObject, FIELD_VALUE
from harvdev_utils.production import (
    Cvterm, FeaturePub, FeatureSynonym, Synonym, Feature
)
from harvdev_utils.chado_functions import get_or_create

from sqlalchemy.orm.exc import NoResultFound

import logging
log = logging.getLogger(__name__)


class ChadoGene(ChadoObject):
    def __init__(self, params):
        log.info('Initializing ChadoGene object.')

        self.P22_FlyBase_reference_ID = params['fields_values'].get('P22')

        self.G1a_symbol_in_FB = params['fields_values'].get('G1a')
        self.G1b_symbol_used_in_ref = params['fields_values'].get('G1b')
        self.G2b_name_used_in_ref = params['fields_values'].get('G2b')

        # Values queried later, placed here for reference purposes.
        self.gene = None
        self.pub = None

        # Initiate the parent.
        super(ChadoGene, self).__init__(params)

    def obtain_session(self, session):
        self.session = session

    def is_current_symbol(self, G1b_entry):
        log.debug('Checking whether \'{}\' is the current symbol in Chado'.format(G1b_entry[FIELD_VALUE]))
        self.current_query_source = G1b_entry
        self.current_query = 'Querying for \'%s\'.' % (G1b_entry[FIELD_VALUE])
        log.debug(self.current_query)

        filters = (
            Feature.is_obsolete == 'f',
            Feature.feature_id == FeatureSynonym.feature_id,
            FeatureSynonym.synonym_id == Synonym.synonym_id,
            FeatureSynonym.is_current == 't',
            Cvterm.name == 'symbol',
            Feature.uniquename == self.gene.uniquename
        )
        try:
            results = self.session.query(Synonym.synonym_sgml).join(Cvterm, Cvterm.cvterm_id == Synonym.type_id).distinct().\
                              filter(*filters).one()
        except NoResultFound:
            return False

        symbol_name_from_results = results[0]

        if symbol_name_from_results == G1b_entry[FIELD_VALUE]:
            log.debug('\'{}\' matches the current symbol in Chado: \'{}\', FBgn: \'{}\'. Returning is_current = \'t\''.
                      format(G1b_entry[FIELD_VALUE], self.G1a_symbol_in_FB[FIELD_VALUE], self.gene.uniquename))
            return True
        else:
            log.debug('\'{}\' does not match the current symbol in Chado: \'{}\', FBgn: \'{}\'. Returning is_current = \'f\''.
                      format(G1b_entry[FIELD_VALUE], self.G1a_symbol_in_FB[FIELD_VALUE], self.gene.uniquename))
            return False

    def process_G1b_symbols(self):

        if self.bang_d == 'G1b':
            # Remove only the entries listed in this field.
            log.info('Removing the entries listed in field \'%s\'.' % (self.bang_d))
            for G1b_entry in self.G1b_symbol_used_in_ref:

                synonym_type_id = super(ChadoGene, self).cvterm_query('synonym type', 'symbol', self.session)
                symbol_used_in_ref_synonym_id = super(ChadoGene, self).synonym_id_from_synonym_symbol(G1b_entry, synonym_type_id, self.session)

                self.current_query_source = G1b_entry
                self.current_query = 'Deleting feature synonym \'%s\'.' % (G1b_entry[FIELD_VALUE])
                log.info(self.current_query)

                filters = (
                    FeatureSynonym.pub_id == self.pub_id,
                    FeatureSynonym.feature_id == self.gene.feature_id,
                    FeatureSynonym.synonym_id == symbol_used_in_ref_synonym_id
                )

                results = self.session.query(FeatureSynonym).\
                    filter(*filters).\
                    delete()

        else:  # Normal loading for G1b only occurs if we don't have a !d flag.
            if self.bang_c == 'G1b':
                # Clear the field if we have a !c
                self.current_query_source = self.G1b_symbol_used_in_ref
                self.current_query = 'Removing all previous entries for field \'%s\' and loading new data.' % (self.bang_c)
                log.debug(self.current_query)

                # Find all FeatureSynonyms matching a specific pub, feature, and synonym type ("symbol").
                filters = (
                    FeatureSynonym.pub_id == self.pub.pub_id,
                    FeatureSynonym.feature_id == self.gene.feature_id,
                    Synonym.type_id == Cvterm.cvterm_id,
                    Cvterm.name == 'symbol',
                    FeatureSynonym.synonym_id == Synonym.synonym_id,
                )

                results = self.session.query(FeatureSynonym, Synonym.type_id, Cvterm.cvterm_id, Cvterm.name).\
                    filter(*filters).\
                    all()

                for item in results:
                    self.session.delete(item.FeatureSynonym)
            if self.G1b_symbol_used_in_ref is not None:
                for G1b_entry in self.G1b_symbol_used_in_ref:

                    synonym_type_id = super(ChadoGene, self).cvterm_query('synonym type', 'symbol', self.session)

                    self.current_query_source = G1b_entry
                    self.current_query = 'Querying for \'%s\'.' % (G1b_entry[FIELD_VALUE])
                    log.debug(self.current_query)

                    # Get one or create the synonym.
                    synonym = get_or_create(
                        self.session, Synonym,
                        synonym_sgml=G1b_entry[FIELD_VALUE],
                        name=G1b_entry[FIELD_VALUE],
                        type_id=synonym_type_id)

                    # Check if our symbol is the current symbol for the feature.
                    is_current = self.is_current_symbol(G1b_entry)

                    # Get one or create the feature_synonym relationship.
                    get_or_create(
                        self.session, FeatureSynonym,
                        feature_id=self.gene.feature_id,
                        is_current=is_current,
                        pub_id=self.pub.pub_id,
                        is_internal=False,
                        synonym_id=synonym.synonym_id
                    )

    def load_content(self):

        # Required querying and loading.
        self.gene = self.feature_from_feature_name(self.G1a_symbol_in_FB[FIELD_VALUE], self.session)
        self.pub = self.pub_from_fbrf(self.P22_FlyBase_reference_ID, self.session)
        log.info("Loading content for gene {} in pub {}.".format(self.gene.uniquename, self.pub.uniquename))

        get_or_create(
            self.session, FeaturePub,
            feature_id=self.gene.feature_id,
            pub_id=self.pub.pub_id)

        # Optional loading.
        if self.bang_c is not None:
            log.info('Found !c entry: {}'.format(self.bang_c))
        else:
            log.info('No !c entries found.')

        if self.bang_d is not None:
            log.info('Found !d entry: {}'.format(self.bang_d))
        else:
            log.info('No !d entries found.')

        if self.G1b_symbol_used_in_ref is not None or self.bang_c == 'G1b' or self.bang_d == 'G1b':
            self.process_G1b_symbols()
