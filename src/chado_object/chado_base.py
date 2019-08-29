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

    def cvterm_query(self, cv_name, cv_term_name, session):
        log.debug('Querying for cv_term_name \'%s\'.' % cv_term_name)

        filters = (
            Cv.name == cv_name,
            Cvterm.name == cv_term_name,
            Cvterm.is_obsolete == 0
        )

        results = session.query(Cv.name, Cvterm.name, Cvterm.is_obsolete, Cvterm.cvterm_id).\
            join(Cvterm).\
            filter(*filters).\
            one()

        return results[3]

    def pub_from_fbrf(self, fbrf_tuple, session):
        """
        Return pub object for a given fbrf.
        Return None if it does not exist.
        """
        log.debug('Querying for FBrf \'%s\'.' % (fbrf_tuple[FIELD_VALUE]))

        pub = session.query(Pub).\
            filter(Pub.uniquename == fbrf_tuple[FIELD_VALUE]).\
            one_or_none()
        return pub

    def feature_from_feature_name(self, feature_name, session):
        log.debug('Querying for feature uniquename from feature id \'%s\'.' % feature_name)

        feature = session.query(Feature).\
            filter(Feature.name == feature_name).\
            one()

        return feature

    def synonym_id_from_synonym_symbol(self, synonym_name_tuple, synonym_type_id, session):
        log.debug('Querying for synonym \'%s\'.' % synonym_name_tuple[FIELD_VALUE])

        results = session.query(Synonym.synonym_id, Synonym.name, Synonym.type_id).\
            filter(Synonym.name == synonym_name_tuple[FIELD_VALUE]).\
            filter(Synonym.type_id == synonym_type_id).\
            one()

        return results[0]
