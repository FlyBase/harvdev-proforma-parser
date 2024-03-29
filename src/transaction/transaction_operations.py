"""

:synopsis: A set of functions to insert ChadoObjects into the Chado database.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
import sys
import logging
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy import event
import traceback

from error.error_tracking import ErrorTracking, CRITICAL_ERROR

log = logging.getLogger(__name__)

# TODO Investigate use of listens_for filtering.
# @event.listens_for(GeneQuery, 'before_compile', retval=True)
# def restrict_gene_fields(query):
#     query = query.filter(Gene.organism_id == '1').\
#             filter(Gene.is_obsolete == 'f')
#     return query

last_query = None


def process_entry(entry, session, filename, references):
    """Process Entry.

    Process entry and deal with exceptions etc and just return if an error was seen.
    """
    error_occurred = False
    last_query = None  # Track the last executed query.
    chado_object = None

    engine = session.get_bind()

    @event.listens_for(engine, "before_cursor_execute")
    def comment_sql_calls(conn, cursor, statement, parameters,
                          context, executemany):
        # Add all executed queries to a list.
        global last_query
        try:
            last_query = statement % parameters
        except TypeError:  # If we don't have parameters to insert.
            last_query = statement

    try:
        log.debug(entry.process_data)
        chado_object = entry.load_content(references)
        session.flush()  # For printing out SQL statements in debug mode.
    except NoResultFound:
        # Create an error object.
        ErrorTracking(filename, None, None, 'Unexpected internal parser error. Please contact Harvdev. \n{} '
                                            'Last query below:'.format(traceback.format_exc()), last_query, None, CRITICAL_ERROR)
        error_occurred = True
    except MultipleResultsFound:
        # Create an error object.
        ErrorTracking(filename, None, None, 'Unexpected internal parser error. Please contact Harvdev. \n{} '
                                            'Last query below:'.format(traceback.format_exc()), last_query, None, CRITICAL_ERROR)
        error_occurred = True
    except Exception:
        # Create an error object.
        ErrorTracking(filename, None, None, 'Unexpected internal parser error. Please contact Harvdev. \n{} '
                                            'Last query below:'.format(traceback.format_exc()), last_query, None, CRITICAL_ERROR)
        error_occurred = True
    return chado_object, error_occurred


def load_message(load_type):
    """Print message wrt type."""
    if load_type == 'production':
        log.warning('Production load specified. Changes to the production database will occur.')
    elif load_type == 'test':
        log.warning('Test load specified. Changes will not be written to the production database.')
    else:
        log.critical('Unrecognized load_type specified.')
        log.critical('Exiting.')
        sys.exit(-1)


def process_entries(session, list_of_objects_to_load):
    """Process the list of objects."""
    error_occurred = False
    references = {}
    last_file = None
    for entry in list_of_objects_to_load:
        entry.obtain_session(session)  # Send session to object.
        filename = entry.filename
        if filename != last_file:
            log.debug("{} DOEs not equal {}".format(filename, last_file))
            references = {}
            last_file = filename
        class_name = entry.__class__.__name__
        # TODO Add proforma field to error tracking from Chado Object.
        log.debug('Initiating transaction for %s' % (class_name))
        log.debug('Source file: %s' % (filename))
        log.debug('Proforma object starts from line: %s' % (entry.proforma_start_line_number))

        chado_object, error_occurred = process_entry(entry, session, filename, references)
        references[class_name] = chado_object
        error_occurred |= error_occurred
    return error_occurred


def process_chado_objects_for_transaction(session, list_of_objects_to_load, load_type):
    """Process object for a transaction.

    Args:
        session: sql session
        list_of_objects_to_load: list of objects to load, of various different proforma
        load_type: 'test' or 'production'
    """
    load_message(load_type)

    error_occurred = process_entries(session, list_of_objects_to_load)

    # Check for critical errors.
    list_of_errors_transactions = [instance for instance in ErrorTracking.instances]

    if len(list_of_errors_transactions) > 0:
        for instance in ErrorTracking.instances:
            if instance.error_level == CRITICAL_ERROR:
                error_occurred = True
                if load_type == 'production':
                    break

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
    elif error_occurred:
        log.critical('Rolling back all transactions due to a critical error.')
        session.rollback()
