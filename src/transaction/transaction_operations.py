"""
.. module:: transactions
   :synopsis: A set of functions to insert ChadoObjects into the Chado database.

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.dialects import postgresql
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

import sys
import logging
log = logging.getLogger(__name__)

# TODO Investigate use of listens_for filtering.
# @event.listens_for(GeneQuery, 'before_compile', retval=True)
# def restrict_gene_fields(query):
#     query = query.filter(Gene.organism_id == '1').\
#             filter(Gene.is_obsolete == 'f')
#     return query
def process_chado_objects_for_transaction(engine, list_of_objects_to_load, load_type):
    
    dict_of_errored_files = {}

    if load_type == 'production':
        log.warning('Production load specified. Changes to the production database will occur.')
    elif load_type == 'test':
        log.warning('Test load specified. Changes will not be written to the production database.')
    else:
        log.critical('Unrecognized load_type specificed.')
        log.critical('Exiting.')
        sys.exit(-1)

    Session = sessionmaker(bind=engine)
    session = Session()
    error_occurred = False
    for entry in list_of_objects_to_load:
        entry.obtain_session(session) # Send session to object.
        filename = entry.filename
        class_name = entry.__class__.__name__
        log.debug('All variables for entry:')
        log.debug(vars(entry))
        # TODO Add proforma field to error tracking from Chado Object.
        log.info('Initiating transaction for %s' % (class_name))
        log.info('Source file: %s' % (filename))
        log.info('Proforma object starts from line: %s' % (entry.proforma_start_line_number))
        
        try:
            entry.load_content()
            session.flush() # For printing out SQL statements in debug mode.
        except NoResultFound:
            session.rollback()
            current_query = entry.current_query
            current_query_source = entry.current_query_source
            dict_of_errored_files = insert_shared_error_lines('NoResultFound', dict_of_errored_files, filename, current_query_source, current_query)
            error_occurred = True
        except MultipleResultsFound:
            session.rollback()
            current_query = entry.current_query
            current_query_source = entry.current_query_source
            dict_of_errored_files = insert_shared_error_lines('MultipleResultsFound', dict_of_errored_files, filename, current_query_source, current_query)
            error_occurred = True
        except:
            session.rollback()
            log.critical('Critical transaction error occured, rolling back and exiting.')
            raise

    if error_occurred == False:
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

    return dict_of_errored_files

def insert_shared_error_lines(error_type, dict_of_errored_files, filename, current_query_source, current_query):
    if filename not in dict_of_errored_files:
        dict_of_errored_files[filename] = []

    error_list = [
        'Transaction error',
        current_query,
        'Proforma line: %s' % (current_query_source[2]),
        'Field: %s' % (current_query_source[0]),
        'Value: %s' % (current_query_source[1])
    ]

    if error_type == 'NoResultFound':
        no_results_found_errors = ['No results found.',
            'Please check whether this entry is correct.',
            ''
        ]
        error_list.extend(no_results_found_errors)
    elif error_type == 'MultipleResultsFound':
        multiple_results_found_error = 'This is most likely a developer error. Please inform Harvdev (Chris).'
        error_list.append(multiple_results_found_error)

    if error_list not in dict_of_errored_files[filename]:
        dict_of_errored_files[filename].append(error_list)

    log.error(filename)
    for entry in error_list:
        log.error(entry)

    return dict_of_errored_files


    

