import sys, json, os, configparser, psycopg2, yaml, logging, pytest
sys.path.append('../../') # To access the model directories used in the main program.

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(levelname)s -- %(message)s')
log = logging.getLogger(__name__)

test_env = os.environ['TEST_ENV']

config_location = None
if test_env == 'local':
    config_location = '../../credentials/proforma/test.cfg'
elif test_env == 'travis':
    config_location = 'src/test/credentials/travis.cfg'

log.info('Using config file location: {}'.format(config_location))

# Import secure config variables.
config = configparser.ConfigParser()
config.read(config_location)

USER = config['connection']['USER']
PASSWORD = config['connection']['PASSWORD']
SERVER = config['connection']['SERVER']
DB = config['connection']['DB']

# Define our connection.
conn_string = "host=%s dbname=%s user=%s password='%s'" % (SERVER, DB, USER, PASSWORD)
# Attempt to get a connection
conn = psycopg2.connect(conn_string)

def connect(sql, conn):
    # Return the cursor and use it to perform queries.
    cursor = conn.cursor()
    # Execute the query.
    cursor.execute(sql) # If we have a variable (e.g. an FBgn) be sure to include it in the execute command.
    # Grab the results.
    records = cursor.fetchall()
    # Close the cursor  
    cursor.close()
    # Return a list of tuples
    return records

###############
# Tests below #
###############

# These tests have assertions which are the *opposite* of those found in `../test_integration/test_integration.py`

# Important note -- when checking for newly inserted test data, be sure to search by name whenever possible.
# Don't use newly created ids (e.g. synonym id) because they might not be the same between tests.

def test_188733_lc_edit_181225():
    # Testing for !d field in G1b to only remove feature_synonym CG10797.
    query = '''SELECT * 
    FROM feature_synonym 
    WHERE feature_synonym.pub_id = 332469 
    AND feature_synonym.feature_id = 3087057 
    AND feature_synonym.synonym_id = 1230505
    '''
    results = connect(query, conn)
    assert len(results) == 1

def test_195387_sm_edit_181223_part1():
    # Testing for !c field in G1b to remove all feature_synonyms.
    query = '''
    SELECT * FROM feature_synonym 
	WHERE feature_synonym.feature_id = 3107733 
    AND feature_synonym.is_current = 'f' 
    AND feature_synonym.pub_id = 339330 
    AND feature_synonym.is_internal = 'FALSE' 
    AND feature_synonym.synonym_id = 1172006
    '''
    results = connect(query, conn)
    assert len(results) == 1

def test_195387_sm_edit_181223_part2():
    # Testing for field in G1b to add Ac12F.
    query = '''
    SELECT * FROM feature_synonym, synonym 
	WHERE feature_synonym.feature_id = 3107733 
    AND feature_synonym.is_current = 'f' 
    AND feature_synonym.pub_id = 339330 
    AND feature_synonym.is_internal = 'FALSE' 
    AND feature_synonym.synonym_id = synonym.synonym_id
    AND synonym.name = 'Ac12F'
    '''
    results = connect(query, conn)
    assert len(results) == 0

def test_213306_jma_edit_170928_part1():
    # Testing for addition of HRS from field G1b, synonym.
    query = '''
    SELECT * FROM synonym 
	WHERE synonym.type_id = 59978
    AND synonym.name = 'HRS'
    '''
    results = connect(query, conn)
    assert len(results) == 0

def test_213306_jma_edit_170928_part2():
    # Testing for addition of HRS from field G1b, feature_synonym.
    query = '''
    SELECT * FROM feature_synonym, synonym 
	WHERE feature_synonym.feature_id = 3111362 
    AND feature_synonym.is_current = 'f' 
    AND feature_synonym.pub_id = 358057 
    AND feature_synonym.is_internal = 'FALSE' 
    AND feature_synonym.synonym_id = synonym.synonym_id
    AND synonym.name = 'HRS'
    '''
    results = connect(query, conn)
    assert len(results) == 0