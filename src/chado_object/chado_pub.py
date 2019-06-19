"""
.. module:: chado_pub
   :synopsis: The "pub" ChadoObject.

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
import re
from .chado_base import ChadoObject, FIELD_VALUE
from chado_object.chado_exceptions import ValidationError
from harvdev_utils.production import (
    Cv, Cvterm, Pub, Pubprop, Pubauthor, PubRelationship, Db, Dbxref, PubDbxref
)
from harvdev_utils.chado_functions import get_or_create

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
        self.P2_multipub = params['fields_values'].get('P2')
        self.P3_volume_number = params['fields_values'].get('P3')
        self.P4_issue_number = params['fields_values'].get('P4')
        self.P10_pub_date = params['fields_values'].get('P10')
        self.P11a_page_range = params['fields_values'].get('P11a')
        self.P11b_url = params['fields_values'].get('P11b')
        self.P11c_san = params['fields_values'].get('P11c')
        self.P11d_doi = params['fields_values'].get('P11d')
        self.P12_authors = params['fields_values'].get('P12')
        self.P13_language = params['fields_values'].get('P13')
        self.P14_additional_language = params['fields_values'].get('P14')
        self.P16_title = params['fields_values'].get('P16')
        self.P18_misc_comments = params['fields_values'].get('P18')
        self.P19_internal_notes = params['fields_values'].get('P19')
        self.P22_FlyBase_reference_ID = params['fields_values'].get('P22')
        self.P23_personal_com = params['fields_values'].get('P23')
        self.P26_pubmed_id = params['fields_values'].get('P26')
        self.P28_pubmed_central_id = params['fields_values'].get('P28')
        self.P29_isbn = params['fields_values'].get('P29')
        self.P30_also_published_as = params['fields_values'].get('P30')
        self.P31_related_publications = params['fields_values'].get('P31')
        self.P32_make_secondary = params['fields_values'].get('P32')
        self.P34_abstract = params['fields_values'].get('P34')
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

    def get_related_pub(self, tuple):
        """
        from the fbrf tuple get the pub
        """
        self.current_query_source = tuple
        self.current_query = "Looking up pub: {}.".format(tuple[FIELD_VALUE])
        return self.session.query(Pub).filter(Pub.uniquename == tuple[FIELD_VALUE]).one()

    def add_relationship(self, subject_pub, object_pub, cvterm, query_source):
        """
        add relationship bewteen the two pubs with cvterm specified
        """
        # look up the cvterm
        self.current_query_source = query_source
        self.current_query = "Querying for cvterm '{}' with cv of 'pub relationship type'.".format(cvterm)
        cvterm = self.session.query(Cvterm).join(Cv).filter(Cv.name == 'pub relationship type',
                                                            Cvterm.name == cvterm,
                                                            Cvterm.is_obsolete == 0).one()
        # now add the relationship
        get_or_create(self.session, PubRelationship,
                      subject_id=subject_pub.pub_id,
                      object_id=object_pub.pub_id,
                      type_id=cvterm.cvterm_id)

    def make_obsolete(self, pub):
        """
        Make the pub obsolete
        """
        pub.is_obsolete = True

    def get_parent_pub(self, pub):
        """
        Get the parent pub.
        Return None if it does not have one. This is okay.
        """
        self.current_query_source = pub.uniquename
        self.current_query = "Querying for cvterm 'published_in' with cv of 'pub relationship type'."
        cvterm = self.session.query(Cvterm).join(Cv).filter(Cv.name == 'pub relationship type',
                                                            Cvterm.name == 'published_in',
                                                            Cvterm.is_obsolete == 0).one()

        pr = self.session.query(PubRelationship).\
            join(Pub, Pub.pub_id == PubRelationship.object_id).\
            join(Cvterm).filter(PubRelationship.subject_id == pub.pub_id,
                                PubRelationship.type_id == cvterm.cvterm_id).one_or_none()
        log.debug("PR => {}".format(pr))
        log.debug(dir(pr))
        if not pr:
            return None
        return self.session.query(Pub).filter(Pub.pub_id == pr.object_id).one()

    def process_multipub(self, tuple):
        """
        Get P2 pub via the  miniref.
        If P22 is new, NO further checks needed.
        If P22 NOT new then
              if it already has a relationship then check it is the same
              if none exists no further checks needed.
        Add relationship
        """

        self.current_query_source = tuple
        self.current_query = "Querying for P2 miniref '{}'.".format(tuple[FIELD_VALUE])
        p2_pub = self.session.query(Pub).filter(Pub.miniref == tuple[FIELD_VALUE]).one()

        if self.P22_FlyBase_reference_ID[FIELD_VALUE] != 'new':
            old_parent = self.get_parent_pub(self.pub)
            if old_parent:
                log.debug("old parent is {}".format(old_parent))
                if old_parent.pub_id != p2_pub.pub_id:
                    old_name = old_parent.miniref
                    if not old_name:
                        old_name = old_parent.uniquename
                    self.current_query = 'P22 has a different parent {} than the one listed {} ()\n'.format(old_name, p2_pub.miniref, p2_pub.uniquename)
                    self.current_query += 'Not allowed to change P2 if it already has one. without !c'
                    raise ValidationError()
                else:
                    return
        # Add the relationship as all is good.
        self.add_relationship(self.pub, p2_pub, 'published_in', tuple)

    def process_related(self):
        """
        Process P30, P31 and P32 (also pub as, related pub, make secondary)
        Each is a list so process accordingly.
        """
        if self.P2_multipub:
            self.process_multipub(self.P2_multipub)
        if self.P30_also_published_as:
            for fbrf in self.P30_also_published_as:
                pub = self.get_related_pub(fbrf)
                self.add_relationship(self.pub, pub, 'also_in', self.P30_also_published_as)
        if self.P31_related_publications:
            for fbrf in self.P31_related_publications:
                pub = self.get_related_pub(fbrf)
                self.add_relationship(self.pub, pub, 'related_to', self.P31_related_publications)
        if self.P32_make_secondary:
            for fbrf in self.P32_make_secondary:
                pub = self.get_related_pub(fbrf)
                self.make_obsolete(pub)

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

    def load_pubprop_singles(self):
        """
        Process the none list pubprops.

        pub_data => [[key, pubprop name, debug message],...]
        """
        pub_data = [[self.P11b_url, 'URL', 'No URL specified, skipping URL'],
                    [self.P13_language, 'languages', 'No language specified, skipping languages transaction.'],
                    [self.P14_additional_language, 'abstract_languages', 'No additional language specified, skipping additional language transaction.'],
                    [self.P19_internal_notes, 'internalnotes', 'No internal notes found, skipping internal notes transaction.'],
                    [self.P23_personal_com, 'perscommtext', 'No personal communication, skipping personal communication notes transaction.'],
                    [self.P34_abstract, 'pubmed_abstract',  'No Abtract, skipping addition of abstract.'],
                    [self.P45_Not_dros, 'not_Drospub', 'Drosophila pub, so no need to set NOT dros flag.']]
        for row in pub_data:
            if row[0]:
                self.load_pubprop('pubprop type', row[1], row[0])
            else:
                log.debug(row[2])

    def update_pubprops(self):
        """
        Update all the pub props.
        """
        self.load_pubprop_singles()

        if self.P40_flag_cambridge is not None:
            for cam_entry in self.P40_flag_cambridge:
                self.load_pubprop('pubprop type', 'cam_flag', cam_entry)
        else:
            log.debug('No Cambridge flags found, skipping Cambridge flags transaction.')

        if self.P41_flag_harvard is not None:
            for harv_entry in self.P41_flag_harvard:
                self.load_pubprop('pubprop type', 'harv_flag', harv_entry)
        else:
            log.debug('No Harvard flags found, skipping Harvard flags transaction.')

    def do_P11_checks(self):
        """
        Check if P11 already has a value. If it matches all well and good.
        If not throw an exception. (!c must be used here)
        """

        """
        If existing pages retrieved from chado via FBrf:
        P11a:  Trying to change <chado-pages> to '<your-pages>' but it isn't yet in Chado.
               # Bang C i guess, not implenented yet ??????????? the one above

        P11a:  Trying to set <pages> to '<your-pages>' but it is '<chado-pages>' in Chado.
        """
        if self.P22_FlyBase_reference_ID[FIELD_VALUE] != 'new':
            if self.pub.pages and self.P11a_page_range and self.pub.pages != self.P11a_page_range[FIELD_VALUE]:
                self.current_query_source = self.P11a_page_range
                self.current_query = 'P11a page range "{}" does not match "{}" already in chado.\n'.format(self.P11a_page_range, self.pub.pages)
                raise ValidationError()

    def update_dbxrefs(self):
        """
        dbxref fiedls to update.
        """
        data = [[self.P11c_san, 'GB'],
                [self.P11d_doi, 'DOI'],
                [self.P26_pubmed_id, 'pubmed'],
                [self.P28_pubmed_central_id, 'PMCID'],
                [self.P29_isbn, 'isbn']]
        for row in data:
            if row[0]:
                self.load_pubdbxref(row[1], row[0])

    def extra_checks(self):
        """
        Not all tests can be done in the validator as if the P11x is blank no checks are done.
        """
        self.do_P11_checks()

    def update_pub(self):
        """
        Add direct fields to the pub.
        """
        if self.P10_pub_date:
            self.pub.pyear = self.P10_pub_date[FIELD_VALUE]
        if self.P11a_page_range:
            self.pub.pages = self.P11a_page_range[FIELD_VALUE]
        if self.P16_title:
            self.pub.title = self.P16_title[FIELD_VALUE]
        if self.P3_volume_number:
            self.pub.volume = self.P3_volume_number[FIELD_VALUE]
        if self.P4_issue_number:
            self.pub.issue = self.P4_issue_number[FIELD_VALUE]

    def load_content(self):
        """
        Main processing routine
        """
        self.pub = self.get_pub()
        if not self.pub:
            return
        self.extra_checks()

        # bang c first as this trumps all things
        if self.bang_c:
            self.bang_c_it()
            return

        # Update the direct column data in Pub
        self.update_pub()

        self.process_related()
        self.update_pubprops()
        self.update_dbxrefs()

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

        self.current_query = 'Querying for FBrf \'%s\'.' % (value_to_add_tuple[FIELD_VALUE])
        log.debug(self.current_query)

        pub_prop = get_or_create(
            self.session, Pubprop,
            pub_id=self.pub.pub_id,
            value=value_to_add_tuple[FIELD_VALUE],
            type_id=cv_term_id
        )
        return pub_prop

    def load_pubdbxref(self, db_name, value_to_add_tuple):
        """
        Add dbxref to the pub (self.pub)
        """
        self.current_query_source = value_to_add_tuple
        self.current_query = "Looking up db: {}.".format(db_name)
        db = self.session.query(Db).filter(Db.name == db_name).one()

        self.current_query = "Looking up dbxref: {}.".format(value_to_add_tuple[FIELD_VALUE])
        dbxref = get_or_create(
            self.session, Dbxref,
            accession=value_to_add_tuple[FIELD_VALUE],
            db_id=db.db_id
        )

        self.current_query = 'Adding \'%s\' to \'%s\'.' % (dbxref.accession, self.pub.uniquename)
        log.debug(self.current_query)

        get_or_create(
            self.session, PubDbxref,
            pub_id=self.pub.pub_id,
            dbxref_id=dbxref.dbxref_id
        )
