"""
.. module:: chado_pub
   :synopsis: The "multipub" ChadoObject.

.. moduleauthor:: Ian Longden <ilongden@morgan.harvard.edu>
"""
import os
from .chado_base import FIELD_VALUE
from .chado_pub import ChadoPub
from harvdev_utils.production import (
    Cv, Cvterm, Pub
)
from harvdev_utils.chado_functions import get_or_create

import logging
from datetime import datetime
log = logging.getLogger(__name__)


class ChadoMultipub(ChadoPub):
    def __init__(self, params):
        log.info('Initializing ChadoMultipub object.')
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
                          'obsolete': self.make_obsolete}

        self.delete_dict = {'direct': self.delete_direct,
                            'author': self.delete_author,
                            'dbxref': self.delete_dbxref,
                            'cvterm': self.delete_cvterm,
                            'ignore': self.delete_ignore,
                            'obsolete': self.delete_obsolete}

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

    def get_pub(self):
        """
        get pub or create pub if new.
        returns None or the pub to be used.
        """
        if not self.newpub:
            fbrf = "multipub_{}".format(self.process_data['MP1']['data'])
            pub = self.pub_from_fbrf(fbrf)
            if not pub:
                self.critical_error(self.process_data['MP1']['data'], 'Pub does not exist in the database.')
                return pub
            # check MP2a is equal to miniref. Must exist from validation.
            if pub.miniref != self.process_data['MP2a']['data'][FIELD_VALUE]:
                message = "{} does not match abbreviation of {}".format(self.process_data['MP2a']['data'][FIELD_VALUE], pub.miniref)
                self.critical_error(self.process_data['MP2a']['data'], message)
                return pub

        cvterm = self.session.query(Cvterm).join(Cv).filter(Cv.name == self.process_data['MP17']['cvname'],
                                                            Cvterm.name == self.process_data['MP17']['data'][FIELD_VALUE],
                                                            Cvterm.is_obsolete == 0).one()
        if not cvterm:
            message = 'Pub type {} does not exist in the database.'.format(self.process_data['MP17']['data'][FIELD_VALUE])
            self.critical_error(self.process_data['MP17']['data'], message)
            return

        # A trigger will swap out multipub:temp_0 to the next rf in the sequence.
        pub, _ = get_or_create(self.session, Pub, type_id=cvterm.cvterm_id, uniquename='multipub:temp_0')
        log.info(pub)
        log.info("New pub created with fbrf {}.".format(pub.uniquename))
        return pub

    def load_content(self):
        """
        Main processing routine
        """
        if self.process_data['MP1']['data'][FIELD_VALUE] == "new":
            self.newpub = True

        self.pub = self.get_pub()

        if self.pub:  # Only proceed if we have a pub. Otherwise we had an error.
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

    def extra_checks(self):
        """
        Perform extra checks that validation was not able to do.
        Matching of miniref to MP17 for existing pub already done in get_pub
        """
        pass  # None i can think of at the moment

    def load_cvterm(self, key):
        """
        MP17 is the only cvterm here and is loaded as part of get_pub
        So it is safe to ignore here.
        """
        pass

    def delete_cvterm(self, key):
        """
        Will need to add this as MP17 can have bangc
        """
        pass
