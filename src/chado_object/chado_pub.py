"""
.. module:: chado_pub
   :synopsis: The "pub" ChadoObject.

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
import re
from .chado_base import ChadoObject, FIELD_VALUE
from chado_object.chado_exceptions import ValidationError
from harvdev_utils.production import (
    Cv, Cvterm, Pub, Pubprop, Pubauthor
)
from harvdev_utils.chado_functions import get_or_create

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

    def get_P1_cvterm_and_validate(self, pub):
        """
        https://svn.flybase.org/flybase-cam/Peeves/doc/specs/pub/P1.txt
        ### Checks:

        To be valid:

        * The value must be a valid term (i.e. does not have is_obsolete: true)
          from flybase_controlled_vocabulary.obo and
        * the value must be in the 'q' namespace and
        * the value must not be either 'compendium' or 'journal'.

        If !c is used:

          * P22 must contain a valid FBrf and
          * the value given in P1 must be different from the value
            stored in Chado for the publication specified by the value given in P22.

        If !c is not used:

        * if P22 contains a valid FBrf, either:
        * the value given in P1 must be identical to the value
          stored in Chado for the publication specified by the value given in P22 or
        * P1 must contain a valid value and no value is stored in

        Chado for the publication specified by the value given in P22;
          * if P22 is 'new', P1 must a contain valid value.
          * if P22 is 'unattributed', P1 must be empty
        """
        # TODO: bang c/d field stuff
        self.current_query_source = self.P1_type
        self.current_query = 'Querying for cvterm {} with cv of pub type\'%s\'.' % (self.P1_type[FIELD_VALUE])

        cvterm = self.session.query(Cvterm).join(Cv).filter(Cvterm.cv_id == Cv.cv_id,
                                                            Cvterm.name == self.P1_type[FIELD_VALUE],
                                                            Cv.name == 'pub type',
                                                            Cvterm.is_obsolete == 0).one()

        if pub:
            old_cvterm = self.session.query(Cvterm).join(Cv).join(Pubprop).\
                            filter(Cvterm.cv_id == Cv.cv_id,
                                   Pubprop.type_id == Cvterm.cvterm_id,
                                   Cv.name == 'pub type',
                                   Pubprop.pub_id == pub.pub_id,
                                   Cvterm.is_obsolete == 0).one_or_none()
            if not old_cvterm:
                # good, does not have a previous result so happy to continue
                return cvterm
            if old_cvterm.cvterm_id != cvterm.cvterm_id:
                self.current_query = 'Cvterm "{}" is not the same as previous {}\n'.format(self.P1_type[FIELD_VALUE], old_cvterm.name)
                self.current_query += 'Not allowed to change P1 if it already had one.'
                raise ValidationError()
        return cvterm

    def get_pub(self):
        """
        get pub or create pub if new.
        returns None or the pub to be used.
        """
        if self.P22_FlyBase_reference_ID[FIELD_VALUE] != 'new':
            pub = super(ChadoPub, self).pub_from_fbrf(self.P22_FlyBase_reference_ID, self.session)
        else:
            pub = None

        if self.P1_type:
            P1_cvterm = self.get_P1_cvterm_and_validate(pub)

        if self.P22_FlyBase_reference_ID[FIELD_VALUE] != 'new':
            pub = self.pub_from_fbrf(self.P22_FlyBase_reference_ID, self.session)
        else:
            if not P1_cvterm:  # ErrorTracking already knows, so just return.
                return None
            log.info("Creating new publication")

            # A trigger will swap out FBrf:temp_0 to the next rf in the sequence.
            pub = get_or_create(self.session, Pub, title=self.P16_title[FIELD_VALUE],
                                type_id=P1_cvterm.cvterm_id, uniquename='FBrf:temp_0')
            log.info(pub)
            log.info("New pub created with fbrf {}.".format(pub.uniquename))
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
            log.info('Drosophila pub, so no need to set NOT dros flag.')

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
            if fields.group(2):
                givennames = fields.group(2)

        self.current_query_source = author
        self.current_query = "Author get/create: {}.".format(author[FIELD_VALUE])
        author = get_or_create(
            self.session, Pubauthor,
            pub_id=self.pub.pub_id,
            surname=surname,
            givennames=givennames
        )
        return author

    def load_pubprop(self, cv_name, cv_term_name, value_to_add_tuple):
        """
        From a given cv and cvterm name add the pubprop with value in tuple.
        If cv or cvterm do not exist create an error and return.
        """
        self.current_query_source = value_to_add_tuple
        self.current_query = "Looking up cvterm: {} {}.".format(cv_name, cv_term_name)
        cv_term_id = super(ChadoPub, self).cvterm_query(cv_name, cv_term_name, self.session)

        self.current_query_source = value_to_add_tuple
        self.current_query = 'Querying for FBrf \'%s\'.' % (value_to_add_tuple[FIELD_VALUE])
        log.info(self.current_query)

        pub_prop = get_or_create(
            self.session, Pubprop,
            pub_id=self.pub.pub_id,
            value=value_to_add_tuple[FIELD_VALUE],
            type_id=cv_term_id
        )
        return pub_prop
