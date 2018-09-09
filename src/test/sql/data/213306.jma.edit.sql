INSERT INTO cvterm(cvterm_id, cv_id, definition, dbxref_id, is_obsolete, is_relationshiptype, name) VALUES (57094, 1, NULL, 794528, 0, 0, 'paper');

INSERT INTO dbxref(dbxref_id, db_id, accession, version, description, url) VALUES (794519, 4, 'internalnotes', '', NULL, NULL);

INSERT INTO dbxref(dbxref_id, db_id, accession, version, description, url) VALUES (1663308, 4, 'symbol', '', NULL, NULL);

INSERT INTO cvterm(cvterm_id, cv_id, definition, dbxref_id, is_obsolete, is_relationshiptype, name) VALUES (59978, 5, NULL, 1663308, 0, 0, 'symbol');

INSERT INTO pub(pub_id, title, volumetitle, volume, series_name, issue, pyear, pages, miniref, type_id, is_obsolete, publisher, pubplace, uniquename) VALUES (358057, 'Second-order conditioning in Drosophila.', NULL, '18', NULL, '4', '2011', '250--253', 'Tabone and de Belle, 2011, Learn. Mem. 18(4): 250--253', 57094, False, NULL, NULL, 'FBrf0213306');

INSERT INTO cv(cv_id, name, definition) VALUES (11, 'pubprop type', 'types of pubprops');

INSERT INTO cvterm(cvterm_id, cv_id, definition, dbxref_id, is_obsolete, is_relationshiptype, name) VALUES (57047, 11, NULL, 794519, 0, 0, 'internalnotes');

INSERT INTO feature(feature_id, dbxref_id, organism_id, name, uniquename, residues, seqlen, md5checksum, type_id, is_analysis, timeaccessioned, timelastmodified, is_obsolete) VALUES (3111362, 622281, 1, 'HisRS', 'FBgn0027087', NULL, 5018, NULL, 219, False, '2003-12-01 18:14:42.601074', '2016-02-04 10:11:00.737160', False);

INSERT INTO cv(cv_id, name, definition) VALUES (5, 'synonym type', NULL);

INSERT INTO synonym(synonym_id, name, type_id, synonym_sgml) VALUES (1169747, 'HRS', 59978, 'HRS');

