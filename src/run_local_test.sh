#! /bin/bash

export POSTGRES_USER=postgres
# in another window if you do not have postgres installed locally
# docker run -p 5432:5432 -e POSTGRES_USER=postgres  postgres
export TEST_ENV="local"

dropdb -h 127.0.0.1 -U postgres testdb
set -e
echo "### Create DB"
createdb -h 127.0.0.1  -U postgres testdb
echo "### Load schema"
psql -h 127.0.0.1 -q -d testdb -U postgres -f test/sql/schema/test_chado_schema.sql

echo "### Load tes sql data"
for f in test/sql/data/*.sql ; do psql -h 127.0.0.1 -q -d testdb -U postgres -f $f ; done
echo "### Test test datan loaded"
pytest test/test_testdb_loaded
echo "### Run app on test proformae"
python3 app.py -v -c ../../credentials/proforma/test.cfg -d test/proformae -l test
echo "### Test changes to postgres db"
pytest test/test_integration/test_integration.py
echo "### End of tests"