"""
.. module:: chado_pub
   :synopsis: The "pub" ChadoObject. 

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
import re
from .chado_base import ChadoObject, FIELD_VALUE, LINE_NUMBER
from error.error_tracking import ErrorTracking
from harvdev_utils.production import *
from harvdev_utils.chado_functions import get_or_create

from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

import logging
from datetime import datetime

log = logging.getLogger(__name__)

class ChadoPub(ChadoObject):
    def __init__(self, params):
        log.info('Initializing ChadoPub object.')
        
        self.proforma_start_line_number = params.get('proforma_start_line_number')

        # Data
        self.bang_c = params.get('bang_c')
        self.P1_type = params['fields_values'].get('P1')
        self.P3_volume_number = params['fields_values'].get('P3')
        self.P4_issue_number = params['fields_values'].get('P4')
        self.P10_pub_date = params['fields_values'].get('P10')
        self.P11a_page_range = params['fields_values'].get('P11a')
        self.P12_authors = params['fields_values'].get('P12')
        self.P13_language = params['fields_values'].get('P13')
        self.P14_additional_language = params['fields_values'].get('P14')
        self.P16_title = params['fields_values'].get('P16')
        self.P18_misc_comments = params['fields_values'].get('P18')
        self.P19_internal_notes = params['fields_values'].get('P19')
        self.P22_FlyBase_reference_ID = params['fields_values'].get('P22')
        self.P23_personal_com = params['fields_values'].get('P23')
        self.P40_flag_cambridge = params['fields_values'].get('P40')
        self.P41_flag_harvard = params['fields_values'].get('P41')
        self.P45_Not_dros = params['fields_values'].get('P45')
        # Values queried later, placed here for reference purposes.
        self.pub = None

        # Initiate the parent.
        super(ChadoPub, self).__init__(params)

         
    def obtain_session(self, session):
        self.session = session

    def get_pub(self):
        """
        get or create pub if new.
        returns None or the pub_id to be used.
        """
        if self.P22_FlyBase_reference_ID[FIELD_VALUE] != 'new':
            pub = super(ChadoPub, self).pub_from_fbrf(self.P22_FlyBase_reference_ID, self.session)
        else:
            log.info("creating new publication")
            try:
                cvterm = self.session.query(Cvterm).join(Dbxref).filter(Dbxref.accession == self.P1_type[FIELD_VALUE]).one()
            except NoResultFound:
                log.debug(self.P1_type)
                log.debug(LINE_NUMBER)
                ErrorTracking(self.filename,
                              self.P1_type[LINE_NUMBER],
                              'Cvterm "{}" Does not exist'.format(self.P1_type[FIELD_VALUE]),
                              'Dbxref lookup failed.')
                return None
            # A trigger will swap out FBrf:temp_0 to the next rf in the sequence.
            pub = get_or_create(self.session, Pub, title = self.P16_title[FIELD_VALUE],
                                type_id = cvterm.cvterm_id, uniquename = 'FBrf:temp_0')
            log.info("New pub created with fbrf {}".format(pub.uniquename))
        return pub


    def bang_c_it(self):
        """
        Delete everything wrt this pub and itself?
        """
        log.critial("Not coded !c yet")

    def update_pubprops(self):
        """
        Update all the pub props.
        """
        if self.P13_language is not None:
            self.load_pubprop('pubprop type', 'languages', self.P13_language)
        else:
            log.info('No language specified, skipping languages transaction.')
 
        if self.P14_additional_language is not None:
            self.load_pubprop('pubprop type', 'abstract_languages', self.P14_additional_language)
        else:
            log.info('No additional language specified, skipping additional language transaction.')

        if self.P19_internal_notes is not None:
            self.load_pubprop('pubprop type', 'internalnotes', self.P19_internal_notes)
        else:
            log.info('No internal notes found, skipping internal notes transaction.')

        if self.P23_personal_com is not None:
            self.load_pubprop('pubprop type', 'perscommtext', self.P23_personal_com)
        else:
            log.info('No personal communication, skipping personal communication notes transaction.')

        if self.P40_flag_cambridge is not None:
            for cam_entry in self.P40_flag_cambridge:
                self.load_pubprop('pubprop type', 'cam_flag', cam_entry)
        else:
            log.info('No Cambridge flags found, skipping Cambridge flags transaction.')

        if self.P41_flag_harvard is not None:
            for harv_entry in self.P41_flag_harvard:
                self.load_pubprop('pubprop type', 'harv_flag', harv_entry)
        else:
            log.info('No Harvard flags found, skipping Harvard flags transaction.')

        if self.P45_Not_dros is not None:
            self.load_pubprop('pubprop type', 'not_Drospub', self.P45_Not_dros)
        else:
            log.info('Drosophila pub, so no need to set NOT dros flag')

 

    def update_pub(self):
        """
        Add direct fields to the pub.
        """
        if self.P10_pub_date:
            self.pub.pyear = self.P10_pub_date[FIELD_VALUE]
        if self.P16_title:
            self.pub.title = self.P16_title[FIELD_VALUE]
        if self.P11a_page_range:
            self.pub.pages = self.P11a_page_range[FIELD_VALUE]
        if self.P3_volume_number:
            self.pub.volume = self.P3_volume_number[FIELD_VALUE]
        if self.P4_issue_number:
            self.pub.issue = self.P4_issue_number[FIELD_VALUE]


    def load_content(self):
        
        self.pub = self.get_pub()
        if not self.pub:
            return
 
        # bang c first as this trumps all things
        if self.bang_c:
            self.bang_c_it()
            return

        # Update the direct column data in Pub
        self.update_pub()

        self.update_pubprops()

        if self.P12_authors is not None:
            for author in self.P12_authors:
                self.load_author(author)

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

        author = get_or_create(
            self.session, Pubauthor,
            pub_id = self.pub.pub_id,
            surname = surname,
            givennames = givennames
        )
        return author

    def load_pubprop(self, cv_name, cv_term_name, value_to_add_tuple):
        """
        From a given cv and cvterm name add the pubprop with value in tuple.
        If cv or cvterm do not exist create an error and return.
        """
        log.info("Adding pub prop to {} {} {}".format(cv_name, cv_term_name, value_to_add_tuple[FIELD_VALUE]))
        try:
            cv_term_id = super(ChadoPub, self).cvterm_query(cv_name, cv_term_name, self.session)
        except NoResultFound:
            ErrorTracking(self.filename,
                          value_to_add_tuple[LINE_NUMBER],
                          'Cvterm "{}" Does not exist'.format(cv_term_name),
                          'For cv "{}".'.format(cv_name))
            return None
        self.current_query_source = value_to_add_tuple
        self.current_query = 'Querying for FBrf \'%s\'.' % (value_to_add_tuple[FIELD_VALUE])
        log.info(self.current_query)

        pub_prop = get_or_create(
            self.session, Pubprop,
            pub_id = self.pub.pub_id,
            value = value_to_add_tuple[FIELD_VALUE],
            type_id = cv_term_id
        )
        return pub_prop