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

    def load_content(self, session):

        # Required Loading.
        self.symbol_in_FB_feature_id = super(ChadoGene, self).feature_id_from_feature_name(self.G1a_symbol_in_FB, session)
        self.pub_id = super(ChadoGene, self).pub_id_from_fbrf(self.P22_FlyBase_reference_ID, session)

        super(ChadoGene, self).get_one_or_create(
            session, 
            FeaturePub, 
            feature_id = self.symbol_in_FB_feature_id,
            pub_id = self.pub_id)

        # Optional Loading.
        if self.G1b_symbol_used_in_ref is not None:
            for G1b_entry in self.G1b_symbol_used_in_ref:

                synonym_type_id = super(ChadoGene, self).cvterm_query('synonym type', 'symbol', session)
                
                self.current_query_source = G1b_entry
                self.current_query = 'Querying for \'%s\'.' % (G1b_entry[1])            
                log.info(self.current_query)
                
                self.symbol_used_in_ref_synonym_id = super(ChadoGene, self).synonym_id_from_synonym_symbol(G1b_entry, synonym_type_id, session)

                super(ChadoGene, self).get_one_or_create(
                    session,
                    FeatureSynonym,
                    feature_id = self.symbol_in_FB_feature_id,
                    is_current = 'FALSE',
                    pub_id = self.pub_id,
                    is_internal = 'FALSE',
                    synonym_id = self.symbol_used_in_ref_synonym_id
                )