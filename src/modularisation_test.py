#################################################################################
# Test we can just use a dict of field + values as our start point for proforma 
# testing/loading. This is too make sure we do not have to start from files and
# we can just use a dict. i.e. if we have a graphical interface at some point we
# want to know NOW that the code can do this, rather than when it is too late to
# change the structure.
##################################################################################
# System and logging imports
import logging
import sys
import os
import configparser
import argparse
import time
import subprocess
import psycopg2

# Minimal prototype test for new proforma parsing software.
# SQL Alchemy imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#from app import 

from proforma.proforma_operations import Proforma
from validation.validation_operations import validate_proforma_object
from error.error_tracking import ErrorTracking
from chado_object.conversions.proforma import process_data_input
from transaction.transaction_operations import process_chado_objects_for_transaction


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(levelname)s -- %(message)s')
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
log = logging.getLogger(__name__)

def create_postgres_session():
    USER = config['connection']['USER']
    PASSWORD = config['connection']['PASSWORD']
    SERVER = config['connection']['SERVER']
    DB = config['connection']['DB']
    PORT = config['connection']['PORT']

    log.info('Using server: {}'.format(SERVER))
    log.info('Using database: {}'.format(DB))

    # Create our SQL Alchemy engine from our environmental variables.
    engine_var = 'postgresql://' + USER + ":" + PASSWORD + '@' + SERVER + ':' + PORT + '/' + DB

    engine = create_engine(engine_var)

    Session = sessionmaker(bind=engine)
    session = Session()

    return session
def stop_db(conn, debug):
    """
    shut down the test database instance
    """
    output = subprocess.getoutput('docker rm $(docker stop $(docker ps -a -q --filter ancestor=flybase/proformatestdb --format="{{.ID}}"))')
    if debug:
        print(output)
    if conn:
        conn.close()


def startup_db(debug=False):
    """
    start up the test database instance
    """

    # This first os.system command is a bit hacky, but it'll prevent errors where the database is already running
    # and we attempt to execute 'docker run' again. TODO Revisit this and handle "docker is already running" issues better.
    os.system('docker rm $(docker stop $(docker ps -a -q --filter ancestor=flybase/proformatestdb --format="{{.ID}}"))')
    os.system('docker run -p 127.0.0.1:5436:5432 --net proforma_net  --name proformatestdb flybase/proformatestdb &')

    conn = None
    trys = 0
    while (not conn and trys < 10):
        trys += 1
        time.sleep(5)
        try:
            conn = psycopg2.connect(host="127.0.0.1", port="5436", database="fb_test", user='tester', password="tester")
        except:
            pass

    if (not conn):
        print("ERROR: Could not connect to test db")
        stop_db(None, debug)
        exit(-1)
    if (debug):
        cursor = conn.cursor()
        cursor.execute("select 1 from feature limit 2")
        feat = cursor.fetchone()
        print("FEAT: {}".format(feat))
    return conn



# Import secure config variables.
config = configparser.ConfigParser()
config.read('../../../proforma/fb_local_test.cfg')

file_metadata = {
    'filename': 'None, getting from dictionary',
    'filename_short': 'Dict',
    'curator_initials': 'get from login',
    'curator_fullname': 'look up from login',
    'record_type': 'publication'
}
proforma_type = '! PUBLICATION PROFORMA                   Version 47:  25 Nov 2014'
proforma = Proforma(file_metadata, proforma_type, 0)

log.debug(proforma.file_metadata)



test_data = {'P22': 'FBrf0000014',
             'P46': 'somefile.jpg',
             'P31': 'FBrf0000014'}
for field, value in test_data.items():
    proforma.add_field_and_value(field, value, 0, None)

log.debug("proforma add filed values done")
log.debug(proforma.fields_values)

validate_proforma_object(proforma)

chado = process_data_input(proforma)
conn = startup_db(True)
log.debug("chado is of type {}".format(type(chado)))
session = create_postgres_session()
log.debug(dir(chado))
process_chado_objects_for_transaction(session, chado, 'test')

for instance in ErrorTracking.instances:
    log.debug(instance)
    instance.print_error_messages()

stop_db(conn, True)