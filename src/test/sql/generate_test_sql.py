import sys, os, subprocess, logging, argparse, psycopg2, configparser, datetime, yaml, pprint

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(levelname)s -- %(message)s')
log = logging.getLogger(__name__)

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

def prepare_result_print_statement(result_list):
    # This function is to help *appropriately* print out values from the results list of a Chado query.
    # What is appropriate? Basically, check for type and include or exclude single quotes as necessary.
    # I can't find a way to have Python automatically print a mixed list of types in this manner when writing a string.

    print_statement = '('

    for entry in result_list:
        if type(entry) is int or type(entry) is bool:
            print_statement = '{}{}, '.format(print_statement, str(entry))
        elif entry is None:
            print_statement = '{}NULL, '.format(print_statement)
        elif type(entry) is str or type(entry) is datetime.datetime:
            print_statement = '{}\'{}\', '.format(print_statement, entry)  
        else:
            log.critical('Found unexpected type when attempting to write SQL output.')
            log.critical('Please check \'prepare_result_print_statement\' function.')
            log.critical('Entry: {} Type: {}'.format(entry, type(entry)))
    
    print_statement = print_statement[:-2] # Remove the last space and comma.
    print_statement = print_statement + ')'

    return print_statement

def main():
    parser = argparse.ArgumentParser(description='Generate SQL for running integration tests in Travis CI.')
    parser.add_argument('-o', '--output', help='The output directory.', required=True)
    parser.add_argument('-c', '--config', help='Specify the location of the configuration file.', required=True)
    
    args = parser.parse_args()

    # Import secure config variables.
    config = configparser.ConfigParser()
    config.read(args.config)

    USER = config['connection']['USER']
    PASSWORD = config['connection']['PASSWORD']
    SERVER = config['connection']['SERVER']
    DB = config['connection']['DB']

    # Define our connection.
    conn_string = "host=%s dbname=%s user=%s password='%s'" % (SERVER, DB, USER, PASSWORD)
    # Attempt to get a connection
    conn = psycopg2.connect(conn_string)

    output_dir = args.output

    try:
        yaml_query_file = open('queries_for_test_sql.yaml', 'r')
        dict_of_test_data_to_generate = yaml.load(yaml_query_file)
    except FileNotFoundError:
        log.critical('Cannot find YAML file \'queries_for_test_sql.yaml\'')
        log.critical('Please ensure it is in the same directory as this Python script.')
        log.critical('Exiting.')
        sys.exit(-1)

    # Uncomment the command below to print out YAML data structure.
    # log.info(yaml.dump(dict_of_test_data_to_generate))

    # TODO Add support for multiple rows of returns.
    for entry in dict_of_test_data_to_generate:
        with open(output_dir + '/' + entry, 'w') as outfile:
            outfile.write('SET session_replication_role = replica;\n\n')
            for query_in_list in dict_of_test_data_to_generate[entry]:
                for (key, value) in query_in_list.items():
                    table = value
                    results, colnames = connect(key, conn)
                    results_list = [x for x in results[0]]
                    # log.info(results_list)
                    value_statement = prepare_result_print_statement(results_list)

                    final_statement = 'INSERT INTO {}({}) VALUES {};\n\n'.format(table, ', '.join(colnames), value_statement)
                    
                    outfile.write(final_statement)

            outfile.write('SET session_replication_role = DEFAULT;\n\n')

if __name__ == '__main__':
    main()