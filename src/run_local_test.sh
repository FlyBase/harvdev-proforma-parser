#! /bin/bash

dropdb testdb
createdb testdb
psql -q -d testdb -f src/test/sql/schema/test_chado_schema.sql

for f in src/test/sql/data/*.sql ; do psql -q -d testdb -f $f ; done
python3 src/app.py -v -c ../../credentials/proforma/config.cfg -d src/test/proformae -l production