"""The App.

.. module:: app
   :synopsis: The root (main) file for the proforma parser.

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""

# Minimal prototype test for new proforma parsing software.
# SQL Alchemy imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# TODO Remove unused sqlalchemy modules after finishing transaction scripts.

# System and logging imports
import logging
import sys
import configparser
import argparse

# Custom module imports
from proforma.proforma_operations import process_proforma_file, process_proforma_directory
from chado_object.conversions.proforma import process_data_input
from transaction.transaction_operations import process_chado_objects_for_transaction
from error.error_tracking import ErrorTracking, WARNING_ERROR

parser = argparse.ArgumentParser(description='Parse proforma files and load them into Chado.')
parser.add_argument('-v', '--verbose', help='Enable verbose mode.', action='store_true')
parser.add_argument('-c', '--config', help='Specify the location of the configuration file.', required=True)
parser.add_argument('-d', '--directory', help='Specify the directory of proformae to be loaded.', required=True)
parser.add_argument('-m', '--multithread', help='Specify the thread numbe if threaded.', required=False)
parser.add_argument('-l', '--load_type', help='Specify whether the load is \'test\' or \'production\'', required=True,
                    choices=['test', 'production'])
args = parser.parse_args()

if args.verbose:
    print("Running in Verbose mode")
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(levelname)s -- %(message)s')
    logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
    # comment/uncomment out below to notsee/see NOTICE messages for sql functions.
    # logging.getLogger('sqlalchemy.dialects.postgresql').setLevel(logging.INFO)
else:
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(levelname)s -- %(message)s')

thread_num = None
if args.multithread:
    thread_num = int(args.multithread)

log = logging.getLogger(__name__)

# Import secure config variables.
config = configparser.ConfigParser()
config.read(args.config)


def create_postgres_session():
    """Create the db connection/session."""
    USER = config['connection']['USER']
    PASSWORD = config['connection']['PASSWORD']
    SERVER = config['connection']['SERVER']
    if type(thread_num) is int:
        SERVER += "_{}".format(thread_num)
    DB = config['connection']['DB']

    log.info('Using server: {}'.format(SERVER))
    log.info('Using database: {}'.format(DB))

    # Create our SQL Alchemy engine from our environmental variables.
    engine_var = 'postgresql://' + USER + ":" + PASSWORD + '@' + SERVER + '/' + DB
    log.debug("PORT engine_var = {}: thread is {}".format(engine_var, thread_num))
    engine = create_engine(engine_var)

    Session = sessionmaker(bind=engine)
    session = Session()

    return session


def get_error_summary():
    """Get the numbers and types or errors generated.

    Returns:
       the counts of critical and warning errors.
    """
    critical_count = 0
    warning_count = 0
    for instance in ErrorTracking.instances:
        if instance.error_level == WARNING_ERROR:
            warning_count += 1
        else:
            critical_count += 1
    return critical_count, warning_count


def obtain_list_of_proformae():
    """Obtain file list of proformae to be processed."""
    directory_to_process = args.directory

    list_of_proformae = process_proforma_directory(directory_to_process)

    return list_of_proformae


def check_load_type(load_type):
    """Check load type.

    Raise:
       Exit immediately if load type is not one of the recognised types.
    """
    if load_type not in ('test', 'production'):
        log.critical('load_type must be specified as either \'test\' or \'production\'')
        log.critical('Exiting.')
        sys.exit(-1)


def process_proforma(list_of_proformae):
    """Process the list of proforma and return a dict of object."""
    dict_of_processed_files = dict()
    curator_dict = dict(config['curators'])
    for proforma_location in list_of_proformae:
        log.info("Validating file {}".format(proforma_location))
        list_of_processed_proforma_objects = process_proforma_file(proforma_location, curator_dict)  # Processing individual proforma file.

        for processed_proforma_object in list_of_processed_proforma_objects:
            filename = processed_proforma_object.get_file_metadata().get('filename')

            if filename not in dict_of_processed_files:
                dict_of_processed_files[filename] = []  # Create a list within the dictionary entry if we don't have it already.
            dict_of_processed_files[filename].append(processed_proforma_object)  # Add the processed proforma object as a dict entry under the filename.

    log.info('--------------------')
    log.info('')
    log.info('Validation Summary.')
    log.info('Processed %s file(s).' % (len(dict_of_processed_files)))
    log.info('')
    return dict_of_processed_files


def proforma_to_chado(dict_of_processed_files):
    """Convert the proforma object to chado ones."""
    main_list_of_chado_objects_to_load = []
    for filename in dict_of_processed_files:
        log.debug('Converting proforma from file %s into ChadoObjects' % filename)
        for proforma_object_to_load in dict_of_processed_files[filename]:
            returned_list_of_chado_objects = process_data_input(proforma_object_to_load)
            main_list_of_chado_objects_to_load.extend(returned_list_of_chado_objects)
    return main_list_of_chado_objects_to_load


def process_errors(load_type):
    """Look at the errors and generate a summary and exit.

    If critical errors are found, no writing to the database occurs.
    """
    list_of_errors_transactions = [instance for instance in ErrorTracking.instances]

    if len(list_of_errors_transactions) > 0:

        critical_count, warning_count = get_error_summary()
        log.info('{} critical error(s) were found.'.format(critical_count))
        log.info('{} warning error(s) were found.'.format(warning_count))
        log.info('')

        for error_object in list_of_errors_transactions:
            index_to_print = list_of_errors_transactions.index(error_object) + 1
            error_object.print_error_messages(index_to_print)

        if critical_count:
            log.critical('Please the correct at least the critical ones or remove these file(s) before proceeding.')
            log.critical('No data was loaded into Chado.')
            log.critical('Exiting.')
            sys.exit(-1)
        elif warning_count:
            log.warning('Ignoring warnings for now!')
    else:
        log.info('0 critical error(s) were found.')
        log.info('0 warning error(s) were found.')
        if load_type == 'test':
            log.info('All files successfully tested against production Chado.')
            log.info('')
        elif load_type == 'production':
            log.info('All files successfully loaded into Chado.')
            log.info('bingo ....you success !....')
            log.info('')


def main(session, list_of_proformae):
    """Process list of proformae."""
    check_load_type(args.load_type)

    log.info('Opening and processing the list of proformae.')
    dict_of_processed_files = process_proforma(list_of_proformae)

    log.info("Starting conversion of proforma object to chado.")
    main_list_of_chado_objects_to_load = proforma_to_chado(dict_of_processed_files)

    # Send our list of Chado Objects off to be loaded into the database.
    log.info("Starting to load chado object into the database.")
    process_chado_objects_for_transaction(session, main_list_of_chado_objects_to_load, args.load_type)

    log.info('--------------------')
    log.info('')
    log.info('Transactions complete.')
    log.info('')
    log.info('Processed {} files'.format(len(list_of_proformae)))
    log.info('          {} proformae.'.format(len(main_list_of_chado_objects_to_load)))
    log.info('')

    # List errors and warning and Exit if any are critical
    process_errors(args.load_type)


if __name__ == '__main__':
    session = create_postgres_session()

    list_of_proformae = obtain_list_of_proformae()

    main(session, list_of_proformae)
