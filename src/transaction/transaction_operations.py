"""
.. module:: transactions
   :synopsis: A set of functions to insert ChadoObjects into the Chado database.

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
import sys
import logging
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy import event

from error.error_tracking import ErrorTracking, CRITICAL_ERROR
from chado_object.chado_base import LINE_NUMBER
from chado_object.chado_exceptions import ValidationError

log = logging.getLogger(__name__)

# TODO Investigate use of listens_for filtering.
# @event.listens_for(GeneQuery, 'before_compile', retval=True)
# def restrict_gene_fields(query):
#     query = query.filter(Gene.organism_id == '1').\
#             filter(Gene.is_obsolete == 'f')
#     return query

def process_entry(entry, session, filename):
    """
    Process Entry and deal with excpetions etc and just return if an error was seen.
    """
    error_occurred = False
    executed_queries = [] # List for tracking all the executed queries.

    engine = session.get_bind()
    @event.listens_for(engine, "before_cursor_execute")
    def comment_sql_calls(conn, cursor, statement, parameters,
                          context, executemany):
        # Add all executed queries to a list.
        executed_queries.append(statement % parameters)

    try:
        entry.load_content()
        session.flush()  # For printing out SQL statements in debug mode.
    except NoResultFound as e:
        session.rollback()
        # Create an error object.
        ErrorTracking(filename, None, None, 'Unexpected internal parser error. NoResultFound. Please contact Harvdev. '
                                            'Last query below:', executed_queries[-1], CRITICAL_ERROR)
        error_occurred = True
    except MultipleResultsFound:
        session.rollback()
        # Create an error object.
        ErrorTracking(filename, None, None, 'Unexpected internal parser error. MultipleResultsFound. Please contact '
                                            'Harvdev. Last query below:', executed_queries[-1], CRITICAL_ERROR)
        error_occurred = True
    except ValidationError:
        current_query = entry.current_query
        current_query_source = entry.current_query_source
        # Create an error object.
        log.critical("Raise of Validation should not be used any more and replaced with Chado's critical_error")
        ErrorTracking(filename, None, current_query_source[LINE_NUMBER], 'Validation Error.', current_query, CRITICAL_ERROR)
        error_occurred = True
    except Exception as e:
        session.rollback()
        log.critical(entry.current_query)
        log.critical('Unexpected exception {}'.format(e))
        # Create an error object.
        ErrorTracking(filename, None, None, 'Unexpected internal parser error. Exception: {}. Please contact Harvdev. '
                                            'Last query below:'.format(e), executed_queries[-1], CRITICAL_ERROR)
    return error_occurred


def process_chado_objects_for_transaction(session, list_of_objects_to_load, load_type):
    """
    session: sql session
    list_of_objects_to_load: list of objects to load, of various different proforma
    load_type: 'test' or 'production'
    """
    if load_type == 'production':
        log.warning('Production load specified. Changes to the production database will occur.')
    elif load_type == 'test':
        log.warning('Test load specified. Changes will not be written to the production database.')
    else:
        log.critical('Unrecognized load_type specified.')
        log.critical('Exiting.')
        sys.exit(-1)

    error_occurred = False
    for entry in list_of_objects_to_load:
        entry.obtain_session(session)  # Send session to object.
        filename = entry.filename
        class_name = entry.__class__.__name__
        log.debug('All variables for entry:')
        log.debug(vars(entry))
        # TODO Add proforma field to error tracking from Chado Object.
        log.info('Initiating transaction for %s' % (class_name))
        log.info('Source file: %s' % (filename))
        log.info('Proforma object starts from line: %s' % (entry.proforma_start_line_number))

        error_occurred |= process_entry(entry, session, filename)

    if not error_occurred:
        if load_type == 'production':
            session.commit()
        elif load_type == 'test':
            log.warning('Rolling back all transactions due to test mode.')
            session.rollback()
        else:
            session.rollback()
            log.critical('Unrecognized load_type specificed. Rolling back.')
            log.critical('Exiting.')
            sys.exit(-1)
