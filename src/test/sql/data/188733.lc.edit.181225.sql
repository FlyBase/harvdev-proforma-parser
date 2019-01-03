SET session_replication_role = replica;

INSERT INTO pub(pub_id, title, volumetitle, volume, series_name, issue, pyear, pages, miniref, type_id, is_obsolete, publisher, pubplace, uniquename) VALUES (332469, 'Cyclic nucleotide phosphodiesterases in Drosophila melanogaster.', NULL, '388', NULL, NULL, '2005', '333--342', 'Day, 2005, Biochem. J. 388: 333--342', 57094, False, NULL, NULL, 'FBrf0188733');

INSERT INTO feature(feature_id, dbxref_id, organism_id, name, uniquename, residues, seqlen, md5checksum, type_id, is_analysis, timeaccessioned, timelastmodified, is_obsolete) VALUES (3087057, 64409, 1, 'dnc', 'FBgn0000479', NULL, 167328, NULL, 219, False, '2003-12-01 16:59:57.374746', '2012-05-07 11:18:52.894067', False);

INSERT INTO feature_pub(feature_pub_id, feature_id, pub_id) VALUES (855234, 3087057, 332469);

INSERT INTO cvterm(cvterm_id, cv_id, definition, dbxref_id, is_obsolete, is_relationshiptype, name) VALUES (59978, 5, NULL, 1663308, 0, 0, 'symbol');

INSERT INTO cv(cv_id, name, definition) VALUES (5, 'synonym type', NULL);

INSERT INTO synonym(synonym_id, name, type_id, synonym_sgml) VALUES (1230505, 'CG10797', 59978, 'CG10797');

INSERT INTO feature_synonym(feature_synonym_id, synonym_id, feature_id, pub_id, is_current, is_internal) VALUES (1794857, 1230505, 3087057, 332469, False, False);

SET session_replication_role = DEFAULT;

