"""
.. module:: chado_gene
   :synopsis: The "gene" ChadoObject. 

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
from .chado_base import ChadoObject

from model.base import Base
from model.tables import *
from model.constructed import *
from sqlalchemy import func

import logging
log = logging.getLogger(__name__)

class ChadoGene(ChadoObject):
    def __init__(self, params):
        log.info('Initializing ChadoGene object.')

        # Query tracking
        self.current_query = None

        # Metadata
        self.filename = params['file_metadata'].get('filename')
        self.filename_short = params['file_metadata'].get('filename')
        self.curator_fullname = params['file_metadata'].get('curator_fullname')
        self.proforma_start_line_number = params['file_metadata'].get('proforma_start_line_number')
        
        # Data
        self.bang_c = params.get('bang_c')

        self.P22_FlyBase_reference_ID = params['fields_values'].get('P22')

        self.G1a_symbol_in_FB = params['fields_values'].get('G1a')
        self.G1b_symbol_used_in_ref = params['fields_values'].get('G1b')
        self.G2b_name_used_in_ref =  params['fields_values'].get('G2b')

        super(ChadoGene, self).__init__()

    def obtain_session(self, session):
        self.session = session

    def is_current_symbol(self, G1b_entry):
            log.info('Checking whether \'{}\' is the current symbol in Chado'.format(G1b_entry[1]))
            self.current_query_source = G1b_entry[1]
            self.current_query = 'Querying for \'%s\'.' % (G1b_entry[1])  
            log.info(self.current_query)
        
            filters = (
                Feature.is_obsolete == 'f',
                Feature.feature_id == FeatureSynonym.feature_id,
                FeatureSynonym.synonym_id == Synonym.synonym_id,
                FeatureSynonym.is_current == 't',
                Synonym.type_id == 59978,
                Feature.uniquename == self.G1a_FBgn # Queried earlier, the FBgn of the symbol.
            )

            results = self.session.query(Synonym.synonym_sgml).distinct().\
                    filter(*filters).\
                    one()      

            symbol_name_from_results = results[0]

            if symbol_name_from_results == G1b_entry[1]:
                log.info('\'{}\' matches the current symbol in Chado: \'{}\', FBgn: \'{}\'. Returning is_current = \'t\''.format(G1b_entry[1], self.G1a_symbol_in_FB[1], self.G1a_FBgn))
                return 't'
            else:
                log.info('\'{}\' does not match the current symbol in Chado: \'{}\', FBgn: \'{}\'. Returning is_current = \'f\''.format(G1b_entry[1], self.G1a_symbol_in_FB[1], self.G1a_FBgn))
                return 'f'

    def load_G1b_symbol(self):
    
        for G1b_entry in self.G1b_symbol_used_in_ref:

            synonym_type_id = super(ChadoGene, self).cvterm_query('synonym type', 'symbol', self.session)
            
            self.current_query_source = G1b_entry
            self.current_query = 'Querying for \'%s\'.' % (G1b_entry[1])            
            log.info(self.current_query)
            
            self.symbol_used_in_ref_synonym_id = super(ChadoGene, self).synonym_id_from_synonym_symbol(G1b_entry, synonym_type_id, self.session)

            is_current = self.is_current_symbol(G1b_entry)

            super(ChadoGene, self).get_one_or_create(
                self.session,
                FeatureSynonym,
                feature_id = self.symbol_in_FB_feature_id,
                is_current = is_current,
                pub_id = self.pub_id,
                is_internal = 'FALSE', 
                synonym_id = self.symbol_used_in_ref_synonym_id
            )

    def load_content(self):

        # Required Loading.
        self.symbol_in_FB_feature_id = super(ChadoGene, self).feature_id_from_feature_name(self.G1a_symbol_in_FB, self.session)
        self.pub_id = super(ChadoGene, self).pub_id_from_fbrf(self.P22_FlyBase_reference_ID, self.session)
        self.G1a_FBgn = super(ChadoGene, self).uniquename_from_feature_id(self.symbol_in_FB_feature_id, self.session)

        super(ChadoGene, self).get_one_or_create(
            self.session, 
            FeaturePub, 
            feature_id = self.symbol_in_FB_feature_id,
            pub_id = self.pub_id)

        # Optional Loading.
        if self.G1b_symbol_used_in_ref is not None:
            self.load_G1b_symbol()
