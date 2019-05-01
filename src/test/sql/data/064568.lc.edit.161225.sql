SET session_replication_role = replica;

INSERT INTO pub(pub_id, title, volumetitle, volume, series_name, issue, pyear, pages, miniref, type_id, is_obsolete, publisher, pubplace, uniquename) VALUES (221699, 'Gelatin as a blocking agent in Southern blot and chromosomal in situ hybridizations.', NULL, '9', NULL, '8', '1993', '261', 'Lakhotia et al., 1993, Trends Genet. 9(8): 261', 57084, False, NULL, NULL, 'FBrf0064568');

INSERT INTO feature(feature_id) VALUES (3167618);

INSERT INTO feature_pub(feature_pub_id, feature_id, pub_id) VALUES (924017, 3167618, 221699);

INSERT INTO cv(cv_id, name, definition) VALUES (5, 'synonym type', NULL);

INSERT INTO cvterm(cvterm_id, cv_id, definition, dbxref_id, is_obsolete, is_relationshiptype, name) VALUES (59978, 5, NULL, 1663308, 0, 0, 'symbol');

INSERT INTO cv(cv_id, name, definition) VALUES (11, 'pubprop type', 'types of pubprops');

INSERT INTO cvterm(cvterm_id, cv_id, definition, dbxref_id, is_obsolete, is_relationshiptype, name) VALUES (92321, 11, NULL, 2413326, 0, 0, 'curated_by');

INSERT INTO synonym(synonym_id, name, type_id, synonym_sgml) VALUES (1301765, 'hsromega', 59978, 'hsrω');

