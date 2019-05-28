import sys, json, os, configparser, psycopg2, yaml, logging, pytest

log = logging.getLogger(__name__)

###############
# Tests below #
###############

# These tests have assertions which are the *opposite* of those found in `test_integration.py`

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

def test_064568_lc_edit_161225():
    # Testing for addition of hsr&ohgr; from field G1b, feature_synonym.
    query = '''
    SELECT * FROM feature_synonym, synonym 
	WHERE feature_synonym.feature_id = 3167618 
    AND feature_synonym.is_current = 'f' 
    AND feature_synonym.pub_id = 221699 
    AND feature_synonym.is_internal = 'FALSE' 
    AND feature_synonym.synonym_id = synonym.synonym_id
    AND synonym.sgml = 'hsrω'
    '''
    results = connect(query, conn)
    assert len(results) == 0