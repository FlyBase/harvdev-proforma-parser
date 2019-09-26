"""
.. module:: chado_base
   :synopsis: The "base" object for a ChadoObject. The properties here are shared by all other ChadoObjects.

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
import logging
import yaml
from harvdev_utils.production import (
    Cv, Cvterm, Feature, Pub, Synonym
)
from error.error_tracking import ErrorTracking, CRITICAL_ERROR, WARNING_ERROR

log = logging.getLogger(__name__)

# tuple positions. Allows for clearer reading of code.
FIELD_NAME = 0
FIELD_VALUE = 1
LINE_NUMBER = 2
SET_BANG = 3  # For 'set' data we hold the wether it is a bangc, bangd or None.


class ChadoObject(object):
    def __init__(self, params):

        # Metadata
        self.proforma_start_line_number = params.get('proforma_start_line_number')
        self.filename = params['file_metadata'].get('filename')
        self.filename_short = params['file_metadata'].get('filename')
        self.curator_fullname = params['file_metadata'].get('curator_fullname')

        # Data
        self.bang_c = params.get('bang_c')
        self.bang_d = params.get('bang_d')
        self.process_data = None

    def obtain_session(self, session):
        self.session = session

    def load_reference_yaml(self, filename, params):
        # TODO Change bang_c "blank" processing to not require an empty process_data[key]['data'] entry.
        process_data = yaml.load(open(filename))
        keys_to_remove = []
        for key in process_data:
            log.debug('process data {}'.format(process_data[key]))
            if process_data[key]['type'] == 'data_set':
                continue
            if key in params['fields_values']:
                if type(params['fields_values'][key]) is list:
                    # Skip if the first value in the list contains None.
                    if params['fields_values'][key][0][FIELD_VALUE] is None and self.bang_c != key:
                        log.debug("Skipping field {} -- it's value is empty in the proforma.".format(key))
                        keys_to_remove.append(key)
                else:
                    # Skip if the value contains None.
                    if params['fields_values'][key][FIELD_VALUE] is None and self.bang_c != key:
                        log.debug("Skipping field {} -- it's value is empty in the proforma.".format(key))
                        keys_to_remove.append(key)

                # If the key exists and it has a non-None value, add it.
                process_data[key]['data'] = params['fields_values'][key]
                log.debug("{}: {}".format(key, process_data[key]))
            else:
                # If the key is missing from the proforma.
                log.debug("Skipping field {} -- it's absent from the proforma.".format(key))
                keys_to_remove.append(key)

        # Remove all unused keys from the dictionary.
        # This has to be a second loop so we don't modify the first loop while it's running.
        for key in keys_to_remove:
            log.debug("Removing unused key {} from the process_data dictionary".format(key))
            process_data.pop(key)

        return process_data

    def get_valid_key_for_data_set(self, data_set):
        """
        Basically check we have at least one valid key and the data is
        not empty.
        """
        valid_key = None  # need a valid key incase something is wrong to report line number etc
        for key in data_set.keys():
            if type(data_set[key]) is not list and data_set[key][FIELD_VALUE]:
                valid_key = key
            elif type(data_set[key]) is list and data_set[key][0][FIELD_VALUE]:
                valid_key = key

        return valid_key

    def has_data(self, key):
        # Checks whether a key exists and contains a FIELD_VALUE that isn't None.
        if key in self.process_data:
            log.debug('Checking whether we have data (not-None) in {}'.format(self.process_data[key]))
            if self.process_data[key]['data'] is not None:
                if type(self.process_data[key]['data']) is list:
                    if self.process_data[key]['data'][0][FIELD_VALUE] is not None:
                        return True
                else:
                    if self.process_data[key]['data'][FIELD_VALUE] is not None:
                        return True
        return False

    def error_track(self, tuple, error_message, level):
        ErrorTracking(self.filename,
                      "Proforma entry starting on line: {}".format(self.proforma_start_line_number),
                      "Proforma error around line: {}".format(tuple[LINE_NUMBER]),
                      'Validation Error.',
                      "{}: {}".format(tuple[FIELD_NAME], error_message),
                      level)

    def critical_error(self, tuple, error_message):
        self.error_track(tuple, error_message, CRITICAL_ERROR)

    def warning_error(self, tuple, error_message):
        self.error_track(tuple, error_message, WARNING_ERROR)

    def cvterm_query(self, cv, cvterm):
        """
        :param cv: str. The name of the cv to lookup.
        :param cvterm: str. The name of the cvterm to lookup.
        :return: str. The cvterm_id from the query.
        """
        log.debug('Querying for cvterm: {} from cv: {}.'.format(cvterm, cv))

        filters = (
            Cv.name == cv,
            Cvterm.name == cvterm,
            Cvterm.is_obsolete == 0
        )

        results = self.session.query(Cv.name, Cvterm.name, Cvterm.is_obsolete, Cvterm.cvterm_id).\
            join(Cvterm).\
            filter(*filters).\
            one()

        return results[3]

    def pub_from_fbrf(self, fbrf_tuple):
        """
        Return pub object for a given fbrf.
        Return None if it does not exist.
        """
        log.debug('Querying for FBrf \'%s\'.' % (fbrf_tuple[FIELD_VALUE]))

        pub = self.session.query(Pub).\
            filter(Pub.uniquename == fbrf_tuple[FIELD_VALUE]).\
            one_or_none()
        return pub

    def feature_from_feature_name(self, feature_name):
        log.debug('Querying for feature uniquename from feature id \'%s\'.' % feature_name)

        feature = self.session.query(Feature).\
            filter(Feature.name == feature_name).\
            one()

        return feature

    def synonym_id_from_synonym_symbol(self, synonym_name_tuple, synonym_type_id):
        log.debug('Querying for synonym \'%s\'.' % synonym_name_tuple[FIELD_VALUE])

        results = self.session.query(Synonym.synonym_id, Synonym.name, Synonym.type_id).\
            filter(Synonym.name == synonym_name_tuple[FIELD_VALUE]).\
            filter(Synonym.type_id == synonym_type_id).\
            one()

        return results[0]

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
