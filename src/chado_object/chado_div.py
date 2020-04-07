"""

:synopsis: The "div" ChadoObject.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>, Ian Longden <ilongden@morgan.harvard.edu>
"""
import logging
import os
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound

from harvdev_utils.chado_functions import get_or_create
from harvdev_utils.production import (
    Feature, FeatureDbxref, FeatureSynonym, FeaturePub,
    Humanhealth, HumanhealthFeature
)
from chado_object.chado_base import FIELD_VALUE
from chado_object.feature.chado_feature import ChadoFeatureObject
from chado_object.utils.dbxref import get_dbxref_by_params
from chado_object.utils.feature_dbxref import fd_add_by_ids
from chado_object.utils.organism import get_default_organism
from error.error_tracking import CRITICAL_ERROR

log = logging.getLogger(__name__)


class ChadoDiv(ChadoFeatureObject):
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
        self.type_dict = {'humanhealth_feature': self.load_humanhealth_feature,
                          'synonym': self.load_synonym,
                          'ignore': self.ignore,
                          'data_set': self.ignore,  # Done separately
                          'featureprop': self.load_featureprop,
                          'dissociate': self.delete,
                          'rename': self.rename}

        self.delete_dict = {'ignore': self.ignore,
                            'synonym': self.delete_synonym,
                            'humanhealth_feature': self.delete_humanhealth_feature,
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
        self.feature = None
        self.type_name = 'div'

    def get_div(self):
        """Get the DIV."""
        div_name = self.process_data['DIV1a']['data'][FIELD_VALUE]
        if self.process_data['DIV1c']['data'][FIELD_VALUE] == "n":
            self.new = True
        cvterm = self.cvterm_query(self.process_data['DIV1a']['cv'], self.process_data['DIV1a']['cvterm'])
        organism = get_default_organism(self.session)
        self.feature, is_new = get_or_create(self.session, Feature, organism_id=organism.organism_id, uniquename=div_name, name=div_name, type_id=cvterm)
        if self.new != is_new:
            if self.new:
                message = "{} already exists but DIV1d specifys it should not.".format(div_name)
            else:
                message = "{} does not exist but DIV1d specifys it should.".format(div_name)
            self.critical_error(self.process_data['DIV1a']['data'], message)
        if self.has_data('DIV1d'):
            self.session.delete(self.feature)
            self.feature = None
            return None

    def rename(self, key):
        """Rename the DIV."""
        if not self.has_data(key):
            return
        self.feature.uniquename = self.process_data[key]['data'][FIELD_VALUE]
        self.feature.name = self.process_data[key]['data'][FIELD_VALUE]
        self.load_synonym(key)

    def create_set_initial_params(self, set_key, data_set):
        """Create params for a set.

        Create initial params to be used for dbxrefprop generation.

        Args:
            set_key (str): the key for the set  i.e. HH5 or HH14.

            data_set (dict): dictionary from yml control file.

        Returns:
            params (dict): dictionary fo elements needed to create a dbxrefprop

        """
        # params = {'cvterm': self.process_data[set_key]['cvterm'],
        #          'cvname': self.process_data[set_key]['cv']}
        params = {}

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

    def load_content(self, references):
        """Process the proforma data."""
        try:
            self.pub = references['ChadoPub']
        except KeyError:
            message = "Unable to find publication."
            self.critical_error(self.process_data['G1a']['data'], message)
            return None

        self.get_div()

        if not self.feature:  # Only proceed if we have a div. Otherwise we had an error.
            return self.feature

        # feature pub
        get_or_create(self.session, FeaturePub, feature_id=self.feature.feature_id, pub_id=self.pub.pub_id)

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
        return self.feature

    def process_sets(self):
        """Process the set data.

        Sets have a specific key, normally the shortened version of the fields
        that it uses. i.e. For Div3a, Div3b etc this becomes DIV3.
        self.set_values is a dictionary of these and points to an list of the
        actual values the curators have added i.e. Div3a, Div3c
        This is an example of what the set_values will look like.

        .. code-block:: JSON

            'DIV3': [{'DIV3a': ('DIV3a', '1900', 18, None),
                      'DIV3b': ('DIV3b', 'HGNC', 19, None),
                      'DIV3c': ('DIV3c', 'hgnc - 1900 -- description', 20, None)}]

        This comes from the test 1900_Div_cretae,txt
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
            dbxref, is_new = get_dbxref_by_params(self.session, params)
            if is_new:
                error_message = "Cannot dissociate as dbxref does not exist"
                self.error_track(data_set[acc_key], error_message, CRITICAL_ERROR)
            else:
                try:
                    f_db = self.session.query(FeatureDbxref).\
                        filter(FeatureDbxref.feature_id == self.feature.feature_id,
                               FeatureDbxref.dbxref_id == dbxref.dbxref_id,
                               FeatureDbxref.is_current == 't').one()
                    f_db.is_current = False
                except NoResultFound:
                    error_message = "Cannot dissociate as feature dbxref does not exist"
                    self.error_track(data_set[acc_key], error_message, CRITICAL_ERROR)
            return
        else:
            log.debug("Dis key NOT set so create stuff")

        params['tuple'] = data_set[acc_key]
        params['feature_id'] = self.feature.feature_id
        try:
            dbxref, _ = get_dbxref_by_params(self.session, params)
        except NoResultFound:
            error_message = "DB {} Could not be found in chado?".format(params['dbname'])
            self.error_track(data_set[acc_key], error_message, CRITICAL_ERROR)
            return
        fd_add_by_ids(self.session, self.feature.feature_id, dbxref.dbxref_id)

    def ignore(self, key):
        """Ignore."""
        pass

    def load_humanhealth_feature(self, key):
        """Load humanhealth feature."""
        if not self.has_data(key):
            return

        for hh_tup in self.process_data[key]['data']:
            try:
                hh_obj = self.session.query(Humanhealth).\
                    filter(Humanhealth.uniquename == hh_tup[FIELD_VALUE],
                           Humanhealth.is_obsolete == 'f').one()
            except NoResultFound:
                error_message = "Humanhealth {} Could not be found in chado?".format(hh_tup[FIELD_VALUE])
                self.error_track(hh_tup, error_message, CRITICAL_ERROR)
                continue
            hhf, _ = get_or_create(self.session, HumanhealthFeature, feature_id=self.feature.feature_id,
                                   humanhealth_id=hh_obj.humanhealth_id, pub_id=self.pub.pub_id)

# Deletion routines
    def delete(self, key):
        """Ignore."""
        pass

    def delete_synonym(self, key, bangc):
        """Delete Synonym bangc only allowed."""
        if not self.has_data(key):
            return

        # make all synonyms not current
        for fs in self.session.query(FeatureSynonym).\
            filter(FeatureSynonym.feature_id == self.feature.feature_id,
                   FeatureSynonym.pub_id == self.pub_id):
            fs.is_current = False

    def delete_humanhealth_feature(self, key, bangc):
        """Delete the humanhealth feature."""
        if bangc:
            # delete them all
            self.session.query(HumanhealthFeature).\
                filter(HumanhealthFeature.feature_id == self.feature.feature_id).delete()
            return
        for hh_tup in self.process_data[key]['data']:
            # get specific hh
            try:
                hh_obj = self.session.query(Humanhealth).\
                    filter(Humanhealth.uniquename == hh_tup[FIELD_VALUE],
                           Humanhealth.is_obsolete == 'f').one()
            except NoResultFound:
                error_message = "Humanhealth {} Could not be found in chado?".format(hh_tup[FIELD_VALUE])
                self.error_track(hh_tup, error_message, CRITICAL_ERROR)
                continue
            # delete hh_f
            self.session.query(HumanhealthFeature).\
                filter(HumanhealthFeature.feature_id == self.feature.feature_id,
                       HumanhealthFeature.humanhealth_id == hh_obj.humanhealth_id).delete()
        self.process_data[key]['data'] = None

    def delete_comment(self, key):
        """Ignore."""
        pass
