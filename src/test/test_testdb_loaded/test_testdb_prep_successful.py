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

try:
    yaml_query_file = open('src/test/sql/queries_for_test_sql.yaml', 'r')
    dict_of_test_data_to_generate = yaml.load(yaml_query_file)
except FileNotFoundError:
    log.critical('Cannot find YAML file \'src/test/sql/queries_for_test_sql.yaml\' ')
    log.critical('Exiting.')
    sys.exit(-1)

combined_list_to_test = []

for entry in dict_of_test_data_to_generate:
    for query_in_list in dict_of_test_data_to_generate[entry]:
        for (key, value) in query_in_list.items():
            combined_list_to_test.append(value)

def connect(sql, conn):
    # Return the cursor and use it to perform queries.
    cursor = conn.cursor()
    # Execute the query.
    cursor.execute(sql) # If we have a variable (e.g. an FBgn) be sure to include it in the execute command.
    # Grab the results.
    records = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    # Close the cursor  
    cursor.close()
    # Return a list of tuples
    return records, colnames

@pytest.mark.parametrize('testdata', combined_list_to_test)
def test_entries(testdata):
    results, colnames = connect(testdata, conn)
    assert len(results) != 0