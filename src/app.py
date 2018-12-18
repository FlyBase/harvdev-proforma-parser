"""
.. module:: app
   :synopsis: The root (main) file for the proforma parser.

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""

# Minimal prototype test for new proforma parsing software.
# SQL Alchemy imports
from sqlalchemy import create_engine, event
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.dialects import postgresql
from model.base import Base
from model.tables import *
from model.constructed import *
# TODO Remove unused sqlalchemy modules after finishing transaction scripts.

# System and logging imports
import os
import logging
import sys
import configparser
import argparse

# Custom module imports
from proforma.proforma_operations import *
from chado_object.conversions.proforma import *
from transaction.transaction_operations import *
from error.error_tracking import ErrorTracking

parser = argparse.ArgumentParser(description='Parse proforma files and load them into Chado.')
parser.add_argument('-v', '--verbose', help='Enable verbose mode.', action='store_true')
parser.add_argument('-c', '--config', help='Specify the location of the configuration file.', required=True)
parser.add_argument('-d', '--directory', help='Specify the directory of proformae to be loaded.', required=True)
parser.add_argument('-l', '--load_type', help='Specify whether the load is \'test\' or \'production\'', required=True,
                    choices=['test', 'production'])
args = parser.parse_args()

if args.verbose:
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(levelname)s -- %(message)s')
    logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
else:
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(levelname)s -- %(message)s')

def main():
    # Import secure config variables.
    config = configparser.ConfigParser()
    config.read(args.config)

    USER = config['connection']['USER']
    PASSWORD = config['connection']['PASSWORD']
    SERVER = config['connection']['SERVER']
    DB = config['connection']['DB']

    curator_dict = dict(config['curators'])

    log = logging.getLogger(__name__)

    # Obtain file list of proformae to be processed.
    directory_to_process = args.directory

    list_of_proformae = process_proforma_directory(directory_to_process)

    dict_of_processed_files = dict()

    log.info('Opening and processing the list of proformae.')

    for proforma_location in list_of_proformae:
        list_of_processed_proforma_objects = process_proforma_file(proforma_location, curator_dict) # Processing individual proforma file.

        for processed_proforma_object in list_of_processed_proforma_objects:
            filename = processed_proforma_object.get_file_metadata().get('filename')

            if filename not in dict_of_processed_files:
                    dict_of_processed_files[filename] = [] # Create a list within the dictionary entry if we don't have it already.
            dict_of_processed_files[filename].append(processed_proforma_object) # Add the processed proforma object as a dict entry under the filename.

    log.info('--------------------')
    log.info('')
    log.info('Validation Summary.')
    log.info('Processed %s file(s).' % (len(dict_of_processed_files)))

    list_of_errors_validation = [instance for instance in ErrorTracking.instances]

    if len(list_of_errors_validation) > 0:
        for error_object in list_of_errors_validation:
            error_object.print_error_messages()

    if len(list_of_errors_validation) > 0:
        log.critical('At least one errored file(s) found.')
        log.critical('Please fix or remove these file(s) before proceeding.')
        log.critical('No data was loaded into Chado.')
        log.critical('Exiting.')
        sys.exit(-1)
    else:
        log.info('All files successfully validated! Proceeding to transactions.')
        log.info('')

    main_list_of_chado_objects_to_load = []

    for filename in dict_of_processed_files:
        log.info('Converting proforma from file %s into ChadoObjects' % (filename))
        for proforma_object_to_load in dict_of_processed_files[filename]:
            returned_list_of_chado_objects = process_data_input(proforma_object_to_load)
            main_list_of_chado_objects_to_load.extend(returned_list_of_chado_objects)
 
    # Create our SQL Alchemy engine from our environmental variables.
    engine_var = 'postgresql://' + USER + ":" + PASSWORD + '@' + SERVER + '/' + DB

    engine = create_engine(engine_var)

    load_type = args.load_type
    if load_type not in ('test', 'production'):
        log.critical('load_type must be specified as either \'test\' or \'production\'')
        log.critical('Exiting.')
        sys.exit(-1)

    # Send our list of Chado Objects off to be loaded into the database.
    process_chado_objects_for_transaction(engine, main_list_of_chado_objects_to_load, load_type)

    log.info('--------------------')
    log.info('')
    log.info('Transactions complete.')
    log.info('')

    list_of_errors_transactions = [instance for instance in ErrorTracking.instances]

    if len(list_of_errors_transactions) > 0:
        for error_object in list_of_errors_transactions:
            error_object.print_error_messages()

    if len(list_of_errors_transactions) > 0:
        log.critical('At least one errored file(s) found.')
        log.critical('Please fix or remove these file(s) before proceeding.')
        log.critical('No data was loaded into Chado.')
        log.critical('Exiting.')
        sys.exit(-1)
    else:
        if load_type == 'test':
            log.info('All files successfully tested against production Chado.')
            log.info('')
        elif load_type == 'production':
            log.info('All files successfully loaded into Chado.')
            log.info('bingo ....you success !....')
            log.info('')

if __name__ == '__main__':
    main()