"""
.. module:: chado_pub
   :synopsis: The "pub" ChadoObject. 

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
import re
from .chado_base import ChadoObject, FIELD_VALUE
from harvdev_utils.production import *
from harvdev_utils.chado_functions import get_or_create

from sqlalchemy import func

import logging
from datetime import datetime

log = logging.getLogger(__name__)

class ChadoPub(ChadoObject):
    def __init__(self, params):
        log.info('Initializing ChadoPub object.')
        
        self.proforma_start_line_number = params.get('proforma_start_line_number')

        # Data
        self.bang_c = params.get('bang_c')
        self.P19_internal_notes = params['fields_values'].get('P19')
        self.P22_FlyBase_reference_ID = params['fields_values'].get('P22')
        self.P40_flag_cambridge = params['fields_values'].get('P40')
        self.P41_flag_harvard = params['fields_values'].get('P41')
        self.P1_type = params['fields_values'].get('P1')
        self.P16_title = params['fields_values'].get('P16')
        self.P12_authors = params['fields_values'].get('P12')
        self.P10_pub_date = params['fields_values'].get('P10')
        # Values queried later, placed here for reference purposes.
        self.pub_id = None

        # Initiate the parent.
        super(ChadoPub, self).__init__(params)

         
    def obtain_session(self, session):
        self.session = session

    def load_content(self):
        if self.P22_FlyBase_reference_ID[FIELD_VALUE] != 'new':
            self.pub_id = super(ChadoPub, self).pub_id_from_fbrf(self.P22_FlyBase_reference_ID, self.session)
        else:
            log.info("creating new publication")
            try:
                cvterm = self.session.query(Cvterm).join(Dbxref).filter(Dbxref.accession == self.P1_type[FIELD_VALUE]).one()
                log.debug("bob is {}".format(cvterm.cvterm_id))
            except Exception as e:
                log.debug("Error {}".format(e))
            # A trigger will swap out FBrf:temp_0 to the next rf in the sequence.
            self.pub_id = get_or_create(self.session, Pub, ret_col = 'pub_id', title = self.P16_title[FIELD_VALUE],
                                        type_id = cvterm.cvterm_id, uniquename = 'FBrf:temp_0')

        if self.P19_internal_notes is not None:
            self.load_pubprops('pubprop type', 'internalnotes', self.P19_internal_notes)
        else:
            log.info('No internal notes found, skipping internal notes transaction.')

        if self.P12_authors is not None:
            for author in self.P12_authors:
                self.load_author(author)

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


    def load_author(self, author):
        pattern = r"""            
            ^(\S+)      # None space surname
            \s+?        # delimiting space
            (.*)?       # optional given names can havingspaces etc in them"""
        fields = re.search(pattern, author[FIELD_VALUE], re.VERBOSE)
        givennames = None
        if fields:
            if fields.group(1):
                surname = fields.group(1)
            else:
                #raise error
                pass
            if fields.group(2):
                givennames = fields.group(2)
        else:
            # rasie error
            pass

        author_id = get_or_create(
            self.session, Pubauthor,
            ret_col = 'pubauthor_id',
            pub_id = self.pub_id,
            surname = surname,
            givennames = givennames
        )
        return author_id

    def load_pubprops(self, cv_name, cv_term_name, value_to_add_tuple):
        cv_term_id = super(ChadoPub, self).cvterm_query(cv_name, cv_term_name, self.session)

        self.current_query_source = value_to_add_tuple
        self.current_query = 'Querying for FBrf \'%s\'.' % (value_to_add_tuple[FIELD_VALUE])
        log.info(self.current_query)

        get_or_create(
            self.session, Pubprop,
            pub_id = self.pub_id,
            value = value_to_add_tuple[FIELD_VALUE],
            type_id = cv_term_id
        )