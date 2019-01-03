#! /bin/bash

export TEST_ENV="local"
set -e

dropdb testdb
createdb testdb
psql -q -d testdb -f src/test/sql/schema/test_chado_schema.sql

for f in src/test/sql/data/*.sql ; do psql -q -d testdb -f $f ; done
pytest src/test/test_testdb_loaded
python3 src/app.py -v -c ../../credentials/proforma/test.cfg -d src/test/proformae -l production
pytest src/test/test_integration/test_integration.py