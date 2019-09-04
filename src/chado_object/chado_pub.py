"""
.. module:: chado_pub
   :synopsis: The "pub" ChadoObject.

.. moduleauthor:: Ian Longden <ilongden@morgan.harvard.edu>
"""
import re
import os
from .chado_base import ChadoObject, FIELD_VALUE, FIELD_NAME
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
        ##########################################
        # Set up how to process each type of input
        ##########################################
        self.type_dict = {'direct': self.load_direct,
                          'pubauthor': self.load_author,
                          'relationship': self.load_relationship,
                          'pubprop': self.load_pubprop,
                          'dbxref': self.load_dbxref,
                          'ignore': self.ignore,
                          'obsolete': self.make_obsolete}

        self.delete_dict = {'direct': self.delete_direct,
                            'pubauthor': self.delete_author,
                            'relationship': self.delete_relationships,
                            'pubprop': self.delete_pubprops,
                            'dbxref': self.delete_dbxref,
                            'ignore': self.delete_ignore,
                            'obsolete': self.delete_obsolete}

        self.proforma_start_line_number = params.get('proforma_start_line_number')

        ###########################################################
        # Values queried later, placed here for reference purposes.
        ############################################################
        self.pub = None   # All other proforma need a reference to a pub
        self.parent_pub = None  # Various checks refer to this so just get it once
        self.gene = None  # Needed reference for alleles
        self.newpub = False  # Modified later for new publications.

        # Initiate the parent.
        super(ChadoPub, self).__init__(params)

        ############################################################
        # Get processing info and data to be processed.
        # Please see the yml/publication.yml file for more details
        ############################################################
        yml_file = os.path.join(os.path.dirname(__file__), 'yml/publication.yml')
        # Populated self.process_data with all possible keys.
        self.process_data = self.load_reference_yaml(yml_file, params)

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

        cvterm = self.session.query(Cvterm).join(Cv).filter(Cvterm.cv_id == Cv.cv_id,
                                                            Cvterm.name == p1_data[FIELD_VALUE],
                                                            Cv.name == 'pub type',
                                                            Cvterm.is_obsolete == 0).one_or_none()

        if not cvterm:
            self.critical_error(p1_data, 'Missing P1 type of publication.')
            return

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

    def get_related_pub(self, tuple, uniquename=True):
        """
        from the fbrf tuple get the pub
        """
        if tuple is not None and tuple[FIELD_VALUE] is not None:
            log.debug("Looking up pub: {}.".format(tuple[FIELD_VALUE]))
            pub = None
            if uniquename:
                pub = self.session.query(Pub).filter(Pub.uniquename == tuple[FIELD_VALUE]).one_or_none()
                if not pub:
                    self.critical_error(tuple, 'Pub does not exist in the database.')
                    return
            else:
                if tuple[FIELD_VALUE]:
                    pub = self.session.query(Pub).filter(Pub.miniref == tuple[FIELD_VALUE]).one()
            return pub
        else:
            return

    def add_relationship(self, subject_pub, object_pub, cvterm, query_source):
        """
        add relationship bewteen the two pubs with cvterm specified
        """
        # look up the cvterm
        log.debug("Querying for cvterm '{}' with cv of 'pub relationship type'.".format(cvterm))
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
        log.debug("Querying for cvterm 'published_in' with cv of 'pub relationship type'.")
        cvterm = self.session.query(Cvterm).join(Cv).filter(Cv.name == 'pub relationship type',
                                                            Cvterm.name == 'published_in',
                                                            Cvterm.is_obsolete == 0).one()

        pr = self.session.query(PubRelationship).\
            join(Pub, Pub.pub_id == PubRelationship.object_id).\
            join(Cvterm).filter(PubRelationship.subject_id == pub.pub_id,
                                PubRelationship.type_id == cvterm.cvterm_id).one_or_none()
        log.debug("PR => {}".format(pr))
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

        log.debug("Querying for P2 miniref '{}'.".format(tuple[FIELD_VALUE]))
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
            if not pub:
                self.critical_error(self.process_data['P22']['data'], 'Pub does not exist in the database.')
                return
        else:
            pub = None

        if self.has_data('P1'):
            P1_cvterm = self.get_P1_cvterm_and_validate(pub)

        if not self.newpub:
            pub = self.pub_from_fbrf(self.process_data['P22']['data'], self.session)
        else:
            if not P1_cvterm:  # ErrorTracking already knows, so just return.
                return None
            log.info("Creating new publication")

            # A trigger will swap out FBrf:temp_0 to the next rf in the sequence.
            pub, _ = get_or_create(self.session, Pub, type_id=P1_cvterm.cvterm_id, uniquename='FBrf:temp_0')
            log.info(pub)
            log.info("New pub created with fbrf {}.".format(pub.uniquename))
        return pub

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
            self.critical_error(P46_data, 'P46 does not have the format */*.')
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

    def extra_checks(self):
        """
        Not all tests can be done in the validator do extra ones here.
        """
        if self.has_data('P11'):
            self.do_P11_checks()
        if self.has_data('P2') and self.bang_c != 'P2' and self.bang_d != 'P2':
            self.check_multipub(self.parent_pub, self.process_data['P2']['data'])
        if self.has_data('P46'):
            self.graphical_abstracts_check()

    def load_direct(self, key):
        """
        Direct fields are those that are directly connected to the pub.
        So things like: title, pages, volume etc

        Params: key: key into the dict (self.process_data) that contains
                     the data and info on what to do with it including extra
                     terms like warning or boolean.
        """
        if self.has_data(key):
            if 'boolean' in self.process_data[key]:
                setattr(self.pub, self.process_data[key]['name'], True)
                if 'warning' in self.process_data[key]:
                    message = "Making {} {}.".format(self.process_data['P22']['data'][FIELD_VALUE], self.process_data[key]['name'])
                    self.warning_error(self.process_data[key]['data'], message)
            else:
                old_attr = getattr(self.pub, self.process_data[key]['name'])
                if old_attr:
                    self.warning_error(self.process_data[key]['data'], "No !c but still overwriting existing value of {}".format(old_attr))
                setattr(self.pub, self.process_data[key]['name'], self.process_data[key]['data'][FIELD_VALUE])

    def load_relationship(self, key):
        if type(self.process_data[key]['data']) is list:
            for fbrf in self.process_data[key]['data']:
                if 'verify_only_on_update' not in self.process_data[key] or self.newpub:
                    pub = self.get_related_pub(fbrf)
                    if not pub:
                        return
                    self.add_relationship(self.pub, pub, self.process_data[key]['cvterm'], self.process_data[key]['data'])
        else:  # P2 can only change with !c or has no parent pub
            log.debug("not list {}".format(key))
            parent_pub = self.get_parent_pub(self.pub)
            if self.bang_c == key or not parent_pub:
                fbrf = self.process_data[key]['data']
                pub = self.get_related_pub(fbrf, uniquename=False)
                if not pub:
                    return
                self.add_relationship(self.pub, pub, self.process_data[key]['cvterm'], self.process_data[key]['data'])

    def load_dbxref(self, key):
        if self.has_data(key):
            self.load_pubdbxref(self.process_data[key]['dbname'], self.process_data[key]['data'])

    def ignore(self, key):
        """
        Some fields no processing but are merely used to define things for checks.
        i.e. P22, this is processed to either fetch an existing pub or is set to new
             so will already have been processed as we get the pub object first.
        So we purposefully ignore it now as it has had all the processing needed already done.
        """
        pass

    def make_obsolete(self, key):
        """
        Makes related pubs obsolete, NOT the pub itself.
        """
        for fbrf in self.process_data[key]['data']:
            if fbrf[FIELD_VALUE] is not None:
                log.debug("Make obsolete {}".format(fbrf))
                pub = self.get_related_pub(fbrf)
                pub.is_obsolete = True

    def load_pubprop(self, key):
        """
        Loads all the pub props.
        Params: key: key to the dict self.process_data
        self.process_data[key]['cvterm'] contains the cvterm to be used in the pupprob.
        self.process_data[key]['data'] contains the value(s) to be added.
        """
        if self.has_data(key):
            log.debug("loading pubprops")
            if type(self.process_data[key]['data']) is list:
                for row in self.process_data[key]['data']:
                    if row[FIELD_VALUE] is not None:
                        log.debug("loading {} {}".format(self.process_data[key]['cvterm'], row[FIELD_VALUE]))
                        self.load_single_pubprop('pubprop type', self.process_data[key]['cvterm'], row)
            else:
                if self.process_data[key]['data'][FIELD_VALUE] is not None:
                    log.debug("loading {} {}".format(self.process_data[key]['cvterm'],
                                                     self.process_data[key]['data'][FIELD_VALUE]))
                    self.load_single_pubprop('pubprop type', self.process_data[key]['cvterm'],
                                             self.process_data[key]['data'])

    def load_content(self):
        """
        Main processing routine
        """
        if self.process_data['P22']['data'][FIELD_VALUE] == "new":
            self.newpub = True

        self.pub = self.get_pub()

        if self.pub:  # Only proceed if we have a pub. Otherwise we had an error.
            self.parent_pub = self.get_parent_pub(self.pub)

            self.extra_checks()

        # bang c first as this supersedes all things
        if self.bang_c:
            self.bang_c_it()
        if self.bang_d:
            self.bang_d_it()

        for key in self.process_data:
            log.debug("Processing {}".format(self.process_data[key]['data']))
            self.type_dict[self.process_data[key]['type']](key)

        timestamp = datetime.now().strftime('%c')
        curated_by_string = 'Curator: %s;Proforma: %s;timelastmodified: %s' % (self.curator_fullname, self.filename_short, timestamp)
        log.info('Curator string assembled as:')
        log.info('%s' % (curated_by_string))

    def get_author(self, author):
        """
        Return surname and fivennames for the author string
        """
        names = author[FIELD_VALUE].split('\t')
        if len(names) > 2:
            self.critical_error(author, "Author has more than 1 tab in it, this is not allowed.")
        elif len(names) == 2:
            surname = names[0]
            givennames = names[1]
        else:
            surname = names[0]
            givennames = None
        return givennames, surname

    def load_author(self, key):
        if self.bang_d != 'P12':
            for author in self.process_data[key]['data']:
                givennames, surname = self.get_author(author)
                log.debug("Author get/create: {}.".format(author[FIELD_VALUE]))
                author, _ = get_or_create(
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
        log.debug("Looking up cvterm: {} {}.".format(cv_name, cv_term_name))
        cv_term_id = super(ChadoPub, self).cvterm_query(cv_name, cv_term_name, self.session)

        log.debug('Querying for FBrf \'%s\'.' % (value_to_add_tuple[FIELD_VALUE]))

        pub_prop, _ = get_or_create(
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
        log.debug("Looking up db: {}.".format(db_name))
        db = self.session.query(Db).filter(Db.name == db_name).one()

        log.debug("Looking up dbxref: {}.".format(value_to_add_tuple[FIELD_VALUE]))
        dbxref, _ = get_or_create(
            self.session, Dbxref,
            accession=value_to_add_tuple[FIELD_VALUE],
            db_id=db.db_id
        )

        log.debug('Adding \'%s\' to \'%s\'.' % (dbxref.accession, self.pub.uniquename))

        get_or_create(
            self.session, PubDbxref,
            pub_id=self.pub.pub_id,
            dbxref_id=dbxref.dbxref_id
        )

    ########################################################################################
    # Deletion bangc and bangd methods.
    # NOTE: After correction or deletion
    ########################################################################################
    def bang_c_it(self):
        """
        Correction. Remove all existing value(s) and replace with the value(s) in this field.
        """
        log.debug("Bang C processing {}".format(self.bang_c))
        key = self.bang_c
        self.delete_dict[self.process_data[key]['type']](key, bangc=True)
        delete_blank = False
        if type(self.process_data[key]['data']) is list:
            for item in self.process_data[key]['data']:
                if not item[FIELD_VALUE]:
                    delete_blank = True
        else:
            if not self.process_data[key]['data'] or not self.process_data[key]['data'][FIELD_VALUE]:
                delete_blank = True
        if delete_blank:
            self.process_data[key]['data'] = None

    def bang_d_it(self):
        """
        Remove specific values indicated in the proforma field.
        """
        log.debug("Bang D processing {}".format(self.bang_d))
        key = self.bang_d

        #####################################
        # check bang_d has a value to delete
        #####################################

        # TODO Bring line number info along with bang c/d info for error reporting.
        if key in self.process_data:
            if type(self.process_data[key]['data']) is not list:
                if not self.process_data[key]['data'][FIELD_VALUE]:
                    log.error("BANGD: {}".format(self.process_data[key]['data']))
                    self.critical_error(self.process_data[key]['data'], "Must specify a value with !d.")
                    self.process_data[key]['data'] = None
                    return
            else:
                for item in self.process_data[key]['data']:
                    if not item[FIELD_VALUE]:
                        log.error("BANGD: {}".format(item))
                        self.critical_error(item, "Must specify a value with !d.")
                        self.process_data[key]['data'] = None
                        return
        else:
            # Faking the tuple because we don't have a field value or line number.
            self.critical_error((key, key, key), "Must specify a value with !d.")
            return

        self.delete_dict[self.process_data[key]['type']](key, bangc=False)
        self.process_data[key]['data'] = None

    def delete_direct(self, key, bangc=True):
        try:
            new_value = self.process_data[key]['data'][FIELD_VALUE]
        except KeyError:
            new_value = None
        setattr(self.pub, self.process_data[key]['name'], new_value)
        # NOTE: direct is a replacement so might aswell delete data to stop it being processed again.
        self.process_data[key]['data'] = None

    def delete_author(self, key, bangc=True):
        if bangc:
            count = self.session.query(Pubauthor).filter(Pubauthor.pub_id == self.pub.pub_id).delete()
            log.debug("Removed {} pub authors".format(count))
        else:  # bangd just remove the ones listed
            for author in self.process_data[key]['data']:
                givennames, surname = self.get_author(author)
                log.debug("Removing {} - {} for {}".format(givennames, surname, self.pub.uniquename))
                pubauthor = self.session.query(Pubauthor).filter(Pubauthor.pub_id == self.pub.pub_id,
                                                                 Pubauthor.givennames == givennames,
                                                                 Pubauthor.surname == surname).one_or_none()
                if not pubauthor:
                    self.critical_error(author, "Cannot delete Author that does not exist.")
                else:
                    self.session.delete(pubauthor)
                    log.debug("{} removed".format(pubauthor))

    def delete_relationship(self, cvterm, item, uniquename):
        if not item[FIELD_VALUE]:
            self.critical_error(item, "Must specify a value with !d.")
            self.process_data[item[FIELD_NAME]]['data'] = None
            return
        if uniquename:
            object_pub = self.session.query(Pub).filter(Pub.uniquename == item[FIELD_VALUE]).one_or_none()
        else:
            object_pub = self.session.query(Pub).filter(Pub.miniref == item[FIELD_VALUE]).one_or_none()
        if not object_pub:
            self.critical_error(item, "Publication '{}' not found.".format(item[FIELD_VALUE]))
            return
        pubrel = self.session.query(PubRelationship).filter(PubRelationship.subject_id == self.pub.pub_id,
                                                            PubRelationship.object_id == object_pub.pub_id,
                                                            PubRelationship.type_id == cvterm.cvterm_id).one_or_none()
        if not pubrel:
            self.critical_error(item, "Publication '{}' not linked via {}.".format(item[FIELD_VALUE], cvterm.name))
            return
        self.session.delete(pubrel)
        log.debug("{} removed".format(pubrel))

    def delete_relationships(self, key, bangc=True):
        cvterm = self.session.query(Cvterm).join(Cv).filter(Cv.name == 'pub relationship type',
                                                            Cvterm.name == self.process_data[key]['cvterm'],
                                                            Cvterm.is_obsolete == 0).one()
        if bangc:
            count = self.session.query(PubRelationship).filter(PubRelationship.subject_id == self.pub.pub_id,
                                                               PubRelationship.type_id == cvterm.cvterm_id).delete()
            log.debug("removed {} Pub relationships".format(count))
        else:
            if type(self.process_data[key]['data']) is list:
                for item in self.process_data[key]['data']:
                    self.delete_relationship(cvterm, item, True)
            else:  # P2 is not a list
                self.delete_relationship(cvterm, self.process_data[key]['data'], False)

    def delete_pubprop(self, cvterm, item):
        """
        Delete specific pubprop specified by the value and cvterm.
        Give critical error if there is no value or value not found.
        """
        if not item[FIELD_VALUE]:
            self.critical_error(item, "Must specify a value with !d.")
            self.process_data[item[FIELD_NAME]]['data'] = None
            return
        pubprop = self.session.query(Pubprop).filter(Pubprop.pub_id == self.pub.pub_id,
                                                     Pubprop.value == item[FIELD_VALUE],
                                                     Pubprop.type_id == cvterm.cvterm_id).one_or_none()
        if not pubprop:
            message = "Publication '{}' has no pubprop of type {} and value {}.".format(self.pub.uniquename, cvterm.name, item[FIELD_VALUE])
            self.critical_error(item, message)
            self.process_data[item[FIELD_NAME]]['data'] = None
            return

        self.session.delete(pubprop)
        log.debug("{} removed".format(pubprop))

    def delete_pubprops(self, key, bangc=True):
        """
        Delete the pubprops specified by self.process_data[key]['cvterm']
        and if not bangc then by just the one with the value.
        """
        cv_term = self.session.query(Cvterm).join(Cv).filter(Cv.name == 'pubprop type',
                                                             Cvterm.name == self.process_data[key]['cvterm'],
                                                             Cvterm.is_obsolete == 0).one()

        if bangc:
            count = self.session.query(Pubprop).filter(Pubprop.pub_id == self.pub.pub_id,
                                                       Pubprop.type_id == cv_term.cvterm_id).delete()
            log.debug("removed {} Pub Props for {}.".format(count, key))
        else:
            if type(self.process_data[key]['data']) is list:
                for item in self.process_data[key]['data']:
                    self.delete_pubprop(cv_term, item)
            else:
                self.delete_pubprop(cv_term, self.process_data[key]['data'])

    def delete_dbxref(self, key, bangc=True):
        """
        Bangc and bangd for dbxrefs.
        """
        db = self.session.query(Db).filter(Db.name == self.process_data[key]['dbname']).one()
        if bangc:
            # delete only the pub_dbxref or dbxref is no others exist.
            count = 0
            for item in self.session.query(PubDbxref).filter(PubDbxref.pub_id == self.pub.pub_id,
                                                             PubDbxref.dbxref_id == Dbxref.dbxref_id,
                                                             Dbxref.db_id == db.db_id):
                count += 1
                self.session.delete(item)
            log.debug("removed {} Pub dbxref for {}.".format(count, key))
        else:
            if not self.process_data[key]['data']:
                self.critical_error(item, "Must specify a value with !d.")
                self.process_data[key]['data'] = None
                return
            dbxref = self.session.query(PubDbxref).join(Pub).join(Dbxref).filter(Pub.pub_id == PubDbxref.pub_id,
                                                                                 Pub.pub_id == self.pub.pub_id,
                                                                                 PubDbxref.dbxref_id == Dbxref.dbxref_id,
                                                                                 Dbxref.db_id == db.db_id,
                                                                                 Dbxref.accession == self.process_data[key]['data'][FIELD_VALUE]).one_or_none()
            if not dbxref:
                message = "Publication '{}'".format(self.pub.uniquename)
                message += " has no dbxref of db '{}'".format(self.process_data[key]['dbname'])
                message += " and accession '{}'.".format(self.process_data[key]['data'][FIELD_VALUE])
                message += " So unable to remove it"
                self.critical_error(self.process_data[key]['data'], message)
                return

            self.session.delete(dbxref)
            log.debug("{} removed".format(dbxref))

    def delete_ignore(self, key, bangc=True):
        """
        Presently P1 only.
        P22 cannot be banged.
        Cannot be blank as it is a required field.

        Bang operations done first so reset the data to prevent harm later on, incase
        they get processed again.

        Bangc and Bangd are the same here as we have to have a value and each one has only one.
        """
        if not self.process_data[key]['data']:
            self.critical_error(self.process_data[key]['data'], "Must specify a value with !d or !c for this field.")
            self.process_data[key]['data'] = None
            return
        if key == 'P22':
            self.critical_error(self.process_data[key]['data'], "Bang operations NOT allowed with P22")
            self.process_data[key]['data'] = None
            return
        cvterm = self.session.query(Cvterm).join(Cv).filter(Cvterm.cv_id == Cv.cv_id,
                                                            Cvterm.name == self.process_data[key]['data'][FIELD_VALUE],
                                                            Cv.name == 'pub type',
                                                            Cvterm.is_obsolete == 0).one_or_none()
        if not cvterm:
            if self.process_data['P1']['data'][FIELD_VALUE] is None:
                self.critical_error(self.process_data[key]['data'],
                                    'Cannot bangc the P1 field with a blank value.')
                return
            else:
                self.critical_error(self.process_data[key]['data'], "cvterm for '{}' not found.".format(self.process_data[key]['data'][FIELD_VALUE]))
                self.process_data[key]['data'] = None
                return
        log.debug("Changed type of pub to {}".format(self.process_data[key]['data'][FIELD_VALUE]))
        self.pub.type_id = cvterm.cvterm_id

        self.process_data[key]['data'] = None

    def delete_obsolete(self, key, bangc=True):
        pass
