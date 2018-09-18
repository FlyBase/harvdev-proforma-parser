"""
.. module:: chado_pub
   :synopsis: The "pub" ChadoObject. 

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
from .chado_base import ChadoObject

from model.base import Base
from model.tables import *
from model.constructed import *
from sqlalchemy import func

import logging
from datetime import datetime

log = logging.getLogger(__name__)

class ChadoPub(ChadoObject):
    def __init__(self, params):
        log.info('Initializing ChadoPub object.')
        # Query tracking
        self.current_query = None

        # Metadata
        self.filename = params['file_metadata'].get('filename')
        self.filename_short = params['file_metadata'].get('filename')
        self.curator_fullname = params['file_metadata'].get('curator_fullname')
        self.proforma_start_line_number = params['file_metadata'].get('proforma_start_line_number')
        
        # Data
        self.bang_c = params.get('bang_c')
        self.P19_internal_notes = params['fields_values'].get('P19')
        self.P22_FlyBase_reference_ID = params['fields_values'].get('P22')
        self.P40_flag_cambridge = params['fields_values'].get('P40')
        self.P41_flag_harvard = params['fields_values'].get('P41')

        super(ChadoPub, self).__init__()

    def obtain_session(self, session):
        self.session = session

    def load_content(self):
        self.pub_id = super(ChadoPub, self).pub_id_from_fbrf(self.P22_FlyBase_reference_ID, self.session)
        
        if self.P19_internal_notes is not None:
            self.load_pubprops('pubprop type', 'internalnotes', self.P19_internal_notes)
        else:
            log.info('No internal notes found, skipping internal notes transaction.')

        if self.P40_flag_cambridge is not None:
            for cam_entry in self.P40_flag_cambridge:
                self.load_pubprops('pubprop type', 'cam_flag', cam_entry)
        else:
            log.info('No Cambridge flags found, skipping Cambridge flags transaction.')

        if self.P41_flag_harvard is not None:
            for harv_entry in self.P41_flag_harvard:
                self.load_pubprops('pubprop type', 'harv_flag', harv_entry)
        else:
            log.info('No Harvard flags found, skipping Harvard flags transaction.')

        timestamp = datetime.now().strftime('%c')
        curated_by_string = 'Curator: %s;Proforma: %s;timelastmodified: %s' % (self.curator_fullname, self.filename_short, timestamp)
        log.info('Curator string assembled as:')
        log.info('%s' % (curated_by_string))
        # value_to_add = curated_by_string
        # self.load_pubprops(session, 'pubprop type', 'curated_by', value_to_add)

    def load_pubprops(self, cv_name, cv_term_name, value_to_add_tuple):
        cv_term_id = super(ChadoPub, self).cvterm_query(cv_name, cv_term_name, self.session)

        self.current_query_source = value_to_add_tuple
        self.current_query = 'Querying for FBrf \'%s\'.' % (value_to_add_tuple[1])
        log.info(self.current_query)

        filters = (
            Pubprop.pub_id == self.pub_id,
            Pubprop.value == value_to_add_tuple[1],
            Pubprop.type_id == cv_term_id
        )

        filters_for_max_rank = (
            Pubprop.pub_id == self.pub_id,
            Pubprop.type_id == cv_term_id
        )
            
        exists = self.session.query(Pubprop.value).\
                        filter(*filters).\
                        one_or_none()
        
        if exists is not None:
            log.info('Previous %s found, update not required.' % (cv_term_name))
        else:
            log.info('Inserting new %s.' % (cv_term_name))
            max_rank = self.session.query(func.max(Pubprop.rank)).\
                filter(*filters_for_max_rank).\
                one()

            new_max_rank = None
            if max_rank[0] is None: # If we've never inserted a pubprop of this type before.
                new_max_rank = 0
            else:
                new_max_rank = max_rank[0] + 1

            new_notes = Pubprop(pub_id = self.pub_id, 
                                value = value_to_add_tuple[1], 
                                type_id = cv_term_id, 
                                rank = new_max_rank
            )

            session.add(new_notes)