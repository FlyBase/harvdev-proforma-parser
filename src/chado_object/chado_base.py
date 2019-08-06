"""
.. module:: chado_base
   :synopsis: The "base" object for a ChadoObject. The properties here are shared by all other ChadoObjects.

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
import logging
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
