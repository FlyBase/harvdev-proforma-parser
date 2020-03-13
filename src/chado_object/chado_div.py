"""

:synopsis: The "div" ChadoObject.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>, Ian Longden <ilongden@morgan.harvard.edu>
"""
from harvdev_utils.production import (
    Feature
)
from src.chado_object.chado_base import ChadoObject, FIELD_VALUE
from harvdev_utils.chado_functions import get_or_create
from src.error.error_tracking import CRITICAL_ERROR
from src.chado_object.utils.feature_dbxref import fd_add_by_ids
from src.chado_object.utils.dbxref import get_dbxref_by_params

# from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime
import os
import logging

log = logging.getLogger(__name__)


class ChadoDiv(ChadoObject):
    """Process the Disease Implicated Variation (DIV) Proforma."""

    def __init__(self, params):
        """Initialise the chado object."""
        log.debug('Initializing ChadoDiv object.')

        self.proforma_start_line_number = params.get('proforma_start_line_number')
        self.reference = params.get('reference')
        self.set_values = params.get('set_values')
        self.new = False

        ###########################################################
        # Values queried later, placed here for reference purposes.
        ############################################################
        self.pub = None             # All other proforma need a reference to a pub

        # yaml file defines what to do with each field. Follow the light
        self.type_dict = {'feature_relationship': self.load_feature_relationship,
                          'synonym': self.load_synonym,
                          'ignore': self.ignore,
                          'data_set': self.ignore,  # Done separately
                          'comment': self.load_comment,
                          'dissociate': self.delete}

        self.delete_dict = {'ignore': self.ignore,
                            'synonym': self.delete_synonym,
                            'feature_relationship': self.delete_feature_relationship,
                            'comment': self.delete_comment}

        # Initiate the parent.
        super(ChadoDiv, self).__init__(params)

        ############################################################
        # Get processing info and data to be processed.
        # Please see the yml/chemical.yml file for more details
        ############################################################
        yml_file = os.path.join(os.path.dirname(__file__), 'yml/div.yml')
        # Populated self.process_data with all possible keys.
        self.process_data = self.load_reference_yaml(yml_file, params)

    def get_div(self):
        """Get the DIV."""
        div_name = self.process_data['DIV1a']['data'][FIELD_VALUE]
        if self.process_data['DIV1c']['data'][FIELD_VALUE] == "n":
            self.new = True
        cvterm = self.cvterm_query(self.process_data['DIV1a']['cv'], self.process_data['DIV1a']['cvname'])
        self.div, is_new = get_or_create(self.session, Feature, uniquename=div_name, name=div_name, type_id=cvterm.cvterm_id)
        if self.new != is_new:
            if self.new:
                message = "{} already exists but DIV1d specifys it should not.".format(div_name)
            else:
                message == "{} does not exist but DIV1d specifys it should.".format(div_name)
            self.critical_error(self.process_data['DIV1a']['data'], message)

    def create_set_initial_params(self, set_key, data_set):
        """Create params for a set.

        Create initial params to be used for dbxrefprop generation.

        Args:
            set_key (str): the key for the set  i.e. HH5 or HH14.

            data_set (dict): dictionary from yml control file.

        Returns:
            params (dict): dictionary fo elements needed to create a dbxrefprop

        """
        params = {'cvterm': self.process_data[set_key]['cvterm'],
                  'cvname': self.process_data[set_key]['cv']}

        db_key = set_key + self.process_data[set_key]['set_db']
        if db_key not in data_set:
            acc_key = set_key + self.process_data[set_key]['set_acc']
            if acc_key in data_set:
                error_message = "Set {} does not have {} specified".format(set_key, db_key)
                self.error_track(data_set[acc_key], error_message, CRITICAL_ERROR)
                return False
        elif db_key not in data_set or not data_set[db_key][FIELD_VALUE]:
            error_message = "Set {} does not have {} specified".format(set_key, db_key)
            self.error_track(data_set[db_key], error_message, CRITICAL_ERROR)
            return False
        else:
            params['dbname'] = data_set[db_key][FIELD_VALUE]

        desc_key = set_key + self.process_data[set_key]['set_desc']
        if desc_key in data_set:
            params['description'] = data_set[desc_key][FIELD_VALUE]

        return params

    def load_content(self):
        """Process the proforma data."""
        self.pub = super(ChadoDiv, self).pub_from_fbrf(self.reference)

        self.get_div()

        if not self.div:  # Only proceed if we have a div. Otherwise we had an error.
            return

        # bang c/d first as this supersedes all things
        if self.bang_c:
            self.bang_c_it()
        if self.bang_d:
            self.bang_d_it()

        if self.set_values:
            self.process_sets()
        else:
            log.debug("No set values")

        for key in self.process_data:
            self.type_dict[self.process_data[key]['type']](key)

        timestamp = datetime.now().strftime('%c')
        curated_by_string = 'Curator: %s;Proforma: %s;timelastmodified: %s' % (self.curator_fullname, self.filename_short, timestamp)
        log.debug('Curator string assembled as:')
        log.debug('%s' % (curated_by_string))

    def process_sets(self):
        """Process the set data.

        Sets have a specific key, normally the shortened version of the fields
        that it uses. i.e. For HH5a, HH5b etc this becomes HH5.
        self.set_values is a dictionary of these and points to an list of the
        actual values the curators have added i.e. HH5a, HH5c
        This is an example of what the set_values will look like.

        .. code-block:: JSON

            {
              HH5: [{'HH5a': ('HH5a', '1111111', 16),
               'HH5b': ('HH5b', 'HGNC', 17),
               'HH5c': ('HH5c', 'hgnc_1', 18)},
              {'HH5a': ('HH5a', '2', 20),
               'HH5b': ('HH5b', 'UniProtKB/Swiss-Prot', 21),
               'HH5c': ('HH5c', 'sw_2', 22)},
              {'HH5a': ('HH5a', '3', 24),
                'HH5b': ('HH5b', 'UniProtKB/Swiss-Prot', 25),
                'HH5c': ('HH5c', None, 26)},
              {'HH5a': ('HH5a', '4444444', 28),
               'HH5b': ('HH5b', 'HGNC', 29),
               'HH5c': ('HH5c', 'hgnc_4', 30)},
              {'HH5a': ('HH5a', '1', 32),
               'HH5b': ('HH5b', 'HGNC', 33),
               'HH5c': ('HH5c', 'already exists so desc not updated', 34)},
              {'HH5a': ('HH5a', None, 36),
               'HH5b': ('HH5b', None, 37),
               'HH5c': ('HH5c', None, 38)
             ]
            }

        This comes from the test 1505_HH_5abc_good_set.txt.sm.edit.1
        """
        for key in self.set_values.keys():
            log.debug("SV: {}: {}".format(key, self.set_values[key]))
            if key == 'DIV3':
                self.process_data_link(key)
            else:
                log.critical("Unknown set {}".format(key))
                return

    def process_data_link(self, set_key):
        """Set the feature dbxref.

        Args:
            set_key: Key to process i.e DIV3

        TODO: disassociation 'd' still needs to be coded.
        """
        for data_set in self.set_values[set_key]:
            if self.process_data[set_key]['sub_type'] == 'feature_dbxref':
                self.process_set_fd(set_key, data_set)
            else:
                log.critical("sub_type for this data set unknown")

    def process_set_fd(self, set_key, data_set):
        """Create/Dissociate the dbxref for this data_set.

        Args:
            set_key (str): Key for the set i.e. DIV3

            data_set (dict): One complete set of data.

        Returns:
            None

        """
        valid_key = self.get_valid_key_for_data_set(data_set)
        if not valid_key:
            return

        params = self.create_set_initial_params(set_key, data_set)
        if not params:
            return

        acc_key = set_key + self.process_data[set_key]['set_acc']
        if acc_key not in data_set:
            error_message = "Set {} does not have {} specified".format(set_key, acc_key)
            self.error_track(data_set[valid_key], error_message, CRITICAL_ERROR)
            return
        if not data_set[acc_key][FIELD_VALUE]:
            error_message = "Set {} does not have {} specified".format(set_key, acc_key)
            self.error_track(data_set[acc_key], error_message, CRITICAL_ERROR)
            return
        else:
            params['accession'] = data_set[acc_key][FIELD_VALUE]

        dis_key = set_key + self.process_data[set_key]['set_dis']
        if dis_key in data_set and data_set[dis_key][FIELD_VALUE] == 'y':
            log.debug("dis_key is set so delete stuff")
            params['tuple'] = data_set[acc_key]
            self.bangd_feature_dbxref(params)
            return
        else:
            log.debug("Dis key NOT set so create stuff")

        params['tuple'] = data_set[acc_key]
        params['feature_id'] = self.div.feature_id
        dbxref, _ = get_dbxref_by_params(self.session, params)
        fd_add_by_ids(self.session, self.div.feature_id, dbxref.dbxref_id)

    def ignore(self, key):
        """Ignore."""
        pass

    def load_feature_relationship(self, key):
        """Ignore."""
        pass

    def load_synonym(self, key):
        """Ignore."""
        pass

    def load_comment(self, key):
        """Ignore."""
        pass

# Deletion routines
    def delete(self, key):
        """Ignore."""
        pass

    def delete_synonym(self, key):
        """Ignore."""
        pass

    def delete_feature_relationship(self, key):
        """Ignore."""
        pass

    def delete_comment(self, key):
        """Ignore."""
        pass
