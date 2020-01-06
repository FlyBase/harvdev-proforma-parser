"""
.. module:: chado_db
   :synopsis: The "db" ChadoObject.

.. moduleauthor:: Ian Longden <ianlongden@morgan.harvard.edu>
"""
import os
from .chado_base import ChadoObject, FIELD_VALUE

from harvdev_utils.production import (
    Db
)
from harvdev_utils.chado_functions import get_or_create

import logging
from datetime import datetime

log = logging.getLogger(__name__)


class ChadoDb(ChadoObject):
    def __init__(self, params):
        log.info('Initializing ChadoDb object.')
        ##########################################
        # Set up how to process each type of input
        ##########################################
        self.type_dict = {'direct': self.load_direct,
                          'ignore': self.ignore}

        self.delete_dict = {'direct': self.delete_direct,
                            'ignore': self.delete_ignore}

        self.proforma_start_line_number = params.get('proforma_start_line_number')

        ###########################################################
        # Values queried later, placed here for reference purposes.
        ############################################################
        self.db = None   # All other proforma need a reference to a pub

        # Initiate the parent.
        super(ChadoDb, self).__init__(params)

        ############################################################
        # Get processing info and data to be processed.
        # Please see the yml/publication.yml file for more details
        ############################################################
        yml_file = os.path.join(os.path.dirname(__file__), 'yml/db.yml')
        # Populated self.process_data with all possible keys.
        self.process_data = self.load_reference_yaml(yml_file, params)
        self.main_key = 'DB1a'

    def load_content(self):
        """
        Main processing routine
        """

        self.db = self.get_db()

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

    def get_db(self):
        """
        Get/Create Db and do checks.
        """
        db_name = self.process_data[self.main_key]['data'][FIELD_VALUE]
        in_chado = self.process_data['DB1g']['data'][FIELD_VALUE]
        self.db, is_new = get_or_create(self.session, Db, name=db_name)

        error_message = None
        if is_new and in_chado == 'y':
            error_message = "Db {} not found in Chado database but DB1g says it currently exists".format(db_name)
        elif not is_new and in_chado == 'n':
            error_message = "Db {} already exists but DB1g says it should not".format(db_name)
        if error_message:
            self.critical_error(self.process_data[self.main_key]['data'], error_message)
        return self.db

    def ignore(self, key):
        pass

    def load_direct(self, key):
        """
        Direct fields are those that are directly connected to the db.
        So things like: description, url and preurl

        Params: key: key into the dict (self.process_data) that contains
                     the data and info on what to do with it including extra
                     terms like warning or boolean.
        """
        if self.has_data(key):
            old_attr = getattr(self.db, self.process_data[key]['name'])
            if old_attr:
                if 'related' in self.process_data[key]:  # old style proforma
                    warning_message = "Using OLD style DB profoma. This will be deprecated soon please change in future proforma."
                    self.warning_error(self.process_data[key]['data'], warning_message)
                    related_key = self.process_data[key]['related']
                    if related_key not in self.process_data:
                        error_message = "cannot change {} as it already has a value and {} is not set to y".format(key, related_key)
                        self.critical_error(self.process_data[key]['data'], error_message)
                        return
                    if self.process_data[related_key]['data'][FIELD_VALUE] != 'y':
                        error_message = "cannot change {} as it already has a value and {} is not set to y".format(key, related_key)
                        self.critical_error(self.process_data[key]['data'], error_message)
                        return
                else:
                    # We should not get here !c will have removed the old value for new style proforma
                    error_message = "You are trying to replace a value without bangc for {}. This is not allowed.".format(key)
                    self.critical_error(self.process_data[key]['data'], error_message)
                    return
            setattr(self.db, self.process_data[key]['name'], self.process_data[key]['data'][FIELD_VALUE])

    def delete_direct(self, key, bangc=True):
        try:
            new_value = self.process_data[key]['data'][FIELD_VALUE]
        except KeyError:
            new_value = None
        setattr(self.db, self.process_data[key]['name'], new_value)
        # NOTE: direct is a replacement so might aswell delete data to stop it being processed again.
        self.process_data[key]['data'] = None

    def delete_ignore(self, key, bangc=True):
        return
