SET session_replication_role = replica;

INSERT INTO pub(pub_id, title, volumetitle, volume, series_name, issue, pyear, pages, miniref, type_id, is_obsolete, publisher, pubplace, uniquename) VALUES (339330, 'A gain-of-function screen identifying genes required for vein formation in the Drosophila melanogaster wing.', NULL, '174', NULL, '3', '2006', '1635--1659', 'Molnar et al., 2006, Genetics 174(3): 1635--1659', 57094, False, NULL, NULL, 'FBrf0195387');

INSERT INTO synonym(synonym_id, name, type_id, synonym_sgml) VALUES (1172006, 'CG9533', 59978, 'CG9533');

INSERT INTO feature_synonym(feature_synonym_id, synonym_id, feature_id, pub_id, is_current, is_internal) VALUES (1712962, 1172006, 3107733, 152597, False, False);

SET session_replication_role = DEFAULT;

