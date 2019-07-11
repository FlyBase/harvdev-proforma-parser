"""
.. module:: chado_pub
   :synopsis: The "pub" ChadoObject.

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
import re
import os
import yaml
from .chado_base import ChadoObject, FIELD_VALUE
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
        #########################################
        # Set up how to process each tpe of input
        #########################################
        self.type_dict = {'direct': self.load_direct,
                          'pubauthor': self.load_author,
                          'relationship': self.load_relationship,
                          'pubprop': self.load_pubprop,
                          'dbxref': self.load_dbxref,
                          'ignore': self.ignore,
                          'obsolete': self.make_obsolete}

        self.proforma_start_line_number = params.get('proforma_start_line_number')

        ############################################################
        # Get processing info and data to be processed.
        ############################################################
        yml_file = os.path.join(os.path.dirname(__file__), 'yml/publication.yml')
        self.process_data = yaml.load(open(yml_file))
        for key in self.process_data:
            self.process_data[key]['data'] = params['fields_values'].get(key)
            if self.process_data[key]['data']:
                log.debug("{}: {}".format(key, self.process_data[key]))
        self.bang_c = params.get('bang_c')

        #################################################
        # various tests use this so create an easy lookup
        #################################################
        if self.process_data['P22']['data'][FIELD_VALUE] == "new":
            self.newpub = True
        else:
            self.newpub = False

        ###########################################################
        # Values queried later, placed here for reference purposes.
        ############################################################
        self.pub = None   # All other proforma need a reference to a pub
        self.parent_pub = None  # Various checks refer to this so just get it once
        self.gene = None  # Needed reference for alleles

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

        p1_data = self.process_data['P1']['data']
        if p1_data[FIELD_VALUE] in ('journal', 'compendium'):
            self.critical_error(p1_data, 'Not allowed to have the value "journal" or "compendium"')

        self.current_query_source = p1_data
        self.current_query = 'Querying for cvterm {} with cv of pub type\'%s\'.' % (p1_data[FIELD_VALUE])

        cvterm = self.session.query(Cvterm).join(Cv).filter(Cvterm.cv_id == Cv.cv_id,
                                                            Cvterm.name == p1_data[FIELD_VALUE],
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
                message = 'Cvterm "{}" is not the same as previous "{}". '.format(p1_data[FIELD_VALUE], old_cvterm.name)
                message += 'Not allowed to change P1 if it already had one.'
                self.critical_error(p1_data, message)
        return cvterm

    def get_related_pub(self, tuple):
        """
        from the fbrf tuple get the pub
        """
        self.current_query_source = tuple
        self.current_query = "Looking up pub: {}.".format(tuple[FIELD_VALUE])
        log.debug("Looking up pub: {}.".format(tuple[FIELD_VALUE]))
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

    def check_multipub(self, old_parent, tuple):
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

        if not self.newpub and old_parent:
            log.debug("old parent is {}".format(old_parent))
            if old_parent.pub_id != p2_pub.pub_id:
                old_name = old_parent.miniref
                if not old_name:
                    old_name = old_parent.uniquename
                message = 'P22 has a different parent "{}" than the one listed "{}" "{}"\n'.format(old_name, p2_pub.miniref, p2_pub.uniquename)
                message += 'Not allowed to change P2 if it already has one. without !c'
                self.critical_error(self.process_data['P22']['data'], message)
                return

    def get_pub(self):
        """
        get pub or create pub if new.
        returns None or the pub to be used.
        """
        if not self.newpub:
            pub = super(ChadoPub, self).pub_from_fbrf(self.process_data['P22']['data'], self.session)
        else:
            pub = None

        if self.process_data['P1']['data']:
            P1_cvterm = self.get_P1_cvterm_and_validate(pub)

        if not self.newpub:
            pub = self.pub_from_fbrf(self.process_data['P22']['data'], self.session)
        else:
            if not P1_cvterm:  # ErrorTracking already knows, so just return.
                return None
            log.info("Creating new publication")

            # A trigger will swap out FBrf:temp_0 to the next rf in the sequence.
            pub = get_or_create(self.session, Pub, type_id=P1_cvterm.cvterm_id, uniquename='FBrf:temp_0')
            log.info(pub)
            log.info("New pub created with fbrf {}.".format(pub.uniquename))
        return pub

    def bang_c_it(self):
        """
        Delete everything wrt this pub and itself?
        """
        log.critical("Not coded !c yet")

    # def load_pubprop_singles(self):
    #     """
    #     Process the none list pubprops.

    #     pub_data => [[key, pubprop name, debug message],...]
    #     """
    #     pub_data = [[self.P11b_url, 'URL', 'No URL specified, skipping URL'],
    #                 [self.P13_language, 'languages', 'No language specified, skipping languages transaction.'],
    #                 [self.P14_additional_language, 'abstract_languages', 'No additional language specified, skipping additional language transaction.'],
    #                 [self.P19_internal_notes, 'internalnotes', 'No internal notes found, skipping internal notes transaction.'],
    #                 [self.P23_personal_com, 'perscommtext', 'No personal communication, skipping personal communication notes transaction.'],
    #                 [self.P34_abstract, 'pubmed_abstract',  'No Abtract, skipping addition of abstract.'],
    #                 [self.P44_disease_notes, 'diseasenotes', 'No disease notes, so skipping disease notes transactions.'],
    #                 [self.P45_Not_dros, 'not_Drospub', 'Drosophila pub, so no need to set NOT dros flag.'],
    #                 [self.P46_graphical_abstract, 'graphical_abstract', 'No graphical abstracts, so skipping.']]

    #     for row in pub_data:
    #         if row[0]:
    #             self.load_pubprop('pubprop type', row[1], row[0])
    #         else:
    #             log.debug(row[2])

    # def load_pubprops_lists(self):
    #     """
    #     Update the pubprops that can be lists
    #     """
    #     data_list = [
    #         [self.P38_deposited_file, 'deposited_files', 'No deposited files, so skipping.'],
    #         [self.P40_flag_cambridge, 'cam_flag', 'No Cambridge flags found, skipping Cambridge flags transaction.'],
    #         [self.P41_flag_harvard, 'harv_flag', 'No Harvard flags found, skipping Harvard flags transaction.'],
    #         [self.P42_flag_ontologist, 'onto_flag', 'No Ontology flags found, skipping Ontology flags transaction.'],
    #         [self.P43_flag_disease, 'dis_flag', 'No Disease flags found, skipping Disease flags transaction.']]

    #     for row in data_list:
    #         if row[0]:
    #             for entry in row[0]:
    #                 self.load_pubprop('pubprop type', row[1], entry)
    #         else:
    #             log.debug(row[2])

    # def update_pubprops(self):
    #     """
    #     Update all the pub props.
    #     """
    #     self.load_pubprop_singles()
    #     self.load_pubprops_lists()

    def graphical_abstracts_check(self):
        """
        Checks within field:

        * field should be separable into two components using '/' as the split character

        TODO:  * Should check that filename is not already in chado (associated with *any* FBrf, not just the one in P22)

        Checks between fields:

        * first part of relative filepath should match the parent journal abbreviation (given either in P2 or in chado),
          with spaces/periods replaced with an underscore
        """
        pattern = r"""
            (\w+)  # pub directory
            [/]    # path divider
            (\w+)  # filename """
        P46_data = self.process_data['P46']['data']
        fields = re.search(pattern, P46_data[FIELD_VALUE], re.VERBOSE)
        if not fields:
            self.warning_error(P46_data, 'P46 does not have the format */*.')
            return

        expected_dir = self.parent_pub.miniref
        expected_dir.replace(". ", "_")
        if expected_dir != fields.group(1):
            message = "'{}' does not equal to what is expected, given its parent.".format(fields.group(1))
            message += "\nWas expecting directory to be {}.".format(expected_dir)
            self.warning_error(P46_data, message)

    def do_P11_checks(self):
        """
        Check if P11 already has a value. If it matches all well and good.
        If not throw an exception. (!c must be used here)
        """

        """  CRITICAL -- Cvterm "journal" is not the same as previous personal communication to FlyBase

        If existing pages retrieved from chado via FBrf:
        P11a:  Trying to change <chado-pages> to '<your-pages>' but it isn't yet in Chado.
               # Bang C i guess, not implenented yet ??????????? the one above

        P11a:  Trying to set <pages> to '<your-pages>' but it is '<chado-pages>' in Chado.
        """
        p11a = self.process_data['P11a']['data']
        if not self.newpub and self.bang_c != 'P11a':
            if self.pub.pages and p11a and self.pub.pages != p11a[FIELD_VALUE]:
                message = 'P11a page range "{}" does not match "{}" already in chado.\n'.format(p11a[FIELD_VALUE], self.pub.pages)
                self.critical_error(p11a, message)

    # def update_dbxrefs(self):
    #     """
    #     dbxref fiedls to update.
    #     """
    #     data = [[self.P11c_san, 'GB'],
    #             [self.P11d_doi, 'DOI'],
    #             [self.P26_pubmed_id, 'pubmed'],
    #             [self.P28_pubmed_central_id, 'PMCID'],
    #             [self.P29_isbn, 'isbn']]
    #     for row in data:
    #         if row[0]:
    #             self.load_pubdbxref(row[1], row[0])

    def extra_checks(self):
        """
        Not all tests can be done in the validator do extra ones here.
        """
        self.do_P11_checks()
        if self.process_data['P2']['data']:
            self.check_multipub(self.parent_pub, self.process_data['P2']['data'])
        if self.process_data['P46']['data']:
            self.graphical_abstracts_check()

    def load_direct(self, key):
        if 'boolean' in self.process_data[key]:
            setattr(self.pub, self.process_data[key]['name'], True)
            if 'warning' in self.process_data[key]:
                message = "Making {} {}.".format(self.process_data['P22']['data'][FIELD_VALUE], self.process_data[key]['name'])
                self.warning_error(self.process_data[key]['data'], message)
        else:
            setattr(self.pub, self.process_data[key]['name'], self.process_data[key]['data'][FIELD_VALUE])

    def load_relationship(self, key):
        for fbrf in self.process_data[key]['data']:
            if 'verify_only_on_update' not in self.process_data[key] or self.newpub:
                pub = self.get_related_pub(fbrf)
                self.add_relationship(self.pub, pub, self.process_data[key]['cvterm'], self.process_data[key]['data'])

    def load_dbxref(self, key):
        self.load_pubdbxref(self.process_data[key]['cvterm'], self.process_data[key]['data'])

    def ignore(self, key):
        pass

    def make_obsolete(self, key):
        log.debug("Inside make obsolete.")
        for fbrf in self.process_data[key]['data']:
            log.debug("Make obsolete {}".format(fbrf))
            pub = self.get_related_pub(fbrf)
            pub.is_obsolete = True

    def load_pubprop(self, key):
        log.debug("loading pubprops")
        if type(self.process_data[key]['data']) is list:
            for row in self.process_data[key]['data']:
                log.debug("loading {} {}".format(self.process_data[key]['cvterm'], row[FIELD_VALUE]))
                self.load_single_pubprop('pubprop type', self.process_data[key]['cvterm'], row)
        else:
            log.debug("loading {} {}".format(self.process_data[key]['cvterm'], self.process_data[key]['data'][FIELD_VALUE]))
            self.load_single_pubprop('pubprop type', self.process_data[key]['cvterm'], self.process_data[key]['data'])

    def load_content(self):
        """
        Main processing routine
        """

        self.pub = self.get_pub()

        self.parent_pub = self.get_parent_pub(self.pub)

        self.extra_checks()

        # bang c first as this trumps all things
        if self.bang_c:
            self.bang_c_it()
            return

        for key in self.process_data:
            if self.process_data[key]['data']:
                log.debug("Processing {}".format(self.process_data[key]['data']))
                self.type_dict[self.process_data[key]['type']](key)

        timestamp = datetime.now().strftime('%c')
        curated_by_string = 'Curator: %s;Proforma: %s;timelastmodified: %s' % (self.curator_fullname, self.filename_short, timestamp)
        log.info('Curator string assembled as:')
        log.info('%s' % (curated_by_string))

    def load_author(self, key):
        pattern = r"""
            ^(\S+)      # None space surname
            \s+?        # delimiting space
            (.*)?       # optional given names can havingspaces etc in them"""
        for author in self.process_data[key]['data']:
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

    def load_single_pubprop(self, cv_name, cv_term_name, value_to_add_tuple):
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
