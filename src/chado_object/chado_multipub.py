"""

:synopsis: The "multipub" ChadoObject.

"moduleauthor: Ian Longden <ilongden@morgan.harvard.edu>
"""
import os
from .chado_base import FIELD_VALUE
from .chado_pub import ChadoPub
from harvdev_utils.production import (
    Cv, Cvterm, Pub, Db, Dbxref, PubDbxref
)
from harvdev_utils.chado_functions import get_or_create, get_cvterm

import logging
from datetime import datetime
log = logging.getLogger(__name__)


class ChadoMultipub(ChadoPub):
    def __init__(self, params):
        log.debug('Initializing ChadoMultipub object.')
        # Initiate the parent.
        super(ChadoPub, self).__init__(params)
        ##########################################
        # Set up how to process each type of input
        ##########################################
        self.type_dict = {'direct': self.load_direct,
                          'author': self.load_author,
                          'dbxref': self.load_dbxref,
                          'cvterm': self.load_cvterm,
                          'ignore': self.ignore,
                          'obsolete': self.make_obsolete,
                          'make_secondary': self.make_secondary}

        self.delete_dict = {'direct': self.delete_direct,
                            'author': self.delete_author,
                            'dbxref': self.delete_dbxref,
                            'cvterm': self.delete_cvterm,
                            'ignore': self.delete_ignore}

        self.proforma_start_line_number = params.get('proforma_start_line_number')

        ###########################################################
        # Values queried later, placed here for reference purposes.
        ############################################################
        self.newpub = False  # Modified later for new publications.

        ############################################################
        # Get processing info and data to be processed.
        # Please see the yml/publication.yml file for more details
        ############################################################
        yml_file = os.path.join(os.path.dirname(__file__), 'yml/multipublication.yml')
        # Populated self.process_data with all possible keys.
        self.process_data = self.load_reference_yaml(yml_file, params)
        self.direct_key = 'MP1'
        self.editor = True

    def add_FlyBase_name_from_pub(self, obs_pub):
        """Create pub dbxref.

        Args:
            obs_pub (Pub Object): pub to ber linked to the Flybase DB.
        """
        # copy flybase name xref to self.pub
        dbxrefs = self.session.query(Dbxref).join(PubDbxref).join(Db).\
            filter(PubDbxref.pub_id == obs_pub.pub_id,
                   Db.name == 'FlyBase').all()
        for dbxref in dbxrefs:
            get_or_create(
                self.session, PubDbxref,
                pub_id=self.pub.pub_id,
                dbxref_id=dbxref.dbxref_id
            )

    def make_secondary(self, key):
        """Make pub obsolete.

        Args:
            key (string): field/key from proforma
        """
        # Make these obsolete
        for tuples in self.process_data[key]['data']:
            log.debug("tuples is {}".format(tuples))
            if tuples[FIELD_VALUE] is not None:
                multi_name = "multipub_{}".format(tuples[FIELD_VALUE])
                log.debug("Make obsolete {}".format(multi_name))
                pub = self.session.query(Pub).filter(Pub.uniquename == multi_name).one_or_none()
                if pub:
                    pub.is_obsolete = True
                    self.add_FlyBase_name_from_pub(pub)
                else:
                    self.critical_error(tuples, 'Pub {} does not exist in the database.'.format(multi_name))

    def get_pub(self):
        """Get pub.

        get pub or create pub if new.

        Returns:
            Pub to be used OR None.
        """
        if not self.newpub:
            fbrf = "multipub_{}".format(self.process_data['MP1']['data'][FIELD_VALUE])
            pub = self.session.query(Pub).\
                filter(Pub.uniquename == fbrf).\
                one_or_none()
            if not pub:
                self.critical_error(self.process_data['MP1']['data'], 'Pub {} does not exist in the database.'.format(fbrf))
                return pub
            # Check MP2a is defined. If not then validation will already have raised an error
            # So just return

            if not self.has_data('MP2a'):
                return pub

            # check MP2a is equal to miniref. Must exist from validation.
            if 'MP2a' not in self.bang_c:
                if pub.miniref != self.process_data['MP2a']['data'][FIELD_VALUE]:
                    message = "{} does not match abbreviation of {}".format(self.process_data['MP2a']['data'][FIELD_VALUE], pub.miniref)
                    self.critical_error(self.process_data['MP2a']['data'], message)
            return pub

        cvterm = get_cvterm(self.session, self.process_data['MP17']['cvname'], self.process_data['MP17']['data'][FIELD_VALUE])
        if not cvterm:
            message = 'Pub type {} does not exist in the database.'.format(self.process_data['MP17']['data'][FIELD_VALUE])
            self.critical_error(self.process_data['MP17']['data'], message)
            return

        # A trigger will swap out multipub:temp_0 to the next rf in the sequence.
        pub, _ = get_or_create(self.session, Pub, type_id=cvterm.cvterm_id, uniquename='multipub:temp_0')
        return pub

    def flag_errors(self):
        """Apply checks for new pub."""
        for key in ['MP15', 'MP2b', 'MP17']:
            if key not in self.process_data:
                self.critical_error((key, None, 0), 'Error {} Must be set for new pubs.'.format(key))
        if 'MP17' in self.process_data and self.process_data['MP17']['data'][FIELD_VALUE] == 'book':
            if 'MP11' not in self.process_data:
                self.critical_error(('MP11', None, 0), 'Error MP11 is not set so cannot set but MP1 is new and MP17 is book, so is required.')

    def load_content(self, references):
        """Process the data."""
        if self.process_data['MP1']['data'][FIELD_VALUE] == "new":
            self.newpub = True
            self.flag_errors()
            if not self.has_data('MP17'):
                return None

        self.pub = self.get_pub()

        if not self.pub:  # Only proceed if we have a pub. Otherwise we had an error.
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
        curated_by_string = 'Curator: %s;Proforma: %s;timelastmodified: %s' % (self.curator_fullname, self.filename_short, timestamp)
        log.debug('Curator string assembled as:')
        log.debug('%s' % (curated_by_string))

    def load_cvterm(self, key):
        """Load multipub cvterm.

        MP17 is the only cvterm here and is loaded as part of get_pub
        So it is safe to ignore here. Nope!!
        Okay give an error if not bangc and it has changed

        Args:
            key (string): field/key from proforma
        """
        if self.has_data(key) and not self.newpub:  # new pub already done
            cvterm = self.session.query(Cvterm).join(Cv).join(Pub).filter(Cv.name == self.process_data[key]['cvname'],
                                                                          Pub.pub_id == self.pub.pub_id).one()
            if not cvterm:
                message = 'Previous Pub type {} does not exist in the database?'.format(self.process_data['MP17']['data'][FIELD_VALUE])
                self.critical_error(self.process_data[key]['data'], message)
            else:
                if cvterm.name != self.process_data[key]['data'][FIELD_VALUE]:
                    message = 'Cannot change type from {} to {} without !c'.format(cvterm.name, self.process_data['MP17']['data'][FIELD_VALUE])
                    self.critical_error(self.process_data[key]['data'], message)

    def delete_cvterm(self, key, bangc):
        """Change cvterm for pub.

        Args:
            key (string): field/key from proforma
            bangc (string): Not used.
        """
        if self.has_data(key):
            old_cvterm = self.session.query(Cvterm).join(Cv).join(Pub, Pub.type_id == Cvterm.cvterm_id).\
                filter(Cv.name == self.process_data[key]['cvname'], Pub.pub_id == self.pub.pub_id).one_or_none()

            new_cvterm = get_cvterm(self.session, self.process_data[key]['cvname'], self.process_data[key]['data'][FIELD_VALUE])
            if not old_cvterm:
                message = 'Previous Pub type {} does not exist in the database???'.format(self.process_data['MP17']['data'][FIELD_VALUE])
                self.critical_error(self.process_data[key]['data'], message)
            elif new_cvterm:
                if old_cvterm.name == self.process_data[key]['data'][FIELD_VALUE]:
                    message = 'Cannot change type from {} to {} as it is the same'.format(old_cvterm.name, new_cvterm.name)
                    self.critical_error(self.process_data[key]['data'], message)
                else:
                    log.debug("Setting pub to new type ({}) {}".format(new_cvterm.cvterm_id, new_cvterm.name))
                    self.pub.type_id = new_cvterm.cvterm_id
            else:  # should be done in avlidation but just being safe!
                message = 'Unknown pub type in chado for {}'.format(self.process_data[key]['data'][FIELD_VALUE])
                self.critical_error(self.process_data[key]['data'], message)
        else:
            message = 'Must specify a pub type; cannot bangc to nothing.'
            self.critical_error(self.process_data[key]['data'], message)
