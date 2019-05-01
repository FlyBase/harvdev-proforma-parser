"""
.. module:: chado_base
   :synopsis: The "base" object for a ChadoObject. The properties here are shared by all other ChadoObjects.

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
import logging
from harvdev_utils.production import *

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects import postgresql

log = logging.getLogger(__name__)

class ChadoObject(object):
    def __init__(self, params):

        # Query tracking
        self.current_query = None

        # Metadata
        self.proforma_start_line_number = params.get('proforma_start_line_number')
        self.filename = params['file_metadata'].get('filename')
        self.filename_short = params['file_metadata'].get('filename')
        self.curator_fullname = params['file_metadata'].get('curator_fullname')

        # Data
        self.bang_c = params.get('bang_c')
        self.bang_d = params.get('bang_d')

    # TODO Create wrapper for this to bring along non-processed values for error reporting.
    # Credit to Erik Taubeneck for this awesome trick.
    # https://skien.cc/blog/2014/02/06/sqlalchemy-and-race-conditions-follow-up-on-commits-and-flushes/
    def get_one_or_create(self, session, model, create_method='', create_method_kwargs=None, **kwargs):
        log.info('Running \'get one or create\' query.')
        try:
            attempt = session.query(model).filter_by(**kwargs).one()
            log.debug(attempt)
            self.current_query = attempt
            log.info('Found previous entry for %s, insert not required.' % (kwargs))
        except NoResultFound:
            kwargs.update(create_method_kwargs or {})
            log.info('Previous entry for %s not found. Adding insert.' % (kwargs))
            try:
                with session.begin_nested():
                    created = getattr(model, create_method, model)(**kwargs)
                    session.add(created)
                    #TODO Add session.flush() here?
                    log.debug(created)
                    self.current_query = created
            except IntegrityError:
                attempt = session.query(model).filter_by(**kwargs).one()
                log.debug(attempt)
                self.current_query = attempt

    def cvterm_query(self, cv_name, cv_term_name, session):
        self.current_query = 'Querying for cv_term_name \'%s\'.' % (cv_term_name)
        log.info(self.current_query)
        
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

    def pub_id_from_fbrf(self, fbrf_tuple, session):
        self.current_query_source = fbrf_tuple
        self.current_query = 'Querying for FBrf \'%s\'.' % (fbrf_tuple[1])
        log.info(self.current_query)

        results = session.query(Pub.uniquename, Pub.pub_id).\
                filter(Pub.uniquename == fbrf_tuple[1]).\
                one()

        return results[1]

    def feature_id_from_feature_name(self, feature_name_tuple, session):
        self.current_query_source = feature_name_tuple
        self.current_query = 'Querying for feature \'%s\'.' % (feature_name_tuple[1])
        log.info(self.current_query)

        results = session.query(Feature.feature_id, Feature.name).\
                filter(Feature.name == feature_name_tuple[1]).\
                one()

        return results[0]

    def uniquename_from_feature_id(self, feature_id, session):
        self.current_query_source = feature_id
        self.current_query = 'Querying for feature uniquename from feature id \'%s\'.' % (feature_id)
        log.info(self.current_query)

        results = session.query(Feature.uniquename).\
            filter(Feature.feature_id == feature_id).\
            one()

        return results[0]

    def synonym_id_from_synonym_symbol(self, synonym_name_tuple, synonym_type_id, session):
        self.current_query_source = synonym_name_tuple
        self.current_query = 'Querying for synonym \'%s\'.' % (synonym_name_tuple[1])
        log.info(self.current_query)

        results = session.query(Synonym.synonym_id, Synonym.name, Synonym.type_id).\
                filter(Synonym.name == synonym_name_tuple[1]).\
                filter(Synonym.type_id == synonym_type_id).\
                one()

        return results[0]