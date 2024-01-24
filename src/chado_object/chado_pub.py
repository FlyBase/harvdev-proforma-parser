"""

:synopsis: The Publication ChadoObject.

:moduleauthor: Ian Longden <ilongden@morgan.harvard.edu>
"""
import re
import os

from harvdev_utils.chado_functions.cvterm import get_cvterm
from .chado_base import ChadoObject, FIELD_VALUE, FIELD_NAME

from harvdev_utils.production import (
    Cv, Cvterm, Pub, Pubprop, Pubauthor, PubRelationship, Db, Dbxref, PubDbxref
)
from harvdev_utils.chado_functions import get_or_create
import logging
from datetime import datetime

log = logging.getLogger(__name__)


class ChadoPub(ChadoObject):
    """ChadoPub Class."""

    def __init__(self, params):
        """Initialise ChadoPub onject."""
        log.debug('Initializing ChadoPub object.')
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
        self.direct_key = 'P22'
        self.editor = False

    def get_P1_cvterm_and_validate(self):
        """Process P1 field and validate.

        https://svn.flybase.org/flybase-cam/Peeves/doc/specs/pub/P1.txt

        Checks To be valid:

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
        if not p1_data[FIELD_VALUE]:
            return
        if p1_data[FIELD_VALUE] in ('journal', 'compendium'):
            self.critical_error(p1_data, 'Not allowed to have the value "journal" or "compendium"')

        cvterm = self.session.query(Cvterm).join(Cv).filter(Cvterm.cv_id == Cv.cv_id,
                                                            Cvterm.name == p1_data[FIELD_VALUE],
                                                            Cv.name == 'pub type',
                                                            Cvterm.is_obsolete == 0).one_or_none()

        if not cvterm:
            self.critical_error(p1_data, 'Missing P1 type of publication.')
            return

        if self.pub:
            old_cvterm = self.session.query(Cvterm).join(Cv).join(Pubprop).\
                filter(Cvterm.cv_id == Cv.cv_id,
                       Pubprop.type_id == Cvterm.cvterm_id,
                       Cv.name == 'pub type',
                       Pubprop.pub_id == self.pub.pub_id,
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
        """From the fbrf tuple get the pub.

        Args:
            tuple (tuple): Proforma field tuple.

            uniquename (Bool): True to lookup via uniquename else miniref is done.

        Returns:
            None or the related ChadoPub object.

        """
        if tuple is not None and tuple[FIELD_VALUE] is not None:
            pub = None
            if uniquename:
                pub = self.session.query(Pub).filter(Pub.uniquename == tuple[FIELD_VALUE]).one_or_none()
                if not pub:
                    self.critical_error(tuple, 'Pub does not exist in the database.')
                    return
            else:
                if tuple[FIELD_VALUE]:
                    pub = self.session.query(Pub).filter(Pub.miniref == tuple[FIELD_VALUE],
                                                         Pub.is_obsolete == 'f').one()
            return pub
        else:
            return

    def add_relationship(self, subject_pub, object_pub, cvterm):
        """Add relationship between the two pubs with cvterm specified.

        Args:
            subject_pub (ChadoPub): pub object to be used as subject

            object_pub (ChadoPub): pub object to be used as object

            cvterm (str): cvterm name for cv 'pub relationship type'

        Returns:
            None

        """
        # look up the cvterm
        cvterm = self.session.query(Cvterm).join(Cv).filter(Cv.name == 'pub relationship type',
                                                            Cvterm.name == cvterm,
                                                            Cvterm.is_obsolete == 0).one()
        # now add the relationship
        get_or_create(self.session, PubRelationship,
                      subject_id=subject_pub.pub_id,
                      object_id=object_pub.pub_id,
                      type_id=cvterm.cvterm_id)

    def get_parent_pub(self):
        """Get the parent pub.

        Returns:
            ChadoPub object of the parent or None, if it does not have one. This is okay.

        """
        cvterm = self.session.query(Cvterm).join(Cv).filter(Cv.name == 'pub relationship type',
                                                            Cvterm.name == 'published_in',
                                                            Cvterm.is_obsolete == 0).one()

        parents = []
        for pr in self.session.query(PubRelationship).\
            join(Pub, Pub.pub_id == PubRelationship.object_id).\
            join(Cvterm).filter(PubRelationship.subject_id == self.pub.pub_id,
                                PubRelationship.type_id == cvterm.cvterm_id).all():
            parents.append(self.session.query(Pub).filter(Pub.pub_id == pr.object_id).one())
        return parents

    def check_multipub(self, old_parents, tuple):
        """Check pub in P2 is the same is the parent.

        Get P2 pub via the  miniref.
        If P22 is new
            * NO further checks needed.

        If P22 NOT new then
            * if it already has a relationship then check it is the same
            * if none exists no further checks needed.

        Args:
            old_parent (ChadoPub): parent pub found from pub.

            tuple (tuple): tuple to get data from.

        Returns:
            None

        """
        p2_pubs = self.session.query(Pub).filter(Pub.miniref == tuple[FIELD_VALUE])
        p2_list = []
        for p2 in p2_pubs:
            p2_list.append(p2.pub_id)

        if not self.newpub and old_parents:
            found = False
            old_name = ""
            for old_parent in old_parents:
                if old_parent.pub_id in p2_list:
                    found = True
                if old_parent.miniref:
                    old_name += old_parent.miniref
                else:
                    old_name += old_parent.uniquename
            if not found:
                message = 'P22 has a different parent "{}" than the one listed\n'.format(old_name)
                message += 'Not allowed to change P2 if it already has one. without !c'
                self.critical_error(self.process_data['P22']['data'], message)
                return

    def get_pub(self):
        """Get the pub or create it if new.

        Returns:
            None or the pub to be used.

        """
        if not self.newpub:
            self.pub = super(ChadoPub, self).pub_from_fbrf(self.process_data['P22']['data'])
            if not self.pub:
                self.critical_error(self.process_data['P22']['data'], 'Pub does not exist in the database.')
                return
        else:
            self.pub = None

        if self.has_data('P1'):
            P1_cvterm = self.get_P1_cvterm_and_validate()

        if not self.newpub:
            self.pub = self.pub_from_fbrf(self.process_data['P22']['data'])
        else:
            if not P1_cvterm:  # ErrorTracking already knows, so just return.
                return None
            log.debug("Creating new publication")

            # A trigger will swap out FBrf:temp_0 to the next rf in the sequence.
            self.pub, _ = get_or_create(self.session, Pub, type_id=P1_cvterm.cvterm_id, uniquename='FBrf:temp_0')
            log.debug(self.pub)
            log.debug("New pub created with fbrf {}.".format(self.pub.uniquename))
        return

    def graphical_abstracts_check(self):
        """Check the format of the graphical abstract.

        Checks within field
            Field should be separable into two components using '/' as the split character

        TODO:  * Should check that filename is not already in chado (associated with *any* FBrf, not just the one in P22)

        Checks between fields:
            First part of relative filepath should match the parent journal abbreviation (given either in P2 or in chado),
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

        expected_dir = self.parent_pub[0].miniref
        expected_dir.replace(". ", "_")
        if expected_dir != fields.group(1):
            message = "'{}' does not equal to what is expected, given its parent.".format(fields.group(1))
            message += "\nWas expecting directory to be {}.".format(expected_dir)
            self.warning_error(P46_data, message)

    def do_P11_checks(self):
        """Check P11a.

        Check if P11a already has a value. If it matches all well and good.

        Returns:
            None

        Critical Error:
            Page does not match what is in P11

        """
        """  CRITICAL -- Cvterm "journal" is not the same as previous personal communication to FlyBase

        If existing pages retrieved from chado via FBrf:
        P11a:  Trying to change <chado-pages> to '<your-pages>' but it isn't yet in Chado.
               # Bang C i guess, not implenented yet ??????????? the one above

        P11a:  Trying to set <pages> to '<your-pages>' but it is '<chado-pages>' in Chado.

        """
        p11a = self.process_data['P11a']['data']
        if not self.newpub and self.has_bang_type('P11a', 'c'):
            if self.pub.pages and p11a and self.pub.pages != p11a[FIELD_VALUE]:
                message = 'P11a page range "{}" does not match "{}" already in chado.\n'.format(p11a[FIELD_VALUE], self.pub.pages)
                self.critical_error(p11a, message)

    def extra_checks(self):
        """Not all tests can be done in the validator do extra ones here.

        Checks:
            * P11a pages match
            * multipub check P2 same as parent
            * graphical abstract format check.

        Critical Error:
            On failing any check.

        Returns:
            None

        """
        if self.has_data('P11'):
            self.do_P11_checks()
        if self.has_data('P2') and not self.has_bang_type('P2'):
            self.check_multipub(self.parent_pub, self.process_data['P2']['data'])
        if self.has_data('P46'):
            self.graphical_abstracts_check()

    def load_direct(self, key):
        """Load the direct fields.

        Direct fields are those that are directly connected to the pub.
        So things like: title, pages, volume etc

        Args:
            key: key into the dict (self.process_data) that contains
                 the data and info on what to do with it including extra
                 terms like warning or boolean.

        Returns:
            None

        Critical Error:
            Direct field already has different value and we have no bangc.

        """
        if self.has_data(key):
            if 'boolean' in self.process_data[key]:
                setattr(self.pub, self.process_data[key]['name'], True)
                if 'warning' in self.process_data[key]:
                    message = "Making {} {}.".format(self.process_data[self.direct_key]['data'][FIELD_VALUE], self.process_data[key]['name'])
                    self.warning_error(self.process_data[key]['data'], message)
            else:
                log.debug("key is {}, name = {}".format(key, self.process_data[key]['name']))
                log.debug("key is {}, value is {}".format(key, self.process_data[key]['data'][FIELD_VALUE]))
                old_attr = getattr(self.pub, self.process_data[key]['name'])
                if old_attr and not self.has_bang_type(key):
                    # Just a check?
                    if old_attr != self.process_data[key]['data'][FIELD_VALUE]:
                        message = "No !c So will not overwrite {} with {}".format(old_attr, self.process_data[key]['data'][FIELD_VALUE])
                        self.critical_error(self.process_data[key]['data'], message)
                else:
                    setattr(self.pub, self.process_data[key]['name'], self.process_data[key]['data'][FIELD_VALUE])

    def load_relationship(self, key):
        """Load relationship between current pub and pub specified via key.

        Args:
            key (str): proforma key name.

        Returns:
            None

        """
        if type(self.process_data[key]['data']) is list:
            for fbrf in self.process_data[key]['data']:
                if 'verify_only_on_update' not in self.process_data[key] or self.newpub:
                    pub = self.get_related_pub(fbrf)
                    if not pub:
                        return
                    self.add_relationship(self.pub, pub, self.process_data[key]['cvterm'])
        else:  # P2 can only change with !c or has no parent pub
            log.debug("not list {}".format(key))
            if self.has_bang_type(key, 'c') or not self.parent_pub:
                fbrf = self.process_data[key]['data']
                pub = self.get_related_pub(fbrf, uniquename=False)
                if not pub:
                    return
                self.add_relationship(self.pub, pub, self.process_data[key]['cvterm'])

    def load_dbxref(self, key):
        """Load the dbxref. given the proforma key.

        Args:
            key (str): proforma key name.

        Returns:
            None

        """
        if self.has_data(key):
            self.load_pubdbxref(self.process_data[key]['dbname'], self.process_data[key]['data'])

    def ignore(self, key):
        """Ignore this key.

        Some fields need no separate processing but are merely used to define things for checks.
        i.e. P22, this is processed to either fetch an existing pub or is set to new
        so will already have been processed as we get the pub object first.
        So we purposefully ignore it now as it has had all the processing needed already done.

        Args:
            key (str): proforma key name but is ignored.

        Returns:
            None

        """
        pass

    def make_obsolete(self, key):
        """Make related pubs obsolete, NOT the pub itself.

        Args:
            key (str): proforma key name but is ignored.

        Returns:
            None

        """
        for fbrf in self.process_data[key]['data']:
            if fbrf[FIELD_VALUE] is not None:
                log.debug("Make obsolete {}".format(fbrf))
                pub = self.get_related_pub(fbrf)
                pub.is_obsolete = True

    def load_pubprop(self, key):
        """Load the pubprop.

        self.process_data[key]['cvterm'] contains the cvterm to be used in the pupprob.
        self.process_data[key]['data'] contains the value(s) to be added.

        Args:
            key (str): proforma key name.

        Returns:
            None

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

    def load_content(self, references):
        """Load the proforma context.

        Main processing routine

        """
        if self.process_data['P22']['data'][FIELD_VALUE] == "new":
            self.newpub = True

        self.get_pub()

        if self.pub:  # Only proceed if we have a pub. Otherwise we had an error.
            self.parent_pub = self.get_parent_pub()

            self.extra_checks()
        else:
            return
        # bang c first as this supersedes all things
        if self.bang_c:
            self.bang_c_it()
        if self.bang_d:
            self.bang_d_it()

        for key in self.process_data:
            log.debug("Processing {}".format(self.process_data[key]['data']))
            self.type_dict[self.process_data[key]['type']](key)

        timestamp = datetime.now().strftime('%c')
        curated_by_string = 'Curator: %s;Proforma: %s;timelastmodified: %s' % (self.curator_fullname, self.filename_short.split('/')[-1], timestamp)
        log.debug('Curator string assembled as:')
        log.debug('%s' % (curated_by_string))
        curated_by = get_cvterm(self.session, 'pubprop type', 'curated_by')
        get_or_create(
            self.session, Pubprop,
            type_id=curated_by.cvterm_id,
            pub_id=self.pub.pub_id,
            value=curated_by_string)
        return self.pub

    def get_author(self, author):
        """Return surname and givennames for the author string.

        Args:
            author (str): author name can be surname and given.

        Returns:
            given name (str)
            surname (str)

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
        """Load the Author.

        Args:
            key (str): key for process_data to get author from.

        Returns:
            None

        """
        if 'P12' not in self.bang_d:
            for author in self.process_data[key]['data']:
                givennames, surname = self.get_author(author)
                log.debug("Author get/create: {}.".format(author[FIELD_VALUE]))
                author, _ = get_or_create(
                    self.session, Pubauthor,
                    pub_id=self.pub.pub_id,
                    surname=surname,
                    editor=self.editor,
                    givennames=givennames
                )

    def load_single_pubprop(self, cv_name, cvterm_name, value_to_add_tuple):
        """Load a single pup prop.

        From a given cv and cvterm name add the pubprop with value in tuple.
        If cv or cvterm do not exist create an error and return.

        Args:
            cv_name (str): cv name to use for prop.

            cvterm_name (str): cvterm name to use for prop.

            value_to_add_tuple (tuple): prop value.

        Returns:
           pubprop (PubProp): pub prop created

        """
        value = value_to_add_tuple[FIELD_VALUE]

        cvterm_id = super(ChadoPub, self).cvterm_query(cv_name, cvterm_name)

        log.debug('Querying for FBrf \'%s\'.' % (value))

        # check if it exists already
        pubprops = self.session.query(Pubprop). \
            filter(Pubprop.pub_id == self.pub.pub_id,
                   Pubprop.type_id == cvterm_id,
                   Pubprop.value == value_to_add_tuple[FIELD_VALUE]).all()
        found = False
        for pp in pubprops:
            found = pp
        if not found:
            pub_prop, _ = get_or_create(
                self.session, Pubprop,
                pub_id=self.pub.pub_id,
                value=value,
                type_id=cvterm_id
            )
        else:
            self.critical_error(value_to_add_tuple, f'{value_to_add_tuple[FIELD_VALUE]} Already set for {self.pub.uniquename}.')
            return None
        return pub_prop

    def load_pubdbxref(self, db_name, value_to_add_tuple):
        """Add dbxref to the pub (self.pub).

        Args:
            db_name (str): db name to use for dbxref.

            value_to_add_tuple (tuple): Holds the accession.

        Returns:
           None

        """
        db = self.session.query(Db).filter(Db.name == db_name).one()

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

    def delete_direct(self, key, bangc=True):
        """Delete the direct value.

        Args:
            key (str): key for process_data.

            bangc (bool): bangc or bangd

        Returns:
            None

        """
        try:
            new_value = self.process_data[key]['data'][FIELD_VALUE]
        except KeyError:
            new_value = None
        setattr(self.pub, self.process_data[key]['name'], new_value)
        # NOTE: direct is a replacement so might aswell delete data to stop it being processed again.
        self.process_data[key]['data'] = None

    def delete_author(self, key, bangc=True):
        """Delete the author.

        Args:
            key (str): key for process_data.

            bangc (bool): bangc or bangd

        Returns:
            None

        Critical Error:
            Author does not exist so cannot delete.

        """
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
        """Delete the pub relationship.

        Args:
            cvterm (Cvterm): cvterm object.

            item (tuple): field data.

            uniquename (bool): Use unique name if true else miniref for lookup.

        Returns:
            None

        Critical Error:
            Publication not found
            Publication is not related

        """
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
        """Delete all relationships.

        Args:
            key (str): key for process_data.

            bangc (bool): bangc or bangd

        Returns:
            None

        """
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
        """Delete the pub relationship.

        Delete specific pubprop specified by the value and cvterm.
        Give critical error if there is no value or value not found.

        Args:
            cvterm (Cvterm): cvterm object.

            item (tuple): field data.

        Returns:
            None

        Critical Error:
            Publication has no pubprop of this type

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
        """Delete pub prop.

        Delete the pubprops specified by self.process_data[key]['cvterm']
        and if not bangc then by just the one with the value.

        Args:
            key (str): key for process_data.

            bangc (bool): bangc or bangd

        Returns:
            None

        """
        cv_term = self.session.query(Cvterm).join(Cv).filter(Cv.name == 'pubprop type',
                                                             Cvterm.name == self.process_data[key]['cvterm'],
                                                             Cvterm.is_obsolete == 0).one()

        if bangc:
            count = self.session.query(Pubprop).filter(Pubprop.pub_id == self.pub.pub_id,
                                                       Pubprop.type_id == cv_term.cvterm_id).delete()
            log.debug("removed {} Pub Props for {}.".format(count, key))
            if not count:
                if type(self.process_data[key]['data']) is list:
                    item = self.process_data[key]['data'][0]
                else:
                    item = self.process_data[key]['data']
                self.critical_error(item, "No previous records found in database. Therefore cannot bangc it.")
        else:
            if type(self.process_data[key]['data']) is list:
                for item in self.process_data[key]['data']:
                    self.delete_pubprop(cv_term, item)
            else:
                self.delete_pubprop(cv_term, self.process_data[key]['data'])

    def delete_dbxref(self, key, bangc=True):
        """Delete the dxxref.

        Bangc and bangd for dbxrefs.

        Args:
            key (str): key for process_data.

            bangc (bool): bangc or bangd

        Returns:
            None

        Critical Errors:
            Publication does not have that dbxref.

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
                self.critical_error(self.process_data[key]['data'], "Must specify a value with !d.")
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
        """Delete P1 data.

        Presently P1 only.
        P22 cannot be banged.
        Cannot be blank as it is a required field.

        Bang operations done first so reset the data to prevent harm later on, incase
        they get processed again.

        Bangc and Bangd are the same here as we have to have a value and each one has only one.

        Args:
            key (str): key for process_data.

            bangc (bool): bangc or bangd

        Returns:
            None

        Critial Errors:
            P1 cannot be blank so cannot bangc with blank value.

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
        """Do nothing."""
        pass
