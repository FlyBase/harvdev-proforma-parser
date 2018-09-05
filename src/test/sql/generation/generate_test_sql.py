import sys, os, subprocess, logging, argparse

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(levelname)s -- %(message)s')
log = logging.getLogger(__name__)

def write_output_file(command):
    retrieve_sql = subprocess.Popen(command, shell=True)
    retrieve_sql.communicate()

def main():
    parser = argparse.ArgumentParser(description='Generate SQL for running integration tests in Travis CI.')
    parser.add_argument('-d', '--database', help='The database used for retrieving SQL.', required=True)
    parser.add_argument('-o', '--output', help='The output directory.', required=True)
    args = parser.parse_args()

    database = args.database
    output_dir = args.output

    dict_of_test_data_to_generate = {
        '213306.jma.edit.sql' : ['SELECT * FROM pub WHERE uniquename = \'FBrf0213306\'']
    }

    for key in dict_of_test_data_to_generate.keys():
        

    output_location = output_dir + '/' + output_file

    command = '''
    psql -d %s -q -c "\\copy (SELECT * FROM pub WHERE uniquename = \'FBrf0213306\') to \'%s\' with csv"''' % (database, output_location)

    print(command)
    write_output_file(command)

if __name__ == '__main__':
    main()