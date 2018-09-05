--
-- PostgreSQL database dump
--

-- Dumped from database version 10.4 (Ubuntu 10.4-0ubuntu0.18.04)
-- Dumped by pg_dump version 10.4 (Ubuntu 10.4-0ubuntu0.18.04)

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: datetime; Type: DOMAIN; Schema: public; Owner: postgres
--

CREATE DOMAIN public.datetime AS timestamp without time zone;


ALTER DOMAIN public.datetime OWNER TO postgres;

--
-- Name: boxquery(integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.boxquery(integer, integer) RETURNS box
    LANGUAGE sql IMMUTABLE
    AS $_$SELECT box (create_point($1, $2), create_point($1, $2))$_$;


ALTER FUNCTION public.boxquery(integer, integer) OWNER TO postgres;

--
-- Name: boxquery(integer, integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.boxquery(integer, integer, integer) RETURNS box
    LANGUAGE sql IMMUTABLE
    AS $_$SELECT box (create_point($1, $2), create_point($1, $3))$_$;


ALTER FUNCTION public.boxquery(integer, integer, integer) OWNER TO postgres;

--
-- Name: boxrange(integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.boxrange(integer, integer) RETURNS box
    LANGUAGE sql IMMUTABLE
    AS $_$SELECT box (create_point(0, $1), create_point($2,500000000))$_$;


ALTER FUNCTION public.boxrange(integer, integer) OWNER TO postgres;

--
-- Name: boxrange(integer, integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.boxrange(integer, integer, integer) RETURNS box
    LANGUAGE sql IMMUTABLE
    AS $_$SELECT box (create_point($1, $2), create_point($1,$3))$_$;


ALTER FUNCTION public.boxrange(integer, integer, integer) OWNER TO postgres;

--
-- Name: chado_args_init(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.chado_args_init() RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
	cvid	INTEGER;
	pubtypeid	INTEGER;
BEGIN
  --insert CVs
  INSERT INTO cv(name) VALUES('sequence topology');
  INSERT INTO cv(name) VALUES('GenBank feature qualifier');
  --INSERT INTO cv(name) VALUES('pub relationship type');
  --INSERT INTO cv(name) VALUES('pubprop type');
  INSERT INTO cv(name) VALUES('GenBank division');

  --insert cvterm's
  --SO terms
  SELECT cv_id INTO cvid FROM cv WHERE name = 'SO';
  INSERT INTO cvterm(cv_id, name) VALUES(cvid, 'mature_peptide');
  INSERT INTO cvterm(cv_id, name) VALUES(cvid, 'signal_peptide');

  --pub type
  SELECT cv_id INTO cvid FROM cv WHERE name = 'pub type';
  INSERT INTO cvterm(cv_id, name) VALUES(cvid, 'null pub');
  --INSERT INTO cvterm(cv_id, name) VALUES(cvid, 'unpublished');
  --INSERT INTO cvterm(cv_id, name) VALUES(cvid, 'paper');
  INSERT INTO cvterm(cv_id, name) VALUES(cvid, 'submitted');
  --INSERT INTO cvterm(cv_id, name) VALUES(cvid, 'other');
  --INSERT INTO cvterm(cv_id, name) VALUES(cvid, 'journal');

  --sequence topology
  SELECT cv_id INTO cvid FROM cv WHERE name = 'sequence topology';
  INSERT INTO cvterm(cv_id, name) VALUES(cvid, 'linear');
  INSERT INTO cvterm(cv_id, name) VALUES(cvid, 'circular');
  
  --GenBank division
  SELECT cv_id INTO cvid FROM cv WHERE name = 'GenBank division';
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'PRI', 'primate sequences');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'ROD', 'rodent sequences');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'MAM', 'other mammalian sequences');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'VRT', 'other vertebrate sequences');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'INV', 'invertebrate sequences');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'PLN', 'plant, fungal, and algal sequences');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'BCT', 'bacterial sequences');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'VRL', 'viral sequences');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'PHG', 'bacteriophage sequences');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'SYN', 'synthetic sequences');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'UNA', 'unannotated sequences');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'EST', 'EST sequences (expressed sequence tags)');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'PAT', 'patent sequences');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'STS', 'STS sequences (sequence tagged sites)');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'GSS', 'GSS sequences (genome survey sequences)');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'HTG', 'HTGS sequences (high throughput genomic sequences)');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'HTC', 'HTC sequences (high throughput cDNA sequences)');

  --property type
  SELECT cv_id INTO cvid FROM cv WHERE name = 'property type';
  INSERT INTO cvterm(cv_id, name) VALUES(cvid, 'keywords');
  INSERT INTO cvterm(cv_id, name) VALUES(cvid, 'organism');
  INSERT INTO cvterm(cv_id, name) VALUES(cvid, 'mol_type');
  INSERT INTO cvterm(cv_id, name) VALUES(cvid, 'dev_stage');
  INSERT INTO cvterm(cv_id, name) VALUES(cvid, 'chromosome');
  INSERT INTO cvterm(cv_id, name) VALUES(cvid, 'map');

  --GenBank feature qualifier
  SELECT cv_id INTO cvid FROM cv WHERE name = 'GenBank feature qualifier';
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'anticodon', 'Location of the anticodon of tRNA and the amino acid for which it codes');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'bound_moiety', 'Moiety bound');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'citation', 'Reference to a citation providing the claim of or evidence for a feature');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'codon', 'Specifies a codon that is different from any found in the reference genetic code');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'codon_start', 'Indicates the first base of the first complete codon in a CDS (as 1 or 2 or 3)');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'cons_splice', 'Identifies intron splice sites that do not conform to the 5''-GT... AG-3'' splice site consensus');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'db_xref', 'A database cross-reference; pointer to related information in another database. A description of all cross-references can be found at: http://www.ncbi.nlm.nih.gov/collab/db_xref.html');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'direction', 'Direction of DNA replication');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'EC_number', 'Enzyme Commission number for the enzyme product of the sequence');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'evidence', 'Value indicating the nature of supporting evidence');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'frequency', 'Frequency of the occurrence of a feature');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'function', 'Function attributed to a sequence');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'gene', 'Symbol of the gene corresponding to a sequence region (usable with all features)');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'label', 'A label used to permanently identify a feature');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'map', 'Map position of the feature in free-format text');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'mod_base', 'Abbreviation for a modified nucleotide base');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'note', 'Any comment or additional information');
INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'number', 'A number indicating the order of genetic elements (e.g., exons or introns) in the 5 to 3 direction');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'organism', 'Name of the organism that is the source of the sequence data in the record. ');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'partial', 'Differentiates between complete regions and partial ones');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'phenotype', 'Phenotype conferred by the feature');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'product', 'Name of a product encoded by a coding region (CDS) feature');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'pseudo', 'Indicates that this feature is a non-functional version of the element named by the feature key');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'rpt_family', 'Type of repeated sequence; Alu or Kpn, for example');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'rpt_type', 'Organization of repeated sequence');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'rpt_unit', 'Identity of repeat unit that constitutes a repeat_region');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'standard_name', 'Accepted standard name for this feature');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'transl_except', 'Translational exception: single codon, the translation of which does not conform to the reference genetic code');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'translation', 'Amino acid translation of a coding region');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'type', 'Name of a strain if different from that in the SOURCE field');
  INSERT INTO cvterm(cv_id, name, definition) VALUES(cvid, 'usedin', 'Indicatesthat feature is used in a compound feature in another entry');
  --feature qualifiers unique to FB
  INSERT INTO cvterm(cv_id, name) VALUES(cvid, 'comment');
  INSERT INTO cvterm(cv_id, name) VALUES(cvid, 'linked_to');
  INSERT INTO cvterm(cv_id, name) VALUES(cvid, 'na_change');
  INSERT INTO cvterm(cv_id, name) VALUES(cvid, 'pr_change');
  INSERT INTO cvterm(cv_id, name) VALUES(cvid, 'reported_na_change');
  INSERT INTO cvterm(cv_id, name) VALUES(cvid, 'reported_pr_change');

  --insert a null pub of type 'null pub'
  SELECT t.cvterm_id into pubtypeid FROM cvterm t, cv  WHERE t.name = 'null pub' and t.cv_id = cv.cv_id and cv.name = 'pub type';
  INSERT INTO pub(uniquename, type_id) VALUES('nullpub', pubtypeid);

  --insert dbs
  --INSERT INTO db(name, contact_id) VALUES('MEDLINE', 1);
  INSERT INTO db(name, contact_id) VALUES('PUBMED', 1);
  RETURN 1;
END;

$$;


ALTER FUNCTION public.chado_args_init() OWNER TO postgres;

--
-- Name: create_point(integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.create_point(integer, integer) RETURNS point
    LANGUAGE sql
    AS $_$SELECT point ($1, $2)$_$;


ALTER FUNCTION public.create_point(integer, integer) OWNER TO postgres;

--
-- Name: cvterm_name_fn_u(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.cvterm_name_fn_u() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  ph_row phenotype%ROWTYPE;
BEGIN
  -- check to see if updated cvterm.name is present in any phenotype.uniquename
  IF NEW.cvterm_id=OLD.cvterm_id and NEW.cv_id=OLD.cv_id and NEW.name<>OLD.name THEN
	FOR ph_row IN SELECT * from phenotype where cvalue_id = NEW.cvterm_id or observable_id = NEW.cvterm_id union select ph.* from phenotype ph, phenotype_cvterm pc where pc.cvterm_id = NEW.cvterm_id and pc.phenotype_id = ph.phenotype_id LOOP
		UPDATE phenotype SET uniquename = regexp_replace(uniquename, OLD.name, New.name) WHERE phenotype_id = ph_row.phenotype_id;
		RAISE NOTICE 'phenotype UNIQUENAME:% UPDATED TO:%', ph_row.uniquename, regexp_replace(ph_row.uniquename, OLD.name, NEW.name);
	END LOOP;
  END IF;
  RETURN NEW;
END;
$$;


ALTER FUNCTION public.cvterm_name_fn_u() OWNER TO postgres;

--
-- Name: cvterm_name_fn_ue(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.cvterm_name_fn_ue() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  ev_row environment%ROWTYPE;
BEGIN
  -- check to see if updated cvterm.name is present in any environment.uniquename only need for FBcv
  IF NEW.cvterm_id=OLD.cvterm_id and NEW.cv_id=OLD.cv_id and NEW.name<>OLD.name and NEW.is_obsolete <> 1 THEN
	FOR ev_row IN select ev.* from environment ev, environment_cvterm ec where ec.cvterm_id = NEW.cvterm_id and ec.environment_id = ev.environment_id LOOP
		UPDATE environment SET uniquename = regexp_replace(uniquename, OLD.name, New.name) WHERE environment_id = ev_row.environment_id;
		RAISE NOTICE 'environment UNIQUENAME:% UPDATED TO:%', ev_row.uniquename, regexp_replace(ev_row.uniquename, OLD.name, NEW.name);
	END LOOP;
  END IF;
  RETURN NEW;
END;
$$;


ALTER FUNCTION public.cvterm_name_fn_ue() OWNER TO postgres;

--
-- Name: cvterm_name_fn_up(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.cvterm_name_fn_up() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  ph_row phenotype%ROWTYPE;
BEGIN
  -- check to see if updated cvterm.name is present in any phenotype.uniquename
  IF NEW.cvterm_id=OLD.cvterm_id and NEW.cv_id=OLD.cv_id and NEW.name<>OLD.name and NEW.is_obsolete <> 1 THEN
	FOR ph_row IN SELECT * from phenotype where cvalue_id = NEW.cvterm_id or observable_id = NEW.cvterm_id 	LOOP
		UPDATE phenotype SET uniquename = regexp_replace(uniquename, OLD.name, New.name) WHERE phenotype_id = ph_row.phenotype_id;
		RAISE NOTICE 'phenotype UNIQUENAME:% UPDATED TO:%', ph_row.uniquename, regexp_replace(ph_row.uniquename, OLD.name, NEW.name);
	END LOOP;
  END IF;
  RETURN NEW;
END;
$$;


ALTER FUNCTION public.cvterm_name_fn_up() OWNER TO postgres;

--
-- Name: expression_assignname_fn_i(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.expression_assignname_fn_i() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  maxid      int;
  maxid_temp int;
  pos        int;
  id         varchar(255);
  maxid_cg   int;
  id_fb      varchar(255);
  message   varchar(255);
  f_row_g expression%ROWTYPE;
  f_type  cvterm.name%TYPE;
  f_type_id cvterm.cvterm_id%TYPE;
  letter_t varchar;
  letter_p varchar;
  d_id    db.db_id%TYPE;
  f_dbxref_id dbxref.dbxref_id%TYPE;
  f_dbxref_id_temp dbxref.dbxref_id%TYPE;
  fd_id library_dbxref.library_dbxref_id%TYPE;
  cg_accession dbxref.accession%TYPE;
  d_accession dbxref.accession%TYPE;
  f_uniquename_temp expression.uniquename%TYPE;
  f_uniquename expression.uniquename%TYPE;
  p_id                 pub.pub_id%TYPE;
  p_type_id            cvterm.cvterm_id%TYPE;
  c_cv_id              cv.cv_id%TYPE;
  f_s_id               feature_synonym.feature_synonym_id%TYPE;
  f_d_id               library_dbxref.library_dbxref_id%TYPE;
  f_type_FBlc   CONSTANT varchar :='cDNA library';
  f_dbname_gadfly CONSTANT varchar :='FlyBase Annotation IDs';
  f_dbname_FB CONSTANT varchar :='FlyBase';
  o_genus  CONSTANT varchar :='Drosophila';
  o_species  CONSTANT varchar:='melanogaster';
  c_name_synonym CONSTANT varchar:='synonym';
  cv_cvname_synonym CONSTANT varchar:='synonym type';
  p_miniref         CONSTANT varchar:='gadfly3';
  p_cvterm_name     CONSTANT varchar:='computer file';
  p_cv_name         CONSTANT varchar:='pub type';
BEGIN
  RAISE NOTICE 'enter exp_i: expression.uniquename:%', NEW.uniquename;
-- here assign new FBex blah
  IF ( NEW.uniquename like 'FBex:temp%') THEN
--      SELECT INTO f_type c.name from library f, cvterm c, organism o where f.type_id=c.cvterm_id and f.uniquename=NEW.uniquename and f.organism_id =NEW.organism_id;
--      IF f_type is NOT NULL THEN
--        RAISE NOTICE 'in library_assignname_fn_i type of this library is:%', f_type;
--      END IF;
     
--      RAISE NOTICE 'in lib_i, library type is:%', f_type;
      SELECT INTO f_row_g * from expression where uniquename=NEW.uniquename;
	 -- and organism_id=NEW.organism_id;
      SELECT INTO maxid max(to_number(substring(uniquename from 5 for 11), '9999999'))+1 from expression where uniquename like 'FBex_______';
      IF maxid IS NULL THEN
          maxid:=1;
      END IF;
               RAISE NOTICE 'maxid after is:%', maxid;
               id:=lpad(CAST(maxid as TEXT), 7, '0000000');
               f_uniquename:=CAST('FBex'||id as TEXT);

--               SELECT INTO d_id db_id from db where name= f_dbname_FB;
--               IF d_id IS NULL THEN 
--                 INSERT INTO db(name) values (f_dbname_FB);
--                 SELECT INTO d_id db_id from db where name= f_dbname_FB;
--               END IF;
--               RAISE NOTICE 'db_id:%, uniquename:%, f_dbname_FB:%:', d_id, f_uniquename, f_dbname_FB; 
--               SELECT INTO f_dbxref_id dbxref_id from dbxref where db_id=d_id and accession=f_uniquename;
--               IF f_dbxref_id IS NULL THEN 
--                 INSERT INTO dbxref (db_id, accession) values(d_id, f_uniquename);
--                 SELECT INTO f_dbxref_id dbxref_id from dbxref where db_id=d_id and accession=f_uniquename;
--               END IF;
--               RAISE NOTICE 'dbxref_id:%', f_dbxref_id;
               RAISE NOTICE 'old uniquename of this feature is:%', f_row_g.uniquename;
               RAISE NOTICE 'new uniquename of this feature is:%', f_uniquename;
               UPDATE expression set uniquename=f_uniquename where expression_id=f_row_g.expression_id;
--               select INTO fd_id library_dbxref_id from library_dbxref where library_id=f_row_g.library_id and dbxref_id=f_dbxref_id;
--               IF fd_id IS NULL THEN
--                  insert into library_dbxref(is_current, library_id, dbxref_id) values ('true',f_row_g.library_id,f_dbxref_id);
              
--               END IF;
  END IF;
  RAISE NOTICE 'leave exp_i .......';
  return NEW;    
END;
$$;


ALTER FUNCTION public.expression_assignname_fn_i() OWNER TO postgres;

--
-- Name: feature_assignname_fn_i(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.feature_assignname_fn_i() RETURNS trigger
    LANGUAGE plpgsql
    AS $_$
DECLARE
  maxid      int;
  maxid_cg   int;
  id         varchar(255);
  id_fb      varchar(255);
  f_row_g feature%ROWTYPE;
  f_type  cvterm.name%TYPE;
  f_type_gene CONSTANT varchar :='gene';
  letter_t varchar;
  cg_accession dbxref.accession%TYPE;
  d_id    db.db_id%TYPE;
  f_dbxref_id feature.dbxref_id%TYPE;
  fd_id feature_dbxref.feature_dbxref_id%TYPE;
  f_uniquename feature.uniquename%TYPE;
  f_dbname_FB CONSTANT varchar :='FlyBase';
  f_dbname_gadfly CONSTANT varchar :='FlyBase Annotation IDs';
BEGIN
  RAISE NOTICE 'enter f_i: feature.uniquename:%, feature.type_id:%', NEW.uniquename, NEW.type_id;
-- here assign new FBal, FBti, FBtp, FBte, FBmc, FBms, FBba, FBab, FBgn, FBtr, FBpp
  IF ( NEW.uniquename like 'FB%:temp%') THEN
    letter_t := substring(NEW.uniquename from 3 for 2);
    SELECT INTO f_type c.name from feature f, cvterm c, organism o where f.type_id=c.cvterm_id and f.uniquename=NEW.uniquename and f.organism_id =NEW.organism_id;
    IF f_type is NOT NULL THEN
        RAISE NOTICE 'in feature_assignname_fn_i type of this feature is:%', f_type;
    END IF;
    IF (letter_t ='gn' AND f_type!='gene') THEN
    
    ELSE  
      RAISE NOTICE 'in f_i, feature type is:%', f_type;
      SELECT INTO f_row_g * from feature where uniquename=NEW.uniquename and organism_id=NEW.organism_id;
      IF (letter_t = 'sf' or letter_t = 'og') THEN
       SELECT INTO maxid max(to_number(substring(accession from 5 for
		 10), '9999999999'))+1 from dbxref dx, db d where
		 dx.db_id=d.db_id and  d.name=f_dbname_FB and accession like
		 'FB'|| letter_t ||'__________';
	   IF maxid IS NULL THEN
         maxid:=1;
       END IF;
       RAISE NOTICE 'maxid after is:%', maxid;
       id:=lpad(CAST(maxid as TEXT), 10, '0000000000');

      ELSE
        SELECT INTO maxid max(to_number(substring(accession from 5 for 7), '9999999'))+1 from dbxref dx, db d  where dx.db_id=d.db_id and  d.name=f_dbname_FB and accession like 'FB'|| letter_t || '_______';
        IF maxid IS NULL THEN
            maxid:=1;
        END IF;
        RAISE NOTICE 'maxid after is:%', maxid;
        id:=lpad(CAST(maxid as TEXT), 7, '0000000');
      END IF;
    
      f_uniquename:=CAST('FB'|| letter_t||id as TEXT);

      SELECT INTO d_id db_id from db where name= f_dbname_FB;
      IF d_id IS NULL THEN 
        INSERT INTO db(name) values (f_dbname_FB);
        SELECT INTO d_id db_id from db where name= f_dbname_FB;
      END IF;
      RAISE NOTICE 'db_id:%, uniquename:%, f_dbname_FB:%:', d_id, f_uniquename, f_dbname_FB; 
      SELECT INTO f_dbxref_id dbxref_id from dbxref where db_id=d_id and accession=f_uniquename;
      IF f_dbxref_id IS NULL THEN 
        INSERT INTO dbxref (db_id, accession) values(d_id, f_uniquename);
        SELECT INTO f_dbxref_id dbxref_id from dbxref where db_id=d_id and accession=f_uniquename;
      END IF;
      RAISE NOTICE 'dbxref_id:%', f_dbxref_id;
      RAISE NOTICE 'old uniquename of this feature is:%', f_row_g.uniquename;
      RAISE NOTICE 'new uniquename of this feature is:%', f_uniquename;
      UPDATE feature set uniquename=f_uniquename, dbxref_id=f_dbxref_id where feature_id=f_row_g.feature_id;
      SELECT INTO fd_id feature_dbxref_id from feature_dbxref where feature_id=f_row_g.feature_id and dbxref_id=f_dbxref_id;
      IF fd_id IS NULL THEN
        insert into feature_dbxref(is_current, feature_id, dbxref_id) values ('true',f_row_g.feature_id,f_dbxref_id);
      END IF;

-- here for FBgn:temp we assume all will be CG, for tr_fr_i, if add any non-mRNA transcript, then update to CR.
/*
      IF (f_type=f_type_gene AND letter_t ='gn') THEN
              SELECT INTO maxid_cg max(to_number(substring(accession from 3 for 7), '99999'))+1 from dbxref dx, db d  where dx.db_id=d.db_id and  d.name=f_dbname_gadfly and accession like 'C______' and accession ~'^C[G|R][0-9]+$'  and accession not like '%:%' and accession not like '%-%';
              id_fb:=lpad(CAST(maxid_cg AS TEXT), 5, '0000000');
              cg_accession:=CAST('CG'||id_fb AS TEXT);
              RAISE NOTICE 'cg_accession is:%', cg_accession;
              SELECT INTO d_id db_id from db where name=f_dbname_gadfly;
              SELECT INTO f_dbxref_id dbxref_id from dbxref dx, db d where dx.db_id=d.db_id and d.name=f_dbname_gadfly and accession=cg_accession;
              IF f_dbxref_id IS NULL THEN
                INSERT INTO dbxref(db_id, accession) values(d_id, cg_accession);
                SELECT INTO f_dbxref_id dbxref_id from dbxref dx, db d where dx.db_id=d.db_id and d.name=f_dbname_gadfly and accession=cg_accession;
              END IF;
              INSERT INTO feature_dbxref(feature_id, dbxref_id, is_current) values(f_row_g.feature_id, f_dbxref_id, 'true');   
              RAISE NOTICE 'new gene:% : %', f_uniquename, cg_accession;
      END IF;
*/
  END IF;
END IF;
  RAISE NOTICE 'leave f_i .......';
  return NEW;    
END;
$_$;


ALTER FUNCTION public.feature_assignname_fn_i() OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: feature; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feature (
    feature_id integer NOT NULL,
    dbxref_id integer,
    organism_id integer NOT NULL,
    name character varying(255),
    uniquename text NOT NULL,
    residues text,
    seqlen integer,
    md5checksum character(32),
    type_id integer NOT NULL,
    is_analysis boolean DEFAULT false NOT NULL,
    timeaccessioned timestamp without time zone DEFAULT ('now'::text)::timestamp(6) with time zone NOT NULL,
    timelastmodified timestamp without time zone DEFAULT ('now'::text)::timestamp(6) with time zone NOT NULL,
    is_obsolete boolean DEFAULT false NOT NULL
);


ALTER TABLE public.feature OWNER TO postgres;

--
-- Name: feature_disjoint_from(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.feature_disjoint_from(integer) RETURNS SETOF public.feature
    LANGUAGE sql
    AS $_$SELECT feature.*
  FROM feature
   INNER JOIN featureloc AS x ON (x.feature_id=feature.feature_id)
   INNER JOIN featureloc AS y ON (y.feature_id = $1)
  WHERE
   x.srcfeature_id = y.srcfeature_id            AND
   ( x.fmax < y.fmin OR x.fmin > y.fmax ) $_$;


ALTER FUNCTION public.feature_disjoint_from(integer) OWNER TO postgres;

--
-- Name: feature_overlaps(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.feature_overlaps(integer) RETURNS SETOF public.feature
    LANGUAGE sql
    AS $_$SELECT feature.*
  FROM feature
   INNER JOIN featureloc AS x ON (x.feature_id=feature.feature_id)
   INNER JOIN featureloc AS y ON (y.feature_id = $1)
  WHERE
   x.srcfeature_id = y.srcfeature_id            AND
   ( x.fmax >= y.fmin AND x.fmin <= y.fmax ) $_$;


ALTER FUNCTION public.feature_overlaps(integer) OWNER TO postgres;

--
-- Name: feature_propagatename_fn_u(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.feature_propagatename_fn_u() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
maxid int;
id    varchar(255);
maxid_fb int;
len     int;
pos     int;
no      int;
id_fb    varchar(255);
message   varchar(255);
exon_id int;
f_row   feature%ROWTYPE;
f_row_g feature%ROWTYPE;
f_row_e feature%ROWTYPE;
f_row_t feature%ROWTYPE;
f_row_p feature%ROWTYPE;
fr_row  feature_relationship%ROWTYPE;
f_type  cvterm.name%TYPE;
f_type_temp  cvterm.name%TYPE;
letter_t varchar;
letter_p varchar;
letter_e varchar;
f_accession_temp varchar(255);
f_accession varchar(255);
uniquename_exon_like varchar;
f_dbxref_id feature.dbxref_id%TYPE;
fb_accession dbxref.accession%TYPE;
d_accession dbxref.accession%TYPE;
f_name_temp feature.uniquename%TYPE;
f_name_gene feature.uniquename%TYPE;
f_name_tr feature.uniquename%TYPE;
f_name_exon feature.uniquename%TYPE;
f_name_protein feature.uniquename%TYPE;
f_uniquename feature.uniquename%TYPE;
f_uniquename_gene feature.uniquename%TYPE;
f_uniquename_tr feature.uniquename%TYPE;
f_uniquename_exon feature.uniquename%TYPE;
f_uniquename_protein feature.uniquename%TYPE;
f_CG_gene dbxref.accession%TYPE;
f_CG_protein dbxref.accession%TYPE;
f_feature_id_exon feature.feature_id%TYPE;
f_feature_id_protein feature.feature_id%TYPE;
d_id                 db.db_id%TYPE;
dx_id                dbxref.dbxref_id%TYPE;
dx_id_temp           dbxref.dbxref_id%TYPE;
d_id_temp            dbxref.dbxref_id%TYPE; 
s_type_id            synonym.type_id%TYPE;
s_id                 synonym.synonym_id%TYPE;
p_id                 pub.pub_id%TYPE;
  p_type_id            cvterm.cvterm_id%TYPE;
  c_cv_id              cv.cv_id%TYPE;
  f_type_gene CONSTANT varchar :='gene';
  f_type_exon CONSTANT varchar :='exon';
  f_type_transcript CONSTANT varchar :='mRNA';
  f_type_snoRNA CONSTANT varchar :='snoRNA';
  f_type_ncRNA CONSTANT varchar :='ncRNA';
  f_type_snRNA CONSTANT varchar :='snRNA';
  f_type_tRNA CONSTANT varchar :='tRNA';
  f_type_rRNA CONSTANT varchar :='rRNA';
  f_type_miRNA CONSTANT varchar :='miRNA';
  f_type_miscRNA CONSTANT varchar :='misc. non-coding RNA';
  f_type_pseudo CONSTANT varchar :='pseudogene';
  f_type_protein CONSTANT varchar :='protein';
  f_type_allele CONSTANT varchar :='allele';
  f_dbname_gadfly CONSTANT varchar :='FlyBase Annotation IDs';
  f_dbname_FB CONSTANT varchar :='FlyBase';
  o_genus  CONSTANT varchar :='Drosophila';
  o_species  CONSTANT varchar:='melanogaster';
  c_name_synonym CONSTANT varchar:='synonym';
  cv_cvname_synonym CONSTANT varchar:='synonym type';
  p_miniref         CONSTANT varchar:='gadfly3';
  p_cvterm_name     CONSTANT varchar:='computer file';
  p_cv_name         CONSTANT varchar:='pub type';
  f_time            timestamp;
BEGIN
  RAISE NOTICE 'enter f_u, OLD uniquename:%, NEW uniquename:%', OLD.uniquename, NEW.uniquename;
  -- here change the timelastmodified whenever something change to feature table, how about featureprop, featureloc ...
  -- also postgre has very weird behavior whenever set spmething to null or change null to something, so ignore here...
  IF NEW.uniquename<>OLD.uniquename OR NEW.dbxref_id<>OLD.dbxref_id OR NEW.organism_id<>OLD.organism_id OR NEW.name<>OLD.name  OR NEW.uniquename<>OLD.uniquename OR NEW.residues<>OLD.residues OR NEW.seqlen<>OLD.seqlen OR NEW.md5checksum<>OLD.md5checksum  OR NEW.type_id<>OLD.type_id OR NEW.is_analysis<>OLD.is_analysis OR NEW.is_obsolete <>OLD.is_obsolete THEN
    SELECT INTO f_time current_timestamp;
    RAISE NOTICE 'set timelastmodified to:% for feature:%', f_time, OLD.uniquename;
    update feature set timelastmodified=current_timestamp where feature_id=OLD.feature_id;
  END IF;
-- here to synchronize transcript name, for CG/CR, done in tr_dbxref_u.sql
  IF NEW.uniquename <>OLD.uniquename and OLD.is_analysis='false' THEN
      SELECT INTO f_type c.name from feature f, cvterm c, organism o where f.type_id=c.cvterm_id and f.uniquename=NEW.uniquename and f.organism_id =NEW.organism_id;
      IF f_type is NOT NULL THEN
        RAISE NOTICE 'in f_u, type of this feature is:%', f_type;
      END IF;
      IF f_type=f_type_gene THEN
        RAISE NOTICE 'in f_u, synchronize the transcript name with genes';
        FOR fr_row IN SELECT * from feature_relationship fr, feature f, featureloc fl where fr.subject_id=f.feature_id and fl.feature_id=f.feature_id and object_id=OLD.feature_id LOOP
           SELECT INTO f_type_temp c.name from feature f, cvterm c where f.type_id=c.cvterm_id and f.feature_id=fr_row.subject_id;
           IF (f_type_temp =f_type_transcript or f_type_temp =f_type_ncRNA or f_type_temp =f_type_snoRNA or f_type_temp =f_type_snRNA or f_type_temp =f_type_tRNA  or f_type_temp =f_type_rRNA or f_type_temp =f_type_pseudo or f_type_temp =f_type_miRNA or f_type_temp=f_type_miscRNA) THEN
              SELECT INTO f_name_temp name from feature where feature_id=fr_row.subject_id; 
              len:=length (f_name_temp);                        
              letter_t:=substring(f_name_temp from len );             
              f_name_tr:=CAST(NEW.name||'-R'||letter_t  AS TEXT);
              RAISE NOTICE 'f_name_tr:%', f_name_tr;
              IF f_name_tr IS NOT NULL THEN
                 UPDATE feature set name=f_name_tr where feature_id=fr_row.subject_id;
              END IF;
           ELSE
              RAISE NOTICE 'Not typical gene->transcript relationship: obj:%, subj:%', NEW.uniquename, fr_row.subject_id;
              message:=CAST('wrong relationship:gene->no_RNA'||'object:'||fr_row.object_id||'subject:'||fr_row.subject_id AS TEXT);
 
           END IF;
        END LOOP;
-- for Apollo ChadoXML, insert order: gene, tr, protein,  protein, f_r_of_tr/protein,f_r of gene/tr, we assign FBpp here, 
-- here we try catch the case of insert order: tr, protein, f_r_of_tr/protein, f_r_of_gene/tr
-- for case: gene, tr, fr_g/t, tr,protein, fr_tr/p, we deal in tr_fr_i.sql
      ELSIF (f_type =f_type_transcript or f_type =f_type_ncRNA or f_type =f_type_snoRNA or f_type =f_type_snRNA or f_type =f_type_tRNA or f_type =f_type_rRNA  or f_type =f_type_pseudo or f_type =f_type_miRNA or f_type=f_type_miscRNA) THEN
        select INTO f_uniquename f.uniquename from feature f, feature_relationship fr where f.feature_id=fr.object_id and fr.subject_id=OLD.feature_id;
        IF f_uniquename IS NOT NULL THEN
          FOR fr_row IN SELECT * from feature_relationship where object_id=OLD.feature_id LOOP
             select INTO f_type_temp c.name from cvterm c, feature f where c.cvterm_id=f.type_id and f.feature_id=fr_row.subject_id;
             IF f_type_temp =f_type_protein THEN
                SELECT INTO f_row * from feature where feature_id=fr_row.subject_id;
                RAISE NOTICE 'f_row.uniquename:%', f_row.uniquename;
                IF f_row.uniquename like 'FBgn:temp%'  THEN
                   select INTO f_CG_gene accession from feature f, feature_relationship fr,feature_dbxref fd, dbxref d, db d1, cvterm c where c.cvterm_id=f.type_id and c.name=f_type_gene  and f.feature_id=fr.object_id and fr.subject_id=OLD.feature_id and f.feature_id=fd.feature_id and fd.dbxref_id=d.dbxref_id and fd.is_current='true' and d.db_id=d1.db_id and d1.name=f_dbname_gadfly ;
                   select INTO f_name_gene f.name from feature f, feature_relationship fr, cvterm c where f.type_id=c.cvterm_id and c.name=f_type_gene and f.feature_id=fr.object_id and fr.subject_id=OLD.feature_id;
                IF f_CG_gene IS NOT NULL THEN  
                   len:=length(f_row.uniquename);
                   RAISE NOTICE 'len:% for uniquename:%', len, f_row.uniquename;
                   letter_p:=substring(f_row.uniquename from len for 1); 

                   f_CG_protein:=CAST(f_CG_gene||'-P'||letter_p  AS TEXT);
                   f_name_protein:=CAST(f_name_gene||'-P'||letter_p  AS TEXT);
                   RAISE NOTICE 'letter_p:%, CG for protein:%', letter_p, f_CG_protein;
                   SELECT INTO d_id db_id from db where name=f_dbname_gadfly;                   
                   SELECT INTO dx_id dbxref_id from dbxref where db_id=d_id and accession=f_CG_protein;
                   IF dx_id IS NULL THEN                    
                      INSERT INTO dbxref(db_id, accession) values(d_id, f_CG_protein);
                      SELECT INTO dx_id dbxref_id from dbxref where db_id=d_id and accession=f_CG_protein;
                   END IF;
                   SELECT INTO d_id_temp dbxref_id from feature_dbxref where feature_id=fr_row.subject_id and dbxref_id=dx_id;
                   IF d_id_temp IS NULL THEN 
                      INSERT INTO feature_dbxref (feature_id, dbxref_id, is_current)  values(fr_row.subject_id, dx_id, 'true');
                   END IF;
                 END IF;

                   SELECT INTO maxid_fb max(to_number(substring(accession from 5 for 11),'9999999')) from dbxref dx, db d where dx.db_id=d.db_id and d.name = f_dbname_FB and accession like 'FBpp%';  
                   IF maxid_fb IS NULL OR maxid_fb< 70000  THEN
                      maxid_fb:=70000;
                   ELSE 
                    maxid_fb:=maxid_fb+1;
                   END IF;
                   id_fb:=lpad(CAST(maxid_fb AS TEXT), 7, '0000000');
                   fb_accession:=CAST('FBpp'||id_fb AS TEXT);
                   RAISE NOTICE 'fb_accession is:%', fb_accession;
                   SELECT INTO d_id db_id from db where name=f_dbname_FB;
                   INSERT INTO dbxref(db_id, accession) values(d_id, fb_accession);
                   SELECT INTO dx_id dbxref_id from dbxref dx , db d where dx.db_id=d.db_id and d.name=f_dbname_FB and accession=fb_accession;
                   INSERT INTO feature_dbxref(feature_id, dbxref_id, is_current) values(fr_row.subject_id, dx_id,'true');
                   RAISE NOTICE 'insert FBpp:% into feature_dbxref, and set is_current as true', fb_accession;

/* here we DO NOT add f_s for protein, either done in tr_fr_i or from cambridge
                   SELECT INTO s_type_id cvterm_id from cvterm c1, cv c2 where c1.name=c_name_synonym and c2.name=cv_cvname_synonym and c1.cv_id=c2.cv_id;
                   RAISE NOTICE 's_type_id:%', s_type_id;
                   SELECT INTO s_id synonym_id from synonym where name=f_uniquename_protein and type_id=s_type_id;
                   IF s_id IS NULL THEN 
                      INSERT INTO synonym(name, synonym_sgml, type_id) values(f_uniquename_protein, f_uniquename_protein, s_type_id);
                      SELECT INTO s_id synonym_id from synonym where name=f_uniquename_protein and type_id=s_type_id;
                   END IF;
                   SELECT INTO p_id pub_id from pub p, cvterm c where uniquename=p_miniref and c.name=p_cvterm_name and c.cvterm_id=p.type_id;
                      IF p_id IS NULL THEN
                         SELECT INTO p_type_id cvterm_id from cvterm where name=p_cvterm_name;
                         IF p_type_id IS NULL THEN
                             SELECT INTO c_cv_id cv_id from cv where name=p_cv_name;
                             IF c_cv_id IS NULL THEN
                                INSERT INTO cv(name) values(p_cv_name);
                                SELECT INTO c_cv_id cv_id from cv where name=p_cv_name;
                             END IF;
                             INSERT INTO cvterm(name, cv_id) values(p_cvterm_name, c_cv_id);
                             SELECT INTO c_cv_id cv_id from cv where name=p_cv_name;
                         END IF;
                         INSERT INTO pub(uniquename, miniref, type_id) values(p_miniref, p_miniref, p_type_id);
                         SELECT INTO p_id pub_id from pub p, cvterm c where uniquename=p_miniref and c.name=p_cvterm_name and c.cvterm_id=p.type_id;
                   END IF;
                   RAISE NOTICe 'start to insert feature_synonym:synonym_id:%,feature_id:%', s_id, fr_row.subject_id;
                   INSERT INTO feature_synonym(feature_id, synonym_id, pub_id, is_current) values (fr_row.subject_id, s_id, p_id, 'true');
*/
                END IF;
                IF (f_row.name like '%temp%' and f_name_gene IS NOT NULL and f_row.uniquename like '%temp%')  THEN         
                    UPDATE feature set uniquename=fb_accession, name=f_name_protein,  dbxref_id=dx_id where feature_id=fr_row.subject_id;
                ELSIF  f_row.uniquename like 'FBgn:temp%' THEN
                   UPDATE feature set uniquename=fb_accession, dbxref_id=dx_id where feature_id=fr_row.subject_id;
                END IF;
             ELSIF f_type_temp =f_type_exon THEN
                RAISE NOTICE 'in f_u, update exon:%', fr_row.subject_id;
                SELECT INTO f_row_e * from feature where feature_id=fr_row.subject_id;
                IF f_row_e.uniquename like 'FBgn:temp%' THEN
                   select INTO f_uniquename_gene f.uniquename from feature f, feature_relationship fr, cvterm c where f.type_id=c.cvterm_id and c.name=f_type_gene and f.feature_id=fr.object_id and fr.subject_id=OLD.feature_id;
                   select INTO f_name_gene f.name from feature f, feature_relationship fr, cvterm c where f.type_id=c.cvterm_id and c.name=f_type_gene and f.feature_id=fr.object_id and fr.subject_id=OLD.feature_id;
-- in case of: FBgn:temp1:2L_4639000_4649000:21, how to find the suffix here:21
                  f_accession_temp:=f_row_e.uniquename;
                  len:=length(f_accession_temp)-1;
                  letter_e:=substring(f_accession_temp from len for 2);    
                  letter_e:=replace(letter_e, ':','');
                  f_uniquename_exon:=CAST(f_uniquename_gene||':'||letter_e  AS TEXT);
                  f_name_exon:=CAST(f_name_gene||':'||letter_e AS TEXT);
/* here is trick: assume two transcripts share one exon, previous loading already update exon.uniquename to this new uniquename,
   we need to delete the exist exon with this update and link to this new one. why NOT re-direct this new one to the existing one ?
*/
                   RAISE NOTICE 'in f_u, new uniquename for exon:%, old unqiuename:%', f_uniquename_exon, f_row_e.uniquename;
                   SELECT INTO f_feature_id_exon feature_id from feature where uniquename=f_uniquename_exon;
                   IF f_feature_id_exon IS NOT NULL THEN 
                      RAISE NOTICE 'this exon:% share with other transcript, re_direct to exist exon and delete this one', f_row_e.uniquename;
                      RAISE NOTICE 'UPDATE feature_relationship set subject_id=% where feature_relationship_id=%',f_feature_id_exon,fr_row.feature_relationship_id;
                      UPDATE feature_relationship set subject_id=f_feature_id_exon where feature_relationship_id=fr_row.feature_relationship_id;
                      delete from feature_dbxref where feature_id=f_row_e.feature_id;
                      delete from feature_synonym where  feature_id=f_row_e.feature_id;
                      delete from featureprop where feature_id=f_row_e.feature_id;
                      DELETE from featureloc where feature_id=f_row_e.feature_id;
                      DELETE from feature where feature_id=f_row_e.feature_id;
                      RAISE NOTICE 'finish re_direct feature_relationship:%',fr_row.feature_relationship_id;
                   ELSE 
                     IF (f_row_e.name like '%temp%'  and f_row_e.uniquename like '%temp%') THEN         
                        RAISE NOTICE 'in f_u, update both uniquename and name for exon:%', f_row_e.uniquename;  
                        UPDATE feature set uniquename=f_uniquename_exon, name=f_name_exon where feature_id=fr_row.subject_id;
                     ELSIF f_row_e.uniquename like '%temp%' THEN
                        RAISE NOTICE 'in f_u, update exon uniuqnename:% to %', f_row_e.uniquename, f_uniquename_exon;   
                        UPDATE feature set uniquename=f_uniquename_exon where feature_id=fr_row.subject_id;
                     END IF;
                   END IF;

                END IF;

             ELSE
                RAISE NOTICE 'wrong relationship: transcript->no_exon/protein, obj:%, subj:%', fr_row.object_id, fr_row.subject_id;
             END IF;
          END LOOP;
        END IF;
      END IF;
  END IF; 
 RAISE NOTICE 'leave f_u ....';
  RETURN OLD;
END;
$$;


ALTER FUNCTION public.feature_propagatename_fn_u() OWNER TO postgres;

--
-- Name: feature_relationship_fn_d(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.feature_relationship_fn_d() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  maxid int;
  exon_id int;
  id    varchar(255);
  maxid_fb int;
  id_fb    varchar(255);
  loginfo      varchar(255);
  len   int;
  f_row_g feature%ROWTYPE;
  f_row_e feature%ROWTYPE;
  f_row_t feature%ROWTYPE;
  f_row_p feature%ROWTYPE;
  f_type  cvterm.name%TYPE;
  f_type_temp  cvterm.name%TYPE;
  letter_e varchar(10);
  letter_t varchar(10);
  letter_p varchar(10);
  f_dbxref_id feature.dbxref_id%TYPE;
  fb_accession dbxref.accession%TYPE;
  d_accession dbxref.accession%TYPE;
  f_uniquename_gene feature.uniquename%TYPE;
  f_uniquename_transcript feature.uniquename%TYPE;
  f_uniquename_exon feature.uniquename%TYPE;
  f_uniquename_protein feature.uniquename%TYPE;
  f_d_id               feature_dbxref.feature_dbxref_id%TYPE;
  d_id                 dbxref.dbxref_id%TYPE;
  s_type_id            synonym.type_id%TYPE;
  s_id                 synonym.synonym_id%TYPE;
  p_id                 pub.pub_id%TYPE;
  fr_row feature_relationship%ROWTYPE;
  f_accession_temp varchar(255);
  f_accession varchar(255);
  f_type_gene CONSTANT varchar :='gene';
  f_type_exon CONSTANT varchar :='exon';
  f_type_transcript CONSTANT varchar :='mRNA';
  f_type_snoRNA CONSTANT varchar :='snoRNA';
  f_type_ncRNA CONSTANT varchar :='ncRNA';
  f_type_snRNA CONSTANT varchar :='snRNA';
  f_type_tRNA CONSTANT varchar :='tRNA';
  f_type_rRNA CONSTANT varchar :='rRNA';
  f_type_miRNA CONSTANT varchar :='miRNA';
  f_type_miscRNA CONSTANT varchar :='misc. non-coding RNA';
  f_type_pseudo CONSTANT varchar :='pseudogene';
  f_type_protein CONSTANT varchar :='protein';
  f_type_allele CONSTANT varchar :='alleleof';
 f_dbname_gadfly CONSTANT varchar :='Gadfly';
 f_dbname_FB CONSTANT varchar :='FlyBase';
  c_name_synonym CONSTANT varchar:='synonym';
  cv_cvname_synonym CONSTANT varchar:='synonym type';
  p_miniref         CONSTANT varchar:='GadFly';
BEGIN
 RAISE NOTICE 'enter fr_d, fr.object_id:%, fr.subject_id:%', OLD.object_id, OLD.subject_id;
 SELECT INTO f_type name from cvterm  where cvterm_id=OLD.type_id;
 IF f_type=f_type_allele THEN
    RAISE NOTICE 'delete relationship beteen gene:% and allele:%', OLD.object_id, OLD.subject_id; 
 ELSE
   SELECT INTO f_type c.name from feature f, cvterm c  where f.type_id=c.cvterm_id and f.feature_id=OLD.object_id;
   IF f_type=f_type_gene THEN 
      SELECT INTO f_type_temp c.name from feature f, cvterm c where f.feature_id=OLD.subject_id and f.type_id=c.cvterm_id;
      IF (f_type_temp=f_type_transcript or f_type_temp=f_type_ncRNA or f_type_temp=f_type_snoRNA  or f_type_temp=f_type_snRNA  or f_type_temp=f_type_tRNA  or f_type_temp=f_type_rRNA  or f_type_temp=f_type_miRNA  or f_type_temp=f_type_pseudo  or f_type_temp=f_type_miscRNA ) THEN
          SELECT INTO fr_row * from feature_relationship where object_id<>OLD.object_id and subject_id=OLD.subject_id;
             if fr_row.object_id IS NULL THEN
                RAISE NOTICE 'delete this lonely transcript:%', OLD.subject_id;
                -- we should NOT delete it, instead we obsolete it, further, we should use ChadoUtil.deleteGeneModel
                -- delete from feature where feature_id=OLD.subject_id;
             END IF;
      ELSE
           RAISE NOTICE 'wrong feature_relationship: gene->NO_transcript:object_id:%, subject_id:%', OLD.object_id, OLD.subject_id;
      END IF;
   ELSIF (f_type=f_type_transcript or f_type=f_type_snoRNA or f_type=f_type_ncRNA or f_type=f_type_snRNA or f_type=f_type_tRNA or f_type=f_type_miRNA or f_type=f_type_rRNA or f_type=f_type_pseudo  or f_type=f_type_miscRNA ) THEN
      SELECT INTO f_type_temp c.name from feature f, cvterm c where f.feature_id=OLD.subject_id and f.type_id=c.cvterm_id;
      IF  f_type_temp=f_type_exon THEN
          SELECT INTO fr_row * from feature_relationship where subject_id=OLD.subject_id and object_id<>OLD.object_id;  
          IF fr_row.object_id IS NULL     THEN     
            RAISE NOTICE 'delete this lonely exon:%', OLD.subject_id;
            delete from feature where feature_id=OLD.subject_id;          
          END IF;
      ELSIF f_type_temp=f_type_protein THEN
          SELECT INTO fr_row * from feature_relationship where subject_id=OLD.subject_id and object_id<>OLD.object_id;  
          IF fr_row.object_id IS NULL     THEN     
            RAISE NOTICE 'obsolete this lonely protein:%', OLD.subject_id;
            update feature set is_obsolete='true' where feature_id=OLD.subject_id;  
            delete from featureloc where feature_id= OLD.subject_id;       
          END IF;
      ELSE
          RAISE NOTICE 'wrong relationship: transcript->NO_protein/exon: objfeature:%, subjfeature:%',OLD.object_id, OLD.subject_id;
      END IF;
   END IF;
 END IF;
 RAISE NOTICE 'leave fr_d ....';
 RETURN OLD;
END;
$$;


ALTER FUNCTION public.feature_relationship_fn_d() OWNER TO postgres;

--
-- Name: feature_relationship_propagatename_fn_i(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.feature_relationship_propagatename_fn_i() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  maxid int;
  exon_id int;
  id    varchar(255);
  maxid_fb int;
  id_fb    varchar(255);
  loginfo      varchar(255);
  len   int;
  f_CG_gene_digit int;
  f_row_g feature%ROWTYPE;
  f_row_e feature%ROWTYPE;
  f_row_t feature%ROWTYPE;
  f_row_p feature%ROWTYPE;
  dx_row  dbxref%ROWTYPE;
  f_type  cvterm.name%TYPE;
  f_type_temp  cvterm.name%TYPE;
  letter_e varchar(10);
  letter_t varchar(10);
  letter_p varchar(10);
  f_dbxref_id          feature.dbxref_id%TYPE;
  fb_accession         dbxref.accession%TYPE;
  d_accession          dbxref.accession%TYPE;
  f_uniquename_gene    feature.uniquename%TYPE;
  f_CG_gene            dbxref.accession%TYPE;
  f_CG_gene_old        dbxref.accession%TYPE;
  f_CG_transcript      dbxref.accession%TYPE;
  f_CG_protein           dbxref.accession%TYPE;
  f_name_gene          feature.name%TYPE;
  f_uniquename_transcript feature.uniquename%TYPE;
  f_name_transcript feature.name%TYPE;
  f_uniquename_exon feature.uniquename%TYPE;
  f_name_exon feature.name%TYPE;
  f_uniquename_protein feature.uniquename%TYPE;
  f_name_protein feature.name%TYPE;
  f_d_id               feature_dbxref.feature_dbxref_id%TYPE;
  dx_id                dbxref.dbxref_id%TYPE;
  dx_id_gene           dbxref.dbxref_id%TYPE;
  d_id                 db.db_id%TYPE;
  s_type_id            synonym.type_id%TYPE;
  s_id                 synonym.synonym_id%TYPE;
  p_id                 pub.pub_id%TYPE;
  p_type_id            cvterm.cvterm_id%TYPE;
  c_cv_id              cv.cv_id%TYPE;
  f_s_id               feature_synonym.feature_synonym_id%TYPE;
  fr_row              feature_relationship%ROWTYPE;
  f_accession_temp varchar(255);
  f_accession varchar(255);
  f_type_gene CONSTANT varchar :='gene';
  f_type_exon CONSTANT varchar :='exon';
  f_type_transcript CONSTANT varchar :='mRNA';
  f_type_snoRNA CONSTANT varchar :='snoRNA';
  f_type_ncRNA CONSTANT varchar :='ncRNA';
  f_type_snRNA CONSTANT varchar :='snRNA';
  f_type_tRNA CONSTANT varchar :='tRNA';
  f_type_miRNA CONSTANT varchar :='miRNA';
  f_type_miscRNA CONSTANT varchar :='misc. non-coding RNA';
  f_type_rRNA CONSTANT varchar :='rRNA';
  f_type_pseudo CONSTANT varchar :='pseudogene';
  f_type_protein CONSTANT varchar :='protein';
  f_type_allele CONSTANT varchar :='alleleof';
 f_dbname_gadfly CONSTANT varchar :='FlyBase Annotation IDs';
 f_dbname_FB CONSTANT varchar :='FlyBase';
  c_name_synonym CONSTANT varchar:='synonym';
  cv_cvname_synonym CONSTANT varchar:='synonym type';
  p_miniref         CONSTANT varchar:='gadfly3';
  p_cvterm_name     CONSTANT varchar:='computer file';
  p_cv_name         CONSTANT varchar:='pub type';
BEGIN
 RAISE NOTICE 'enter fr_i, fr.object_id:%, fr.subject_id:%', NEW.object_id, NEW.subject_id;
 SELECT INTO f_type name from cvterm  where cvterm_id=NEW.type_id;
 IF f_type=f_type_allele THEN
    SELECT INTO f_accession d.accession from feature_dbxref fd, dbxref d where fd.feature_id=NEW.subject_id and fd.dbxref_id=d.dbxref_id and d.accession like 'FBal%';
/*  here we do not insert dbxref for FBal here
    IF f_accession IS NULL THEN
           SELECT INTO maxid_fb to_number(substring(max(accession) from 5 for 11),'9999999') from dbxref dx, db d  where dx.db_id=d.db_id and d.name = f_dbname_FB and accession like 'FBal%';  
           IF maxid_fb IS NULL OR maxid_fb< 70000  THEN
               maxid_fb:=70000;
           ELSE 
               maxid_fb:=maxid_fb+1;
           END IF;
           id_fb:=lpad(CAST(maxid_fb AS TEXT), 7, '0000000');
           fb_accession:=CAST('FBal'||id_fb AS TEXT);
           RAISE NOTICE 'fb_accession is:%', fb_accession;
           SELECT INTO d_id db_id from db where name=f_dbname_FB;
           RAISE NOTICE 'db_id is:%', d_id;
           SELECT INTO dx_id dbxref_id from dbxref dx, db d where dx.db_id=d.db_id and d.name=f_dbname_FB and accession=fb_accession;
           IF ( dx_id IS NOT NULL ) THEN
                RAISE NOTICE 'warning: you insert dumplicate accession:% into db....', fb_accession;
           ELSE 
              INSERT INTO dbxref(db_id, accession) values(d_id, fb_accession);
              SELECT INTO f_dbxref_id dbxref_id from dbxref dx, db d where dx.db_id=d.db_id and d.name=f_dbname_FB and accession=fb_accession;
           END IF;
           INSERT INTO feature_dbxref(feature_id, dbxref_id) values(NEW.subject_id, f_dbxref_id);       
    END IF;
    SELECT INTO f_d_id feature_dbxref_id from feature_dbxref fd, dbxref d where fd.feature_id=NEW.subject_id and fd.dbxref_id=d.dbxref_id and d.accession like 'FBgn%';
    IF f_d_id IS NOT NULL THEN
        delete from feature_dbxref where feature_dbxref_id=f_d_id;
        RAISE NOTICE 'delete this feature_dbxref which originally set as FBgn, and should be FBal:%',f_d_id;      
    END IF;
*/
 ELSE
   SELECT INTO f_type c.name from feature f, cvterm c  where f.type_id=c.cvterm_id and f.feature_id=NEW.object_id;
   IF f_type=f_type_gene THEN 
      SELECT INTO f_type_temp c.name from feature f, cvterm c where f.feature_id=NEW.subject_id and f.type_id=c.cvterm_id and f.is_analysis='false' and f.is_obsolete='false';

-- here for new transcript of new/old gene, it will: generate new FBtr and set to both f.uniquename and d.accession, also generate CG/CRnnnnn-R_, synonym. 
      IF (f_type_temp=f_type_transcript or f_type_temp=f_type_snoRNA or f_type_temp=f_type_ncRNA or f_type_temp=f_type_snRNA or f_type_temp=f_type_tRNA or f_type_temp=f_type_rRNA or f_type_temp=f_type_miRNA or f_type_temp=f_type_pseudo or f_type_temp=f_type_miscRNA ) THEN
          SELECT INTO f_row_t * from feature where feature_id=NEW.subject_id;
          IF f_row_t.uniquename like 'FBgn:temp%'  THEN
              SELECT INTO maxid_fb max(to_number(substring(accession from 5 for 11), '9999999'))+1 from dbxref dx, db d  where dx.db_id=d.db_id and  d.name=f_dbname_FB and accession like 'FBtr_______';
             id_fb:=lpad(CAST(maxid_fb AS TEXT), 7, '0000000');
             fb_accession:=CAST('FBtr'||id_fb AS TEXT);
             RAISE NOTICE 'fb_accession is:%', fb_accession;
             SELECT INTO d_id db_id from db where name=f_dbname_FB;
             INSERT INTO dbxref(db_id, accession) values(d_id, fb_accession);
             SELECT INTO dx_id dbxref_id from dbxref dx, db d where dx.db_id=d.db_id and d.name=f_dbname_FB and accession=fb_accession;
             INSERT INTO feature_dbxref(feature_id, dbxref_id, is_current) values(NEW.subject_id, dx_id, 'true');
             RAISE NOTICE 'insert FBtr:% into feature_dbxref, and set is_current as true', fb_accession;
             SELECT INTO f_CG_gene_digit to_number(substring(accession from 3 for 7),'99999') from feature_dbxref fd, dbxref d  where fd.feature_id=NEW.object_id and fd.dbxref_id=d.dbxref_id and fd.is_current='true' and (d.accession like 'C______' or d.accession like 'C_____');
             f_accession_temp:=f_row_t.uniquename;
             IF f_type_temp=f_type_transcript and f_CG_gene_digit IS NOT NULL THEN
                len:=length(f_accession_temp);
                letter_t:=substring(f_accession_temp from len for 1);             
                f_CG_transcript:=CAST('CG'||f_CG_gene_digit||'-R'||letter_t  AS TEXT);
             ELSIF f_CG_gene_digit IS NOT NULL THEN
                len:=length(f_accession_temp);
                letter_t:=substring(f_accession_temp from len for 1);             
                f_CG_transcript:=CAST('CR'||f_CG_gene_digit||'-R'||letter_t  AS TEXT);
                f_CG_gene:=CAST('CR'||f_CG_gene_digit  AS TEXT);
                f_CG_gene_old:=CAST('CG'||f_CG_gene_digit  AS TEXT);
                SELECT INTO f_row_g * from feature where feature_id=NEW.object_id;
-- here for case of non_coding gene, we need to update CG to CR for f.name, dbxref.accession
                IF f_row_g.name =f_CG_gene_old THEN
                    update feature set name=f_CG_gene where feature_id=NEW.object_id;
                END IF;
                SELECT INTO dx_id_gene dbxref_id from dbxref where accession=f_CG_gene;
                IF dx_id_gene IS NULL THEN
                   update dbxref set accession=f_CG_gene where accession=f_CG_gene_old;
                END IF;
             END IF;
             RAISE NOTICE 'start to update feature, old:%, new:%', f_row_t.uniquename,fb_accession;
             IF f_row_t.name like '%temp%' and f_CG_gene_digit IS NOT NULL THEN
                RAISE NOTICE 'also update feature.name';
                UPDATE feature set name=f_CG_transcript, uniquename=fb_accession, dbxref_id=dx_id where feature_id=NEW.subject_id;
                f_name_transcript:=f_CG_transcript;
             ELSE                
                UPDATE feature set  uniquename=fb_accession, dbxref_id=dx_id where feature_id=NEW.subject_id;
                f_name_transcript:=f_row_t.name;
             END IF;   
             RAISE NOTICE 'assign new number for transcript:%', NEW.subject_id;

/* start from R5.2, we NO long insert any synonym triggered by Apollo data
             SELECT INTO s_type_id cvterm_id from cvterm c1, cv c2 where c1.name=c_name_synonym and c2.name=cv_cvname_synonym and c1.cv_id=c2.cv_id;
             RAISE NOTICE 's_type_id:%', s_type_id;
             SELECT INTO s_id synonym_id from synonym where name=f_name_transcript and type_id=s_type_id;
             IF s_id IS NULL THEN 
                 INSERT INTO synonym(name, synonym_sgml, type_id) values(f_name_transcript, f_name_transcript, s_type_id);
                 SELECT INTO s_id synonym_id from synonym where name=f_name_transcript and type_id=s_type_id;
             END IF;
             SELECT INTO p_id pub_id from pub p, cvterm c where uniquename=p_miniref and c.name=p_cvterm_name and c.cvterm_id=p.type_id;
             IF p_id IS NULL THEN
                 SELECT INTO p_type_id cvterm_id from cvterm where name=p_cvterm_name;
                 IF p_type_id IS NULL THEN
                    SELECT INTO c_cv_id cv_id from cv where name=p_cv_name;
                    IF c_cv_id IS NULL THEN
                        INSERT INTO cv(name) values(p_cv_name);
                        SELECT INTO c_cv_id cv_id from cv where name=p_cv_name;
                    END IF;
                    INSERT INTO cvterm(name, cv_id) values(p_cvterm_name, c_cv_id);
                    SELECT INTO c_cv_id cv_id from cv where name=p_cv_name;
                 END IF;
                 INSERT INTO pub(uniquename, miniref, type_id) values(p_miniref, p_miniref, p_type_id);
                 SELECT INTO p_id pub_id from pub p, cvterm c where uniquename=p_miniref and c.name=p_cvterm_name and c.cvterm_id=p.type_id;
             END IF;
             RAISE NOTICe 'start to insert feature_synonym:synonym_id:%,feature_id:%, pub_id:%', s_id, f_row_t.feature_id, p_id;
             SELECT INTO f_s_id feature_synonym_id from feature_synonym where feature_id=f_row_t.feature_id and synonym_id=s_id and pub_id=p_id;
             IF f_s_id IS NULL THEN 
                  INSERT INTO feature_synonym(feature_id, synonym_id, pub_id, is_current) values (f_row_t.feature_id, s_id, p_id, 'true');           
             END IF;   
*/  
             RAISE NOTICE 'insert new accession for transcript, dbname:%, accession:%', f_dbname_gadfly, f_CG_transcript;
          IF f_CG_gene_digit IS NOT NULL THEN
             SELECT INTO d_id db_id from db where name=f_dbname_gadfly;
             SELECT INTO dx_id dbxref_id from dbxref dx, db d where dx.db_id=d.db_id and d.name=f_dbname_gadfly and accession=f_CG_transcript;
             IF (dx_id IS NOT NULL ) THEN 
                RAISE NOTICE 'warning: you insert dumplicate transcript:% into db....', f_CG_transcript;
             ELSE 
               insert into dbxref (db_id, accession) values(d_id, f_CG_transcript);
               SELECT INTO dx_id dbxref_id from dbxref dx, db d where dx.db_id=d.db_id and d.name=f_dbname_gadfly and accession=f_CG_transcript;
             END IF;
             SELECT INTO f_d_id feature_dbxref_id from feature_dbxref where feature_id=NEW.subject_id and dbxref_id=dx_id;
             IF f_d_id IS NULL THEN
                INSERT INTO feature_dbxref(feature_id, dbxref_id, is_current) values(NEW.subject_id, dx_id, 'true');     
              END IF;
           ELSE
             RAISE NOTICE 'NO CG/CR associated with the gene, so will NOT add CG/CRnnnnn-R_ to this transcript here:%',fb_accession;
           END IF;
          ELSE
             RAISE NOTICe 'Warning:unexpected format for uniquename(transcript):%', f_row_t.uniquename;
          END IF;
      ELSE
              RAISE NOTICE 'wrong feature_relationship: gene->NO_transcript:object_id:%, subject_id:%', NEW.object_id, NEW.subject_id;
      END IF;

   ELSIF (f_type=f_type_transcript or f_type=f_type_ncRNA  or f_type=f_type_snoRNA or f_type=f_type_snRNA or f_type=f_type_tRNA or f_type=f_type_rRNA or f_type=f_type_miRNA or f_type=f_type_pseudo or f_type=f_type_miscRNA )   THEN
      SELECT INTO f_CG_gene d.accession from feature f, feature_relationship fr, cvterm c, feature_dbxref fd, dbxref d, db d1 where f.feature_id=fr.object_id and fr.subject_id=NEW.object_id and f.type_id=c.cvterm_id and c.name=f_type_gene and f.feature_id=fd.feature_id and fd.dbxref_id=d.dbxref_id and fd.is_current='true' and d.db_id=d1.db_id and d1.name=f_dbname_gadfly and d.accession like 'C______';
      SELECT INTO f_name_gene f.name from feature f, feature_relationship fr, cvterm c where f.feature_id=fr.object_id and fr.subject_id=NEW.object_id and f.type_id=c.cvterm_id and c.name=f_type_gene;
      SELECT INTO f_uniquename_gene f.uniquename from feature f, feature_relationship fr, cvterm c where f.feature_id=fr.object_id and fr.subject_id=NEW.object_id and f.type_id=c.cvterm_id and c.name=f_type_gene;
      SELECT INTO f_type_temp c.name from feature f, cvterm c where f.feature_id=NEW.subject_id and f.type_id=c.cvterm_id;

-- here for proteint of new transcript, it will: generate new FBpp and set to both f.uniquename and d.accession, also generate CG/CR, synonym.
-- if we first insert tr/protein, then gene, it will add CG/Rnnnnn-P_ to protein in tr_f_u 
-- here f_CG_gene maybe null, which cause overwrite problem for protein temp uniquename
      IF f_type_temp=f_type_protein  THEN
          SELECT INTO f_row_p * from feature where feature_id=NEW.subject_id;  
          IF f_row_p.uniquename like 'FBgn:temp%'  THEN  
             SELECT INTO maxid_fb max(to_number(substring(accession from 5 for 11), '9999999'))+1 from dbxref dx, db d  where dx.db_id=d.db_id and  d.name=f_dbname_FB and accession like 'FBpp_______';
             id_fb:=lpad(CAST(maxid_fb AS TEXT), 7, '0000000');
             fb_accession:=CAST('FBpp'||id_fb AS TEXT);
             RAISE NOTICE 'fb_accession is:%', fb_accession;
             SELECT INTO d_id db_id from db where name=f_dbname_FB;
             INSERT INTO dbxref(db_id, accession) values(d_id, fb_accession);
             SELECT INTO dx_id dbxref_id from dbxref dx, db d where dx.db_id=d.db_id and d.name=f_dbname_FB and accession=fb_accession;
             INSERT INTO feature_dbxref(feature_id, dbxref_id, is_current) values(NEW.subject_id, dx_id, 'true');
             RAISE NOTICE 'insert FBpp:% into feature_dbxref, and set is_current as true', fb_accession;

             f_accession_temp:=f_row_p.uniquename;
             len:=length(f_accession_temp);
             letter_p:=substring(f_accession_temp from len for 1);       
             f_CG_protein:=CAST(f_CG_gene||'-P'||letter_p  AS TEXT);
             f_name_protein:=CAST(f_name_gene||'-P'||letter_p  AS TEXT);

             RAISE NOTICE 'start to update feature, old:%, new:%', f_row_p.uniquename, fb_accession;
             IF f_row_p.name like '%temp%' and f_name_gene IS NOT NULL THEN
                RAISE NOTICE 'also update feature.name';
                UPDATE feature set name=f_name_protein, uniquename=fb_accession, dbxref_id=dx_id where feature_id=NEW.subject_id;
             ELSE                
                UPDATE feature set  uniquename=fb_accession, dbxref_id=dx_id where feature_id=NEW.subject_id;
                f_name_protein:=f_row_p.name;
             END IF;  


             RAISE NOTICE 'update uniquename of protein:% to new uniquename:%',f_row_p.uniquename, fb_accession;
          IF f_CG_gene IS NOT NULL THEN
             SELECT INTO d_id db_id from db where name=f_dbname_gadfly;
             SELECT INTO dx_id dbxref_id from dbxref dx, db d  where dx.db_id=d.db_id and d.name=f_dbname_gadfly and accession=f_CG_protein;
             IF  dx_id IS NULL THEN
                 insert into dbxref (db_id, accession) values(d_id, f_CG_protein);
                 SELECT INTO dx_id dbxref_id from dbxref dx, db d  where dx.db_id=d.db_id and d.name=f_dbname_gadfly and accession=f_CG_protein;
             END IF;
             SELECT INTO f_d_id feature_dbxref_id from feature_dbxref where feature_id=NEW.subject_id and dbxref_id=dx_id;
             IF f_d_id IS NULL THEN 
                 INSERT INTO feature_dbxref(feature_id, dbxref_id, is_current) values(NEW.subject_id, dx_id, 'true');
             END IF;
             RAISE NOTICE 'assign new number:% for protein:%', f_CG_protein,  NEW.subject_id;
          ELSE
             RAISE NOTICE 'no existing CG/CR for this gene, so will NOT add CG/Rnnnnn-P_ to this protein:%',fb_accession;
          END IF;

/* start from r5.2, we NO long insert and synonym triggered by Apollo file
             SELECT INTO s_type_id cvterm_id from cvterm c1, cv c2 where c1.name=c_name_synonym and c2.name=cv_cvname_synonym and c1.cv_id=c2.cv_id;
             SELECT INTO s_id synonym_id from synonym where name=f_name_protein and type_id=s_type_id;
             IF s_id IS NULL THEN
                  INSERT INTO synonym(name, synonym_sgml, type_id) values(f_name_protein, f_name_protein, s_type_id);
                  SELECT INTO s_id synonym_id from synonym where name=f_name_protein and type_id=s_type_id;
             END IF;

             SELECT INTO p_id pub_id from pub p, cvterm c where uniquename=p_miniref and c.name=p_cvterm_name and c.cvterm_id=p.type_id;
             IF p_id IS NULL THEN
                 SELECT INTO p_type_id cvterm_id from cvterm where name=p_cvterm_name;
                 IF p_type_id IS NULL THEN
                    SELECT INTO c_cv_id cv_id from cv where name=p_cv_name;
                    IF c_cv_id IS NULL THEN
                        INSERT INTO cv(name) values(p_cv_name);
                        SELECT INTO c_cv_id cv_id from cv where name=p_cv_name;
                    END IF;
                    INSERT INTO cvterm(name, cv_id) values(p_cvterm_name, c_cv_id);
                    SELECT INTO c_cv_id cv_id from cv where name=p_cv_name;
                 END IF;
                 INSERT INTO pub(uniquename, miniref, type_id) values(p_miniref, p_miniref, p_type_id);
                  SELECT INTO p_id pub_id from pub p, cvterm c where uniquename=p_miniref and c.name=p_cvterm_name and c.cvterm_id=p.type_id;
             END IF;
             SELECT INTo f_s_id feature_synonym_id from feature_synonym where feature_id=f_row_p.feature_id and synonym_id=p_id;
             IF f_s_id IS NOT NULL THEN
                INSERT INTO feature_synonym(feature_id, synonym_id, pub_id, is_current) values (f_row_p.feature_id, s_id, p_id, 'true');
             END IF;
*/
       
          ELSIF (f_row_p.uniquename like 'FBpp_______' ) and  f_row_p.uniquename not like '%:%' THEN
              RAISE NOTICE 'add protein to exist transcript';
          ELSE
              RAISE NOTICE 'warning:unexpected format of protein uniquename:%', f_row_p.uniquename;
          END IF;
      ELSIF f_type_temp=f_type_exon  THEN
-- for Apollo chadoXML, it will never come here since fr_g/t not yet in db, so temp uniquename of exon will unpdate in tr_f_u.sql
          SELECT INTO f_row_e * from feature where feature_id=NEW.subject_id;
          IF f_row_e.uniquename like 'FBgn:temp%' and f_uniquename_gene IS NOT NULL  THEN  
             SELECT INTO f_uniquename_gene f.uniquename from feature f, feature_relationship fr, cvterm c where f.feature_id=fr.object_id and fr.subject_id=NEW.object_id and f.type_id=c.cvterm_id and c.name=f_type_gene ;
             SELECT INTO f_name_gene f.name from feature f, feature_relationship fr, cvterm c where f.feature_id=fr.object_id and fr.subject_id=NEW.object_id and f.type_id=c.cvterm_id and c.name=f_type_gene ;
             RAISE NOTICE 'gene uniquename:%, gene name:%',f_uniquename_gene, f_name_gene;
-- in case of: FBgn:temp1:2L_4639000_4649000:21, how to find the suffix here:21
             f_accession_temp:=f_row_e.uniquename;
             len:=length(f_accession_temp)-1;
             letter_e:=substring(f_accession_temp from len for 2);    
             letter_e:=replace(letter_e, ':','');
              f_uniquename_exon:=CAST(f_uniquename_gene||':'||letter_e  AS TEXT);
              f_name_exon:=CAST(f_name_gene||':'||letter_e AS TEXT);

--              f_name_exon:=replace(f_row_e.name, 'FBgn:temp' , f_uniquename_gene);
--             f_uniquename_exon:=replace(f_row_e.uniquename, 'FBgn:temp', f_uniquename_gene); 
 
             RAISE NOTICE 'letter_e:%, uniquename:%', letter_e, f_uniquename_exon;
             if f_row_e.name like '%temp%' THEN
                UPDATE feature set name=f_name_exon, uniquename=f_uniquename_exon, dbxref_id=d_id where feature_id=NEW.subject_id;
             ELSE
                UPDATE feature set  uniquename=f_uniquename_exon, dbxref_id=d_id where feature_id=NEW.subject_id;
             END IF;               
          ELSIF f_row_e.uniquename like 'FBgn%:%' THEN 
               RAISE NOTICE 'add exon to exist transcript';  
          ELSE
               RAISE NOTICE 'unexpected format of exon uniquename:%', f_row_e.uniquename;            
          END IF;
      ELSE
         RAISE NOTICE 'no link to gene for this transcript or wrong feature_relationship: transcript->protein/exon:object_id:%, subject_id:%', NEW.object_id, NEW.subject_id;
      END IF;
   END IF;
 END IF;
 RAISE NOTICE 'leave fr_i ....';
 RETURN NEW;
END;
$$;


ALTER FUNCTION public.feature_relationship_propagatename_fn_i() OWNER TO postgres;

--
-- Name: featureloc; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.featureloc (
    featureloc_id integer NOT NULL,
    feature_id integer NOT NULL,
    srcfeature_id integer,
    fmin integer,
    is_fmin_partial boolean DEFAULT false NOT NULL,
    fmax integer,
    is_fmax_partial boolean DEFAULT false NOT NULL,
    strand smallint,
    phase integer,
    residue_info text,
    locgroup integer DEFAULT 0 NOT NULL,
    rank integer DEFAULT 0 NOT NULL,
    CONSTRAINT featureloc_c2 CHECK ((fmin <= fmax))
);


ALTER TABLE public.featureloc OWNER TO postgres;

--
-- Name: featureloc_slice(integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.featureloc_slice(integer, integer) RETURNS SETOF public.featureloc
    LANGUAGE sql
    AS $_$SELECT * from featureloc where boxquery($1, $2) @ boxrange(fmin,fmax)$_$;


ALTER FUNCTION public.featureloc_slice(integer, integer) OWNER TO postgres;

--
-- Name: featureloc_slice(integer, integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.featureloc_slice(integer, integer, integer) RETURNS SETOF public.featureloc
    LANGUAGE sql
    AS $_$SELECT * 
   FROM featureloc 
   WHERE boxquery($1, $2, $3) && boxrange(srcfeature_id,fmin,fmax)$_$;


ALTER FUNCTION public.featureloc_slice(integer, integer, integer) OWNER TO postgres;

--
-- Name: featureloc_slice(character varying, integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.featureloc_slice(character varying, integer, integer) RETURNS SETOF public.featureloc
    LANGUAGE sql
    AS $_$SELECT featureloc.* 
   FROM featureloc 
   INNER JOIN feature AS srcf ON (srcf.feature_id = featureloc.srcfeature_id)
   WHERE boxquery($2, $3) @ boxrange(fmin,fmax)
   AND srcf.name = $1 $_$;


ALTER FUNCTION public.featureloc_slice(character varying, integer, integer) OWNER TO postgres;

--
-- Name: featureslice(integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.featureslice(integer, integer) RETURNS SETOF public.featureloc
    LANGUAGE sql
    AS $_$SELECT * from featureloc where boxquery($1, $2) @ boxrange(fmin,fmax)$_$;


ALTER FUNCTION public.featureslice(integer, integer) OWNER TO postgres;

--
-- Name: fn_feature_del(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_feature_del() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE 
  f_type cvterm.name%TYPE;
  f_id_gene feature.feature_id%TYPE;
  f_id_transcript feature.feature_id%TYPE;
  f_id_exon feature.feature_id%TYPE;
  f_id_exon_temp feature.feature_id%TYPE; 
  f_id_protein feature.feature_id%TYPE;
  f_id_allele feature.feature_id%TYPE;
  fr_object_id feature.feature_id%TYPE;
  f_type_gene CONSTANT varchar :='gene';
  f_type_exon CONSTANT varchar :='exon';
  f_type_transcript CONSTANT varchar :='mRNA';	
  f_type_snoRNA CONSTANT varchar :='snoRNA';
  f_type_ncRNA CONSTANT varchar :='ncRNA';
  f_type_snRNA CONSTANT varchar :='snRNA';
  f_type_tRNA CONSTANT varchar :='tRNA';
  f_type_rRNA CONSTANT varchar :='rRNA';
  f_type_miRNA CONSTANT varchar :='miRNA';
  f_type_miscRNA CONSTANT varchar :='misc. non-coding RNA';
  f_type_pseudo CONSTANT varchar :='pseudogene';
  f_type_protein CONSTANT varchar :='protein';
  f_type_allele CONSTANT varchar :='alleleof';
  f_return feature.feature_id%TYPE;
  f_row feature%ROWTYPE;
  fr_row_transcript feature_relationship%ROWTYPE;
  fr_row_exon feature_relationship%ROWTYPE;
  fr_row_protein feature_relationship%ROWTYPE;
  message   varchar(255);
BEGIN
   RAISE NOTICE 'enter f_d, feature uniquename:%, type_id:%',OLD.uniquename, OLD.type_id;
   f_return:=OLD.feature_id;
   SELECT INTO f_type c.name from feature f, cvterm c where f.feature_id=OLD.feature_id and f.type_id=c.cvterm_id;
   IF f_type=f_type_gene THEN
     SELECT INTO f_id_allele fr.subject_id from  feature_relationship fr, cvterm c where  (fr.object_id=OLD.feature_id or fr.subject_id=OLD.feature_id)  and fr.type_id=c.cvterm_id and c.name=f_type_allele;
     IF NOT FOUND THEN 
       FOR fr_row_transcript IN SELECT * from feature_relationship fr where fr.object_id=OLD.feature_id LOOP
         SELECT INTO f_id_transcript  f.feature_id from feature f, cvterm c where f.feature_id=fr_row_transcript.subject_id and f.type_id=c.cvterm_id and (c.name=f_type_transcript or c.name=f_type_ncRNA or c.name=f_type_snoRNA or c.name=f_type_snRNA or c.name=f_type_tRNA  or c.name=f_type_rRNA  or c.name=f_type_pseudo  or c.name=f_type_miRNA or c.name=f_type_miscRNA); 
         SELECT INTO f_id_gene f.feature_id from feature f, feature_relationship fr, cvterm c where f.feature_id=fr.object_id and fr.subject_id=f_id_transcript and f.type_id=c.cvterm_id and c.name=f_type_gene and f.feature_id !=OLD.feature_id;
         IF f_id_gene IS NULL and f_id_transcript IS NOT NULL THEN
            RAISE NOTICE 'delete lonely transcript:%', f_id_transcript;
            message:=CAST('delete lonely transcript'||f_id_transcript AS TEXT);
            delete from feature where feature_id=f_id_transcript;
         ELSIF f_id_gene IS NOT NULL AND F_id_transcript IS NOT NULL THEN
            RAISE NOTICE 'There is another gene:% associated with this transcript:%, so this transcript will be kept',f_id_gene, f_id_transcript;
            message:=CAST('There is another gene:'||f_id_gene||' associated with this transcript:'||f_id_transcript AS TEXT); 
         END IF;
      END LOOP;
      message:=CAST('delete gene:'||OLD.feature_id AS TEXT);
    ELSE
     RAISE NOTICE 'there is other allele associated with this gene:%', f_id_allele;
            message:=CAST('There is other allele associated with this gene:'||f_id_allele AS TEXT); 
     -- return NULL will skip the delete operation since this happen BEFORE delete on featre ????  -----------------
     return NULL;
    END IF;
  ELSIF (f_type=f_type_transcript or f_type=f_type_ncRNA or f_type=f_type_snoRNA or f_type=f_type_snRNA or f_type=f_type_tRNA  or f_type=f_type_rRNA or f_type=f_type_pseudo or  f_type=f_type_miRNA or f_type=f_type_miscRNA) THEN
     FOR fr_row_exon IN SELECT * from feature_relationship fr where fr.object_id=OLD.feature_id LOOP
        select INTO f_id_exon f.feature_id from feature f, cvterm c where f.feature_id=fr_row_exon.subject_id and f.type_id=c.cvterm_id and c.name=f_type_exon;
        SELECT INTO f_id_transcript f.feature_id from feature f, feature_relationship fr, cvterm c where f.feature_id=fr.object_id and fr.subject_id=f_id_exon and f.type_id=c.cvterm_id and (c.name=f_type_transcript or c.name=f_type_ncRNA or c.name=f_type_snoRNA or c.name=f_type_snRNA or c.name=f_type_tRNA  or c.name=f_type_rRNA  or c.name=f_type_pseudo  or c.name=f_type_miRNA or c.name=f_type_miscRNA) and f.feature_id!=OLD.feature_id;
        IF f_id_transcript IS NULL and f_id_exon IS NOT NULL THEN
            RAISE NOTICE 'delete lonely exon:%', f_id_exon;
           delete from feature where feature_id=f_id_exon; 
            message:=CAST('delete lonely exon:'||f_id_exon AS TEXT); 
        ELSIF f_id_transcript IS NOT NULL and f_id_exon IS NOT NULL THEN
            RAISE NOTICE 'There is another transcript:% associated with this exon:%, so this exon will be kept', f_id_transcript, f_id_exon;
            message:=CAST('There is another transcript:'||f_id_transcript||' associated with this exon:'||f_id_exon AS TEXT); 
        END IF;    
     END LOOP;

     FOR fr_row_protein IN SELECT * from feature_relationship fr where fr.object_id=OLD.feature_id LOOP
        SELECT INTO f_id_protein f.feature_id from feature f, cvterm c where f.feature_id=fr_row_protein.subject_id and f.type_id=c.cvterm_id and c.name=f_type_protein;
        SELECT INTO f_id_transcript f.feature_id from feature f, feature_relationship fr, cvterm c where f.feature_id=fr.object_id and fr.subject_id=f_id_protein and f.type_id=c.cvterm_id and (c.name=f_type_transcript or c.name=f_type_ncRNA or c.name=f_type_snoRNA or c.name=f_type_snRNA or c.name=f_type_tRNA  or c.name=f_type_rRNA   or c.name=f_type_pseudo or  c.name=f_type_miRNA or c.name=f_type_miscRNA) and f.feature_id !=OLD.feature_id;
        IF f_id_transcript IS NULL and f_id_protein IS NOT NULL THEN
                  RAISE NOTICE 'delete lonely protein:%', f_id_protein;
                  delete from feature where feature_id=f_id_protein;
                  message:=CAST('delete lonely protein:'||f_id_protein AS TEXT); 
        ELSIF f_id_transcript IS NOT NULL and f_id_protein IS NOT NULL THEN
                  RAISE NOTICE 'There is another transcript:% associated with this protein:%, so this exon will be kept', f_id_transcript, f_id_protein;
        END IF;
     END LOOP;
  END IF;
  RAISE NOTICE 'leave f_d ....';
  RETURN OLD; 
END;
$$;


ALTER FUNCTION public.fn_feature_del() OWNER TO postgres;

--
-- Name: fn_feature_evi_del(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_feature_evi_del() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  f_type  cvterm.name%TYPE;
  f_feature feature.feature_id%TYPE;
  f_type_est CONSTANT varchar :='EST';
  f_type_cdna CONSTANT varchar :='cDNA';
  f_type_protein CONSTANT varchar :='protein';
  feature_HSP_csr cursor for SELECT feature_id from featureloc where srcfeature_id=OLD.feature_id;
  feature_clone_csr cursor for  select DISTINCT object_id from feature_relationship
			     where subject_id in (select feature_id from
			     featureloc where srcfeature_id=OLD.feature_id);
  message varchar(255);
BEGIN
     	 RAISE NOTICE 'enter feature_evi_del, feature uniquename:%, type_id:%',OLD.uniquename, OLD.type_id;
         SELECT INTO f_type name from cvterm  where cvterm_id=OLD.type_id;
	 
 	        IF f_type=f_type_est or f_type=f_type_cdna or f_type=f_type_protein
		   THEN
		      IF OLD.residues!=NEW.residues
		       THEN
		       RAISE NOTICE 'old and new residues are different'; 
		     open feature_HSP_csr;
		        LOOP
                         FETCH feature_HSP_csr into f_feature;
			 exit when f_feature is NULL;
			 delete from feature where feature_id=f_feature;
			   message:=CAST('delete old matches for feature:'||f_feature||' associated with this '|| f_type ||':'|| OLD.feature_id AS TEXT); 
			   --insert into trigger_log(value, table_name, id) values(message, 'feature',f_feature);  
			        RAISE NOTICE 'delete old HSP matches feature:%, srcfeature_id:%',f_feature,OLD.feature_id;
	                END LOOP;
		      close feature_HSP_csr;
		      open feature_clone_csr;
		        LOOP
                         FETCH feature_clone_csr into f_feature;
			 exit when f_feature is NULL;
			  delete from feature where feature_id=f_feature;
			      message:=CAST('delete old matches for feature:'||f_feature||' associated with this '|| f_type ||':'|| OLD.feature_id AS TEXT); 
			  -- insert into trigger_log(value, table_name, id) values(message, 'feature',f_feature); 
			  RAISE NOTICE 'delete old alignment feature:%, srcfeature_id:%',f_feature,OLD.feature_id;
	                END LOOP;
		      close feature_clone_csr;
		      END IF;
		   END IF;
			
                RETURN NEW;
        END;
$$;


ALTER FUNCTION public.fn_feature_evi_del() OWNER TO postgres;

--
-- Name: grp_assignname_fn_i(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.grp_assignname_fn_i() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  maxid      int;
  maxid_temp int;
  pos        int;
  id         varchar(255);
  maxid_cg   int;
  id_fb      varchar(255);
  message   varchar(255);
  f_row_g grp%ROWTYPE;
  f_type  cvterm.name%TYPE;
  f_type_id cvterm.cvterm_id%TYPE;
  letter_t varchar;
  letter_p varchar;
  d_id    db.db_id%TYPE;
  f_dbxref_id dbxref.dbxref_id%TYPE;
  f_dbxref_id_temp dbxref.dbxref_id%TYPE;
  fd_id grp_dbxref.grp_dbxref_id%TYPE;
  cg_accession dbxref.accession%TYPE;
  d_accession dbxref.accession%TYPE;
  f_uniquename_temp grp.uniquename%TYPE;
  f_uniquename grp.uniquename%TYPE;
  p_id                 pub.pub_id%TYPE;
  p_type_id            cvterm.cvterm_id%TYPE;
  c_cv_id              cv.cv_id%TYPE;
  f_s_id               feature_synonym.feature_synonym_id%TYPE;
  f_d_id               grp_dbxref.grp_dbxref_id%TYPE;
  f_dbname_gadfly CONSTANT varchar :='FlyBase Annotation IDs';
  f_dbname_FB CONSTANT varchar :='FlyBase';
  o_genus  CONSTANT varchar :='Drosophila';
  o_species  CONSTANT varchar:='melanogaster';
  c_name_synonym CONSTANT varchar:='synonym';
  cv_cvname_synonym CONSTANT varchar:='synonym type';
  p_miniref         CONSTANT varchar:='gadfly3';
  p_cvterm_name     CONSTANT varchar:='computer file';
  p_cv_name         CONSTANT varchar:='pub type';
BEGIN
  RAISE NOTICE 'enter grp_i: grp.uniquename:%, grp.type_id:%', NEW.uniquename, NEW.type_id;
-- here assign new FBgg
  IF ( NEW.uniquename like 'FBgg:temp%') THEN
      SELECT INTO f_type c.name from grp f, cvterm c where f.type_id=c.cvterm_id and f.uniquename=NEW.uniquename;
      IF f_type is NOT NULL THEN
        RAISE NOTICE 'in grp_assignname_fn_i type of this grp is:%', f_type;
      END IF;
     
      RAISE NOTICE 'in grp_i, grp type is:%', f_type;
      SELECT INTO f_row_g * from grp where uniquename=NEW.uniquename;
      SELECT INTO maxid max(to_number(substring(accession from 5 for 11), '9999999'))+1 from dbxref dx, db d  where dx.db_id=d.db_id and  d.name=f_dbname_FB and accession like 'FBgg_______';
      IF maxid IS NULL THEN
          maxid:=40;
      END IF;
               RAISE NOTICE 'maxid after is:%', maxid;
               id:=lpad(CAST(maxid as TEXT), 7, '0000000');
               f_uniquename:=CAST('FBgg'||id as TEXT);

               SELECT INTO d_id db_id from db where name= f_dbname_FB;
               IF d_id IS NULL THEN 
                 INSERT INTO db(name) values (f_dbname_FB);
                 SELECT INTO d_id db_id from db where name= f_dbname_FB;
               END IF;
               RAISE NOTICE 'db_id:%, uniquename:%, f_dbname_FB:%:', d_id, f_uniquename, f_dbname_FB; 
               SELECT INTO f_dbxref_id dbxref_id from dbxref where db_id=d_id and accession=f_uniquename;
               IF f_dbxref_id IS NULL THEN 
                 INSERT INTO dbxref (db_id, accession) values(d_id, f_uniquename);
                 SELECT INTO f_dbxref_id dbxref_id from dbxref where db_id=d_id and accession=f_uniquename;
               END IF;
               RAISE NOTICE 'dbxref_id:%', f_dbxref_id;
               RAISE NOTICE 'old uniquename of this feature is:%', f_row_g.uniquename;
               RAISE NOTICE 'new uniquename of this feature is:%', f_uniquename;
               UPDATE grp set uniquename=f_uniquename where grp_id=f_row_g.grp_id;
               select INTO fd_id grp_dbxref_id from grp_dbxref where grp_id=f_row_g.grp_id and dbxref_id=f_dbxref_id;
               IF fd_id IS NULL THEN
                  insert into grp_dbxref(is_current, grp_id, dbxref_id) values ('true',f_row_g.grp_id,f_dbxref_id);
              
               END IF;
  END IF;
  RAISE NOTICE 'leave grp_i .......';
  return NEW;    
END;
$$;


ALTER FUNCTION public.grp_assignname_fn_i() OWNER TO postgres;

--
-- Name: humanhealth_assignname_fn_i(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.humanhealth_assignname_fn_i() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  maxid      int;
  maxid_temp int;
  pos        int;
  id         varchar(255);
  maxid_cg   int;
  id_fb      varchar(255);
  message   varchar(255);
  f_row_g humanhealth%ROWTYPE;
  f_type  cvterm.name%TYPE;
  f_type_id cvterm.cvterm_id%TYPE;
  letter_t varchar;
  letter_p varchar;
  d_id    db.db_id%TYPE;
  f_dbxref_id dbxref.dbxref_id%TYPE;
  f_dbxref_id_temp dbxref.dbxref_id%TYPE;
  fd_id humanhealth_dbxref.humanhealth_dbxref_id%TYPE;
  cg_accession dbxref.accession%TYPE;
  d_accession dbxref.accession%TYPE;
  f_uniquename_temp humanhealth.uniquename%TYPE;
  f_uniquename humanhealth.uniquename%TYPE;
  p_id                 pub.pub_id%TYPE;
  p_type_id            cvterm.cvterm_id%TYPE;
  c_cv_id              cv.cv_id%TYPE;
  f_s_id               humanhealth_synonym.humanhealth_synonym_id%TYPE;
  f_d_id               humanhealth_dbxref.humanhealth_dbxref_id%TYPE;
  f_type_FBlc   CONSTANT varchar :='cDNA library';
  f_dbname_gadfly CONSTANT varchar :='FlyBase Annotation IDs';
  f_dbname_FB CONSTANT varchar :='FlyBase';
  o_genus  CONSTANT varchar :='Drosophila';
  o_species  CONSTANT varchar:='melanogaster';
  c_name_synonym CONSTANT varchar:='synonym';
  cv_cvname_synonym CONSTANT varchar:='synonym type';
  p_miniref         CONSTANT varchar:='gadfly3';
  p_cvterm_name     CONSTANT varchar:='computer file';
  p_cv_name         CONSTANT varchar:='pub type';
BEGIN
  RAISE NOTICE 'enter humanhealth_i: humanhealth.uniquename:%, humanhealth.organism_id:%', NEW.uniquename, NEW.organism_id;
-- here assign new FBhh blah
  IF ( NEW.uniquename like 'FBhh:temp%') THEN
--      SELECT INTO f_type c.name from library f, cvterm c, organism o where f.type_id=c.cvterm_id and f.uniquename=NEW.uniquename and f.organism_id =NEW.organism_id;
--      IF f_type is NOT NULL THEN
--        RAISE NOTICE 'in library_assignname_fn_i type of this library is:%', f_type;
--      END IF;
     
--      RAISE NOTICE 'in lib_i, library type is:%', f_type;
      SELECT INTO f_row_g * from humanhealth where uniquename=NEW.uniquename 
	  and organism_id=NEW.organism_id;
      SELECT INTO maxid max(to_number(substring(uniquename from 5 for 11), '9999999'))+1 from humanhealth where uniquename like 'FBhh_______';
      IF maxid IS NULL THEN
          maxid:=1;
      END IF;
               RAISE NOTICE 'maxid after is:%', maxid;
               id:=lpad(CAST(maxid as TEXT), 7, '0000000');
               f_uniquename:=CAST('FBhh'||id as TEXT);

               SELECT INTO d_id db_id from db where name= f_dbname_FB;
               IF d_id IS NULL THEN 
                 INSERT INTO db(name) values (f_dbname_FB);
                 SELECT INTO d_id db_id from db where name= f_dbname_FB;
               END IF;
               RAISE NOTICE 'db_id:%, uniquename:%, f_dbname_FB:%:', d_id, f_uniquename, f_dbname_FB; 
               SELECT INTO f_dbxref_id dbxref_id from dbxref where db_id=d_id and accession=f_uniquename;
               IF f_dbxref_id IS NULL THEN 
                 INSERT INTO dbxref (db_id, accession) values(d_id, f_uniquename);
                 SELECT INTO f_dbxref_id dbxref_id from dbxref where db_id=d_id and accession=f_uniquename;
               END IF;
               RAISE NOTICE 'dbxref_id:%', f_dbxref_id;
               RAISE NOTICE 'old uniquename of this humanhealth is:%', f_row_g.uniquename;
               RAISE NOTICE 'new uniquename of this humanhealth is:%', f_uniquename;
               UPDATE humanhealth set uniquename=f_uniquename, dbxref_id=f_dbxref_id where humanhealth_id=f_row_g.humanhealth_id;
               select INTO fd_id humanhealth_dbxref_id from humanhealth_dbxref where humanhealth_id=f_row_g.humanhealth_id and dbxref_id=f_dbxref_id;
               IF fd_id IS NULL THEN
                  insert into humanhealth_dbxref(is_current, humanhealth_id, dbxref_id) values ('true',f_row_g.humanhealth_id,f_dbxref_id);
              
               END IF;
  END IF;
  RAISE NOTICE 'leave humanhealth_i .......';
  return NEW;    
END;
$$;


ALTER FUNCTION public.humanhealth_assignname_fn_i() OWNER TO postgres;

--
-- Name: humanhealth_dbxrefprop_pub_audit(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.humanhealth_dbxrefprop_pub_audit() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
	DECLARE
		pkey integer;
		ukey_vals text;
		ukey_cols varchar;
		audit_vals text;
		audit_cols varchar;
		bval varchar;
	BEGIN
		IF TG_OP = 'INSERT' THEN
			pkey := NEW.humanhealth_dbxrefprop_pub_id;
			ukey_vals := NEW.humanhealth_dbxrefprop_id || '<audit_delimiter>' || NEW.pub_id;
			ukey_cols := 'humanhealth_dbxrefprop_id' || '<audit_delimiter>' || 'pub_id';
			audit_cols := 'humanhealth_dbxrefprop_pub_id' || '<audit_delimiter>' || 'humanhealth_dbxrefprop_id' || '<audit_delimiter>' || 'pub_id';
			audit_vals := NEW.humanhealth_dbxrefprop_pub_id || '<audit_delimiter>' || NEW.humanhealth_dbxrefprop_id || '<audit_delimiter>' || NEW.pub_id;
			INSERT into audit_chado SELECT 'I', now(), user, TG_RELNAME, pkey, ukey_cols, ukey_vals, audit_cols, audit_vals;
			RETURN NEW;

		ELSE
			pkey := OLD.humanhealth_dbxrefprop_pub_id;
			ukey_vals := OLD.humanhealth_dbxrefprop_id || '<audit_delimiter>' || OLD.pub_id;
			ukey_cols := 'humanhealth_dbxrefprop_id' || '<audit_delimiter>' || 'pub_id';
			audit_cols := 'humanhealth_dbxrefprop_pub_id' || '<audit_delimiter>' || 'humanhealth_dbxrefprop_id' || '<audit_delimiter>' || 'pub_id';
			audit_vals := OLD.humanhealth_dbxrefprop_pub_id || '<audit_delimiter>' || OLD.humanhealth_dbxrefprop_id || '<audit_delimiter>' || OLD.pub_id;
			IF TG_OP = 'UPDATE' THEN
				INSERT into audit_chado SELECT 'U', now(), user, TG_RELNAME, pkey, ukey_cols, ukey_vals, audit_cols, audit_vals;
				RETURN OLD;
			END IF;
			IF TG_OP = 'DELETE' THEN
				INSERT into audit_chado SELECT 'D', now(), user, TG_RELNAME, pkey, ukey_cols, ukey_vals, audit_cols, audit_vals;
				RETURN OLD;
			END IF;
		END IF;
	END;
$$;


ALTER FUNCTION public.humanhealth_dbxrefprop_pub_audit() OWNER TO postgres;

--
-- Name: FUNCTION humanhealth_dbxrefprop_pub_audit(); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.humanhealth_dbxrefprop_pub_audit() IS 'This is an automatically generated function for auditing table humanhealth_dbxrefprop_pub.  For each transaction on this table, a record is inserted into table audit_chado reflecting time and type of transaction, user executing transaction, and current column values (for INSERT transactions) or old (pre-change) column values (for UPDATE and DELETE transactions).';


--
-- Name: library_assignname_fn_i(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.library_assignname_fn_i() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  maxid      int;
  maxid_temp int;
  pos        int;
  id         varchar(255);
  maxid_cg   int;
  id_fb      varchar(255);
  message   varchar(255);
  f_row_g library%ROWTYPE;
  f_type  cvterm.name%TYPE;
  f_type_id cvterm.cvterm_id%TYPE;
  letter_t varchar;
  letter_p varchar;
  d_id    db.db_id%TYPE;
  f_dbxref_id dbxref.dbxref_id%TYPE;
  f_dbxref_id_temp dbxref.dbxref_id%TYPE;
  fd_id library_dbxref.library_dbxref_id%TYPE;
  cg_accession dbxref.accession%TYPE;
  d_accession dbxref.accession%TYPE;
  f_uniquename_temp library.uniquename%TYPE;
  f_uniquename library.uniquename%TYPE;
  p_id                 pub.pub_id%TYPE;
  p_type_id            cvterm.cvterm_id%TYPE;
  c_cv_id              cv.cv_id%TYPE;
  f_s_id               feature_synonym.feature_synonym_id%TYPE;
  f_d_id               library_dbxref.library_dbxref_id%TYPE;
  f_type_FBlc   CONSTANT varchar :='cDNA library';
  f_dbname_gadfly CONSTANT varchar :='FlyBase Annotation IDs';
  f_dbname_FB CONSTANT varchar :='FlyBase';
  o_genus  CONSTANT varchar :='Drosophila';
  o_species  CONSTANT varchar:='melanogaster';
  c_name_synonym CONSTANT varchar:='synonym';
  cv_cvname_synonym CONSTANT varchar:='synonym type';
  p_miniref         CONSTANT varchar:='gadfly3';
  p_cvterm_name     CONSTANT varchar:='computer file';
  p_cv_name         CONSTANT varchar:='pub type';
BEGIN
  RAISE NOTICE 'enter lib_i: library.uniquename:%, library.type_id:%', NEW.uniquename, NEW.type_id;
-- here assign new FBlc
  IF ( NEW.uniquename like 'FBlc:temp%') THEN
      SELECT INTO f_type c.name from library f, cvterm c, organism o where f.type_id=c.cvterm_id and f.uniquename=NEW.uniquename and f.organism_id =NEW.organism_id;
      IF f_type is NOT NULL THEN
        RAISE NOTICE 'in library_assignname_fn_i type of this library is:%', f_type;
      END IF;
     
      RAISE NOTICE 'in lib_i, library type is:%', f_type;
      SELECT INTO f_row_g * from library where uniquename=NEW.uniquename and organism_id=NEW.organism_id;
      SELECT INTO maxid max(to_number(substring(accession from 5 for 11), '9999999'))+1 from dbxref dx, db d  where dx.db_id=d.db_id and  d.name=f_dbname_FB and accession like 'FBlc_______';
      IF maxid IS NULL THEN
          maxid:=40;
      END IF;
               RAISE NOTICE 'maxid after is:%', maxid;
               id:=lpad(CAST(maxid as TEXT), 7, '0000000');
               f_uniquename:=CAST('FBlc'||id as TEXT);

               SELECT INTO d_id db_id from db where name= f_dbname_FB;
               IF d_id IS NULL THEN 
                 INSERT INTO db(name) values (f_dbname_FB);
                 SELECT INTO d_id db_id from db where name= f_dbname_FB;
               END IF;
               RAISE NOTICE 'db_id:%, uniquename:%, f_dbname_FB:%:', d_id, f_uniquename, f_dbname_FB; 
               SELECT INTO f_dbxref_id dbxref_id from dbxref where db_id=d_id and accession=f_uniquename;
               IF f_dbxref_id IS NULL THEN 
                 INSERT INTO dbxref (db_id, accession) values(d_id, f_uniquename);
                 SELECT INTO f_dbxref_id dbxref_id from dbxref where db_id=d_id and accession=f_uniquename;
               END IF;
               RAISE NOTICE 'dbxref_id:%', f_dbxref_id;
               RAISE NOTICE 'old uniquename of this feature is:%', f_row_g.uniquename;
               RAISE NOTICE 'new uniquename of this feature is:%', f_uniquename;
               UPDATE library set uniquename=f_uniquename where library_id=f_row_g.library_id;
               select INTO fd_id library_dbxref_id from library_dbxref where library_id=f_row_g.library_id and dbxref_id=f_dbxref_id;
               IF fd_id IS NULL THEN
                  insert into library_dbxref(is_current, library_id, dbxref_id) values ('true',f_row_g.library_id,f_dbxref_id);
              
               END IF;
  END IF;
  RAISE NOTICE 'leave lib_i .......';
  return NEW;    
END;
$$;


ALTER FUNCTION public.library_assignname_fn_i() OWNER TO postgres;

--
-- Name: p(integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.p(integer, integer) RETURNS point
    LANGUAGE sql
    AS $_$SELECT point ($1, $2)$_$;


ALTER FUNCTION public.p(integer, integer) OWNER TO postgres;

--
-- Name: pub_assignname_fn_i(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.pub_assignname_fn_i() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  id         int;
  maxid      int;
  p_row pub%ROWTYPE; 
  p_miniref         CONSTANT varchar:='gadfly3';
  p_uniquename pub.uniquename%TYPE;
  id_db db.db_id%TYPE;
  id_contact contact.contact_id%TYPE;
  id_dbxref dbxref.dbxref_id%TYPE;
  f_dbxref_id feature.dbxref_id%TYPE;
  id_feature_dbxref feature_dbxref.feature_dbxref_id%TYPE;
  pd_id pub_dbxref.pub_dbxref_id%TYPE;
  db_name_FB         CONSTANT varchar:='FlyBase';
  contact_description         CONSTANT varchar:='dummy';
BEGIN
  RAISE NOTICE 'enter pub_i: pub.uniquename:%, pub.type_id:%', NEW.uniquename, NEW.type_id;
  IF (NEW.uniquename like 'FBrf:temp%' or NEW.uniquename like 'multipub:temp%')  THEN
    IF (NEW.uniquename like 'FBrf:temp%') THEN
        SELECT INTO maxid max(to_number(substring(uniquename from 5 for 11), '9999999')) from pub where uniquename like 'FBrf0%';

               RAISE NOTICE 'in pub_i, maxid before is:%', maxid;
               IF maxid IS NULL THEN
                   maxid:=1;
               ELSE
                   maxid:=maxid+1;
               END IF;
               /* here all prefix with FBrf0 instead of FBrf because some special FBrf1234567   */
               id:=lpad(CAST(maxid AS TEXT), 6, '000000');
               p_uniquename:=CAST('FBrf0'||id as TEXT);
               RAISE NOTICE 'new uniquename is:%', p_uniquename;
               UPDATE pub set uniquename=p_uniquename  where pub_id=NEW.pub_id;

               SELECT INTO id_db db_id from db where name= db_name_FB;
               IF id_db IS NULL THEN 
                 INSERT INTO db(name) values (db_name_FB);
                 SELECT INTO id_db db_id from db where name= db_name_FB;
               END IF;
               RAISE NOTICE 'db_id:%, uniquename:%:', id_db, p_uniquename; 
               SELECT INTO f_dbxref_id dbxref_id from dbxref where db_id=id_db and accession=p_uniquename;
               if f_dbxref_id IS NULL THEN 
                 INSERT INTO dbxref (db_id, accession) values(id_db, p_uniquename);
                 SELECT INTO f_dbxref_id dbxref_id from dbxref where db_id=id_db and accession=p_uniquename;
               END IF;

               select INTO pd_id pub_dbxref_id from pub_dbxref where pub_id=NEW.pub_id and dbxref_id=f_dbxref_id;
               IF pd_id IS NULL THEN
                  insert into pub_dbxref(pub_id, dbxref_id) values (NEW.pub_id,f_dbxref_id);
               END IF;

    END IF;

    IF (NEW.uniquename like 'multipub:temp%') THEN
        SELECT INTO maxid max(to_number(substring(uniquename from 10 for 14), '999999')) from pub where uniquename  like 'multipub_%';

               RAISE NOTICE 'in pub_i, maxid before is:%', maxid;
               IF maxid IS NULL THEN
                   maxid:=1;
               ELSE
                   maxid:=maxid+1;
               END IF;
               p_uniquename:=CAST('multipub_'||maxid as TEXT);
               RAISE NOTICE 'new uniquename is:%', p_uniquename;
               UPDATE pub set uniquename=p_uniquename  where pub_id=NEW.pub_id;

               SELECT INTO id_db db_id from db where name= db_name_FB;
               IF id_db IS NULL THEN 
                 INSERT INTO db(name) values (db_name_FB);
                 SELECT INTO id_db db_id from db where name= db_name_FB;
               END IF;
               RAISE NOTICE 'db_id:%, uniquename:%:', id_db, p_uniquename; 
               SELECT INTO f_dbxref_id dbxref_id from dbxref where db_id=id_db and accession=p_uniquename;
               if f_dbxref_id IS NULL THEN 
                 INSERT INTO dbxref (db_id, accession) values(id_db, p_uniquename);
                 SELECT INTO f_dbxref_id dbxref_id from dbxref where db_id=id_db and accession=p_uniquename;
               END IF;
               select INTO pd_id pub_dbxref_id from pub_dbxref where pub_id=NEW.pub_id and dbxref_id=f_dbxref_id;
               IF pd_id IS NULL THEN
                  insert into pub_dbxref(pub_id, dbxref_id) values (NEW.pub_id,f_dbxref_id);
               END IF;
     END IF;

  END IF;
  RAISE NOTICE 'leave pub_i .......';
  return NEW;    
END;
$$;


ALTER FUNCTION public.pub_assignname_fn_i() OWNER TO postgres;

--
-- Name: pubprop_rank_fn_u(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.pubprop_rank_fn_u() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  rank_new    pubprop.rank%TYPE;
  p_cv_name         CONSTANT varchar:='pub type';
BEGIN
  -- here we ensure that any two records with same pub_id/type_id/rank but different value will NOT be overwrite
  IF NEW.pub_id=OLD.pub_id and NEW.type_id=OLD.type_id and NEW.rank=OLD.rank and NEW.value<>OLD.value THEN
     SELECT INTO rank_new max(rank) from pubprop where pub_id=NEW.pub_id and type_id=NEW.type_id;
     rank_new:=rank_new+1;
     RAISE NOTICE 'create a new record to avoid overwrite same pub_id/type_id/rank with diff value. The Old one,old value:%, new value:%',OLD.value, NEW.value;
     insert into pubprop(pub_id, type_id, rank, value) values (OLD.pub_id, OLD.type_id, rank_new, NEW.value);
  END IF;
  -- Triggers fired BEFORE signal the trigger manager to skip the operation for this actual row when returning NULL. 
  -- Otherwise, the returned record/row replaces the inserted/updated row in the operation.
  -- It is possible to replace single values directly in NEW and return that or to build a complete new record/row to return.
  -- Notice here, we INSERT a record so SKIP the update step which fire the trigger
  RETURN NULL;
END;
$$;


ALTER FUNCTION public.pubprop_rank_fn_u() OWNER TO postgres;

--
-- Name: strain_assignname_fn_i(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.strain_assignname_fn_i() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  maxid      int;
  maxid_temp int;
  pos        int;
  id         varchar(255);
  maxid_cg   int;
  id_fb      varchar(255);
  message   varchar(255);
  f_row_g strain%ROWTYPE;
  f_type  cvterm.name%TYPE;
  f_type_id cvterm.cvterm_id%TYPE;
  letter_t varchar;
  letter_p varchar;
  d_id    db.db_id%TYPE;
  f_dbxref_id dbxref.dbxref_id%TYPE;
  f_dbxref_id_temp dbxref.dbxref_id%TYPE;
  fd_id strain_dbxref.strain_dbxref_id%TYPE;
  cg_accession dbxref.accession%TYPE;
  d_accession dbxref.accession%TYPE;
  f_uniquename_temp strain.uniquename%TYPE;
  f_uniquename strain.uniquename%TYPE;
  p_id                 pub.pub_id%TYPE;
  p_type_id            cvterm.cvterm_id%TYPE;
  c_cv_id              cv.cv_id%TYPE;
  f_s_id               strain_synonym.strain_synonym_id%TYPE;
  f_d_id               strain_dbxref.strain_dbxref_id%TYPE;
  f_type_FBlc   CONSTANT varchar :='cDNA library';
  f_dbname_gadfly CONSTANT varchar :='FlyBase Annotation IDs';
  f_dbname_FB CONSTANT varchar :='FlyBase';
  o_genus  CONSTANT varchar :='Drosophila';
  o_species  CONSTANT varchar:='melanogaster';
  c_name_synonym CONSTANT varchar:='synonym';
  cv_cvname_synonym CONSTANT varchar:='synonym type';
  p_miniref         CONSTANT varchar:='gadfly3';
  p_cvterm_name     CONSTANT varchar:='computer file';
  p_cv_name         CONSTANT varchar:='pub type';
BEGIN
  RAISE NOTICE 'enter strain_i: strain.uniquename:%, strain.organism_id:%', NEW.uniquename, NEW.organism_id;
-- here assign new FBsn blah
  IF ( NEW.uniquename like 'FBsn:temp%') THEN
--      SELECT INTO f_type c.name from library f, cvterm c, organism o where f.type_id=c.cvterm_id and f.uniquename=NEW.uniquename and f.organism_id =NEW.organism_id;
--      IF f_type is NOT NULL THEN
--        RAISE NOTICE 'in library_assignname_fn_i type of this library is:%', f_type;
--      END IF;
     
--      RAISE NOTICE 'in lib_i, library type is:%', f_type;
      SELECT INTO f_row_g * from strain where uniquename=NEW.uniquename 
	  and organism_id=NEW.organism_id;
      SELECT INTO maxid max(to_number(substring(uniquename from 5 for 11), '9999999'))+1 from strain where uniquename like 'FBsn_______';
      IF maxid IS NULL THEN
          maxid:=1;
      END IF;
               RAISE NOTICE 'maxid after is:%', maxid;
               id:=lpad(CAST(maxid as TEXT), 7, '0000000');
               f_uniquename:=CAST('FBsn'||id as TEXT);

               SELECT INTO d_id db_id from db where name= f_dbname_FB;
               IF d_id IS NULL THEN 
                 INSERT INTO db(name) values (f_dbname_FB);
                 SELECT INTO d_id db_id from db where name= f_dbname_FB;
               END IF;
               RAISE NOTICE 'db_id:%, uniquename:%, f_dbname_FB:%:', d_id, f_uniquename, f_dbname_FB; 
               SELECT INTO f_dbxref_id dbxref_id from dbxref where db_id=d_id and accession=f_uniquename;
               IF f_dbxref_id IS NULL THEN 
                 INSERT INTO dbxref (db_id, accession) values(d_id, f_uniquename);
                 SELECT INTO f_dbxref_id dbxref_id from dbxref where db_id=d_id and accession=f_uniquename;
               END IF;
               RAISE NOTICE 'dbxref_id:%', f_dbxref_id;
               RAISE NOTICE 'old uniquename of this strain is:%', f_row_g.uniquename;
               RAISE NOTICE 'new uniquename of this strain is:%', f_uniquename;
               UPDATE strain set uniquename=f_uniquename, dbxref_id=f_dbxref_id where strain_id=f_row_g.strain_id;
               select INTO fd_id strain_dbxref_id from strain_dbxref where strain_id=f_row_g.strain_id and dbxref_id=f_dbxref_id;
               IF fd_id IS NULL THEN
                  insert into strain_dbxref(is_current, strain_id, dbxref_id) values ('true',f_row_g.strain_id,f_dbxref_id);
              
               END IF;
  END IF;
  RAISE NOTICE 'leave strain_i .......';
  return NEW;    
END;
$$;


ALTER FUNCTION public.strain_assignname_fn_i() OWNER TO postgres;

--
-- Name: analysisfeature; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.analysisfeature (
    analysisfeature_id integer NOT NULL,
    feature_id integer NOT NULL,
    analysis_id integer NOT NULL,
    rawscore double precision,
    normscore double precision,
    significance double precision,
    identity double precision
);


ALTER TABLE public.analysisfeature OWNER TO postgres;

--
-- Name: cvterm; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cvterm (
    cvterm_id integer NOT NULL,
    cv_id integer NOT NULL,
    definition text,
    dbxref_id integer NOT NULL,
    is_obsolete integer DEFAULT 0 NOT NULL,
    is_relationshiptype integer DEFAULT 0 NOT NULL,
    name character varying(1024) NOT NULL
);


ALTER TABLE public.cvterm OWNER TO postgres;

--
-- Name: af_type; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.af_type AS
 SELECT f.feature_id,
    f.name,
    f.uniquename,
    f.dbxref_id,
    c.name AS type,
    f.residues,
    f.seqlen,
    f.md5checksum,
    f.type_id,
    f.organism_id,
    af.analysis_id,
    f.timeaccessioned,
    f.timelastmodified
   FROM public.feature f,
    public.analysisfeature af,
    public.cvterm c
  WHERE ((f.type_id = c.cvterm_id) AND (f.feature_id = af.feature_id));


ALTER TABLE public.af_type OWNER TO postgres;

--
-- Name: feature_relationship; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feature_relationship (
    feature_relationship_id integer NOT NULL,
    subject_id integer NOT NULL,
    object_id integer NOT NULL,
    type_id integer NOT NULL,
    rank integer DEFAULT 0 NOT NULL,
    value text
);


ALTER TABLE public.feature_relationship OWNER TO postgres;

--
-- Name: alignment_evidence; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.alignment_evidence AS
 SELECT (((((anchor.feature_id)::text || ':'::text) || (fr.object_id)::text) || ':'::text) || (af.analysis_id)::text) AS alignment_evidence_id,
    anchor.feature_id,
    fr.object_id AS evidence_id,
    af.analysis_id
   FROM public.featureloc anchor,
    public.analysisfeature af,
    public.feature_relationship fr,
    public.featureloc hsploc
  WHERE ((anchor.srcfeature_id = hsploc.srcfeature_id) AND (anchor.strand = hsploc.strand) AND (hsploc.feature_id = af.feature_id) AND (hsploc.feature_id = fr.subject_id) AND ((hsploc.fmin <= anchor.fmax) AND (hsploc.fmax >= anchor.fmin)))
  GROUP BY anchor.feature_id, fr.object_id, af.analysis_id;


ALTER TABLE public.alignment_evidence OWNER TO postgres;

--
-- Name: analysis; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.analysis (
    analysis_id integer NOT NULL,
    name character varying(255),
    description text,
    program character varying(255) NOT NULL,
    programversion character varying(255) NOT NULL,
    algorithm character varying(255),
    sourcename character varying(255),
    sourceversion character varying(255),
    sourceuri text,
    timeexecuted timestamp without time zone DEFAULT ('now'::text)::timestamp(6) with time zone NOT NULL
);


ALTER TABLE public.analysis OWNER TO postgres;

--
-- Name: analysis_analysis_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.analysis_analysis_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.analysis_analysis_id_seq OWNER TO postgres;

--
-- Name: analysis_analysis_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.analysis_analysis_id_seq OWNED BY public.analysis.analysis_id;


--
-- Name: analysisfeature_analysisfeature_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.analysisfeature_analysisfeature_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.analysisfeature_analysisfeature_id_seq OWNER TO postgres;

--
-- Name: analysisfeature_analysisfeature_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.analysisfeature_analysisfeature_id_seq OWNED BY public.analysisfeature.analysisfeature_id;


--
-- Name: analysisgrp; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.analysisgrp (
    analysisgrp_id integer NOT NULL,
    rawscore double precision,
    normscore double precision,
    significance double precision,
    identity double precision,
    analysis_id integer NOT NULL,
    grp_id integer NOT NULL
);


ALTER TABLE public.analysisgrp OWNER TO postgres;

--
-- Name: analysisgrp_analysisgrp_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.analysisgrp_analysisgrp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.analysisgrp_analysisgrp_id_seq OWNER TO postgres;

--
-- Name: analysisgrp_analysisgrp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.analysisgrp_analysisgrp_id_seq OWNED BY public.analysisgrp.analysisgrp_id;


--
-- Name: analysisgrpmember; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.analysisgrpmember (
    analysisgrpmember_id integer NOT NULL,
    rawscore double precision,
    normscore double precision,
    significance double precision,
    identity double precision,
    analysis_id integer NOT NULL,
    grpmember_id integer NOT NULL
);


ALTER TABLE public.analysisgrpmember OWNER TO postgres;

--
-- Name: analysisgrpmember_analysisgrpmember_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.analysisgrpmember_analysisgrpmember_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.analysisgrpmember_analysisgrpmember_id_seq OWNER TO postgres;

--
-- Name: analysisgrpmember_analysisgrpmember_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.analysisgrpmember_analysisgrpmember_id_seq OWNED BY public.analysisgrpmember.analysisgrpmember_id;


--
-- Name: analysisprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.analysisprop (
    analysisprop_id integer NOT NULL,
    analysis_id integer NOT NULL,
    type_id integer NOT NULL,
    value text
);


ALTER TABLE public.analysisprop OWNER TO postgres;

--
-- Name: analysisprop_analysisprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.analysisprop_analysisprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.analysisprop_analysisprop_id_seq OWNER TO postgres;

--
-- Name: analysisprop_analysisprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.analysisprop_analysisprop_id_seq OWNED BY public.analysisprop.analysisprop_id;


--
-- Name: cell_line; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cell_line (
    cell_line_id integer NOT NULL,
    name character varying(255),
    uniquename character varying(255) NOT NULL,
    organism_id integer NOT NULL,
    timeaccessioned timestamp without time zone DEFAULT now() NOT NULL,
    timelastmodified timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.cell_line OWNER TO postgres;

--
-- Name: cell_line_cell_line_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cell_line_cell_line_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cell_line_cell_line_id_seq OWNER TO postgres;

--
-- Name: cell_line_cell_line_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cell_line_cell_line_id_seq OWNED BY public.cell_line.cell_line_id;


--
-- Name: cell_line_cvterm; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cell_line_cvterm (
    cell_line_cvterm_id integer NOT NULL,
    cell_line_id integer NOT NULL,
    cvterm_id integer NOT NULL,
    pub_id integer NOT NULL,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.cell_line_cvterm OWNER TO postgres;

--
-- Name: cell_line_cvterm_cell_line_cvterm_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cell_line_cvterm_cell_line_cvterm_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cell_line_cvterm_cell_line_cvterm_id_seq OWNER TO postgres;

--
-- Name: cell_line_cvterm_cell_line_cvterm_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cell_line_cvterm_cell_line_cvterm_id_seq OWNED BY public.cell_line_cvterm.cell_line_cvterm_id;


--
-- Name: cell_line_cvtermprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cell_line_cvtermprop (
    cell_line_cvtermprop_id integer NOT NULL,
    cell_line_cvterm_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.cell_line_cvtermprop OWNER TO postgres;

--
-- Name: cell_line_cvtermprop_cell_line_cvtermprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cell_line_cvtermprop_cell_line_cvtermprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cell_line_cvtermprop_cell_line_cvtermprop_id_seq OWNER TO postgres;

--
-- Name: cell_line_cvtermprop_cell_line_cvtermprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cell_line_cvtermprop_cell_line_cvtermprop_id_seq OWNED BY public.cell_line_cvtermprop.cell_line_cvtermprop_id;


--
-- Name: cell_line_dbxref; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cell_line_dbxref (
    cell_line_dbxref_id integer NOT NULL,
    cell_line_id integer NOT NULL,
    dbxref_id integer NOT NULL,
    is_current boolean DEFAULT true NOT NULL
);


ALTER TABLE public.cell_line_dbxref OWNER TO postgres;

--
-- Name: cell_line_dbxref_cell_line_dbxref_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cell_line_dbxref_cell_line_dbxref_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cell_line_dbxref_cell_line_dbxref_id_seq OWNER TO postgres;

--
-- Name: cell_line_dbxref_cell_line_dbxref_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cell_line_dbxref_cell_line_dbxref_id_seq OWNED BY public.cell_line_dbxref.cell_line_dbxref_id;


--
-- Name: cell_line_feature; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cell_line_feature (
    cell_line_feature_id integer NOT NULL,
    cell_line_id integer NOT NULL,
    feature_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.cell_line_feature OWNER TO postgres;

--
-- Name: cell_line_feature_cell_line_feature_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cell_line_feature_cell_line_feature_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cell_line_feature_cell_line_feature_id_seq OWNER TO postgres;

--
-- Name: cell_line_feature_cell_line_feature_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cell_line_feature_cell_line_feature_id_seq OWNED BY public.cell_line_feature.cell_line_feature_id;


--
-- Name: cell_line_library; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cell_line_library (
    cell_line_library_id integer NOT NULL,
    cell_line_id integer NOT NULL,
    library_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.cell_line_library OWNER TO postgres;

--
-- Name: cell_line_library_cell_line_library_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cell_line_library_cell_line_library_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cell_line_library_cell_line_library_id_seq OWNER TO postgres;

--
-- Name: cell_line_library_cell_line_library_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cell_line_library_cell_line_library_id_seq OWNED BY public.cell_line_library.cell_line_library_id;


--
-- Name: cell_line_libraryprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cell_line_libraryprop (
    cell_line_libraryprop_id integer NOT NULL,
    cell_line_library_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.cell_line_libraryprop OWNER TO postgres;

--
-- Name: TABLE cell_line_libraryprop; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.cell_line_libraryprop IS 'Attributes of a cell_line_library relationship.  Eg, a comment';


--
-- Name: cell_line_libraryprop_cell_line_libraryprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cell_line_libraryprop_cell_line_libraryprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cell_line_libraryprop_cell_line_libraryprop_id_seq OWNER TO postgres;

--
-- Name: cell_line_libraryprop_cell_line_libraryprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cell_line_libraryprop_cell_line_libraryprop_id_seq OWNED BY public.cell_line_libraryprop.cell_line_libraryprop_id;


--
-- Name: cell_line_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cell_line_pub (
    cell_line_pub_id integer NOT NULL,
    cell_line_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.cell_line_pub OWNER TO postgres;

--
-- Name: cell_line_pub_cell_line_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cell_line_pub_cell_line_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cell_line_pub_cell_line_pub_id_seq OWNER TO postgres;

--
-- Name: cell_line_pub_cell_line_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cell_line_pub_cell_line_pub_id_seq OWNED BY public.cell_line_pub.cell_line_pub_id;


--
-- Name: cell_line_relationship; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cell_line_relationship (
    cell_line_relationship_id integer NOT NULL,
    subject_id integer NOT NULL,
    object_id integer NOT NULL,
    type_id integer NOT NULL
);


ALTER TABLE public.cell_line_relationship OWNER TO postgres;

--
-- Name: cell_line_relationship_cell_line_relationship_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cell_line_relationship_cell_line_relationship_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cell_line_relationship_cell_line_relationship_id_seq OWNER TO postgres;

--
-- Name: cell_line_relationship_cell_line_relationship_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cell_line_relationship_cell_line_relationship_id_seq OWNED BY public.cell_line_relationship.cell_line_relationship_id;


--
-- Name: cell_line_strain; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cell_line_strain (
    cell_line_strain_id integer NOT NULL,
    strain_id integer NOT NULL,
    cell_line_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.cell_line_strain OWNER TO postgres;

--
-- Name: TABLE cell_line_strain; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.cell_line_strain IS 'cell_line_strain links a strain to cell_lines associated with the strain/pub.';


--
-- Name: cell_line_strain_cell_line_strain_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cell_line_strain_cell_line_strain_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cell_line_strain_cell_line_strain_id_seq OWNER TO postgres;

--
-- Name: cell_line_strain_cell_line_strain_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cell_line_strain_cell_line_strain_id_seq OWNED BY public.cell_line_strain.cell_line_strain_id;


--
-- Name: cell_line_strainprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cell_line_strainprop (
    cell_line_strainprop_id integer NOT NULL,
    cell_line_strain_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.cell_line_strainprop OWNER TO postgres;

--
-- Name: TABLE cell_line_strainprop; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.cell_line_strainprop IS 'Attributes of a cell_line_strain relationship.  Eg, a comment';


--
-- Name: cell_line_strainprop_cell_line_strainprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cell_line_strainprop_cell_line_strainprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cell_line_strainprop_cell_line_strainprop_id_seq OWNER TO postgres;

--
-- Name: cell_line_strainprop_cell_line_strainprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cell_line_strainprop_cell_line_strainprop_id_seq OWNED BY public.cell_line_strainprop.cell_line_strainprop_id;


--
-- Name: cell_line_synonym; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cell_line_synonym (
    cell_line_synonym_id integer NOT NULL,
    cell_line_id integer NOT NULL,
    synonym_id integer NOT NULL,
    pub_id integer NOT NULL,
    is_current boolean DEFAULT false NOT NULL,
    is_internal boolean DEFAULT false NOT NULL
);


ALTER TABLE public.cell_line_synonym OWNER TO postgres;

--
-- Name: cell_line_synonym_cell_line_synonym_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cell_line_synonym_cell_line_synonym_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cell_line_synonym_cell_line_synonym_id_seq OWNER TO postgres;

--
-- Name: cell_line_synonym_cell_line_synonym_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cell_line_synonym_cell_line_synonym_id_seq OWNED BY public.cell_line_synonym.cell_line_synonym_id;


--
-- Name: cell_lineprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cell_lineprop (
    cell_lineprop_id integer NOT NULL,
    cell_line_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.cell_lineprop OWNER TO postgres;

--
-- Name: cell_lineprop_cell_lineprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cell_lineprop_cell_lineprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cell_lineprop_cell_lineprop_id_seq OWNER TO postgres;

--
-- Name: cell_lineprop_cell_lineprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cell_lineprop_cell_lineprop_id_seq OWNED BY public.cell_lineprop.cell_lineprop_id;


--
-- Name: cell_lineprop_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cell_lineprop_pub (
    cell_lineprop_pub_id integer NOT NULL,
    cell_lineprop_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.cell_lineprop_pub OWNER TO postgres;

--
-- Name: cell_lineprop_pub_cell_lineprop_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cell_lineprop_pub_cell_lineprop_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cell_lineprop_pub_cell_lineprop_pub_id_seq OWNER TO postgres;

--
-- Name: cell_lineprop_pub_cell_lineprop_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cell_lineprop_pub_cell_lineprop_pub_id_seq OWNED BY public.cell_lineprop_pub.cell_lineprop_pub_id;


--
-- Name: contact; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.contact (
    contact_id integer NOT NULL,
    description character varying(255),
    name character varying(30) NOT NULL
);


ALTER TABLE public.contact OWNER TO postgres;

--
-- Name: contact_contact_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.contact_contact_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.contact_contact_id_seq OWNER TO postgres;

--
-- Name: contact_contact_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.contact_contact_id_seq OWNED BY public.contact.contact_id;


--
-- Name: cv; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cv (
    cv_id integer NOT NULL,
    name character varying(255) NOT NULL,
    definition text
);


ALTER TABLE public.cv OWNER TO postgres;

--
-- Name: cv_cv_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cv_cv_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cv_cv_id_seq OWNER TO postgres;

--
-- Name: cv_cv_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cv_cv_id_seq OWNED BY public.cv.cv_id;


--
-- Name: cvterm_cvterm_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cvterm_cvterm_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cvterm_cvterm_id_seq OWNER TO postgres;

--
-- Name: cvterm_cvterm_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cvterm_cvterm_id_seq OWNED BY public.cvterm.cvterm_id;


--
-- Name: cvterm_dbxref; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cvterm_dbxref (
    cvterm_dbxref_id integer NOT NULL,
    cvterm_id integer NOT NULL,
    dbxref_id integer NOT NULL,
    is_for_definition integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.cvterm_dbxref OWNER TO postgres;

--
-- Name: cvterm_dbxref_cvterm_dbxref_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cvterm_dbxref_cvterm_dbxref_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cvterm_dbxref_cvterm_dbxref_id_seq OWNER TO postgres;

--
-- Name: cvterm_dbxref_cvterm_dbxref_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cvterm_dbxref_cvterm_dbxref_id_seq OWNED BY public.cvterm_dbxref.cvterm_dbxref_id;


--
-- Name: cvterm_relationship; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cvterm_relationship (
    cvterm_relationship_id integer NOT NULL,
    type_id integer NOT NULL,
    subject_id integer NOT NULL,
    object_id integer NOT NULL
);


ALTER TABLE public.cvterm_relationship OWNER TO postgres;

--
-- Name: cvterm_relationship_cvterm_relationship_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cvterm_relationship_cvterm_relationship_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cvterm_relationship_cvterm_relationship_id_seq OWNER TO postgres;

--
-- Name: cvterm_relationship_cvterm_relationship_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cvterm_relationship_cvterm_relationship_id_seq OWNED BY public.cvterm_relationship.cvterm_relationship_id;


--
-- Name: cvterm_type; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.cvterm_type AS
 SELECT cvt.cvterm_id,
    cvt.name,
    cv.name AS termtype
   FROM public.cvterm cvt,
    public.cv
  WHERE (cvt.cv_id = cv.cv_id);


ALTER TABLE public.cvterm_type OWNER TO postgres;

--
-- Name: cvtermpath; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cvtermpath (
    cvtermpath_id integer NOT NULL,
    type_id integer,
    subject_id integer NOT NULL,
    object_id integer NOT NULL,
    cv_id integer NOT NULL,
    pathdistance integer
);


ALTER TABLE public.cvtermpath OWNER TO postgres;

--
-- Name: cvtermpath_cvtermpath_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cvtermpath_cvtermpath_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cvtermpath_cvtermpath_id_seq OWNER TO postgres;

--
-- Name: cvtermpath_cvtermpath_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cvtermpath_cvtermpath_id_seq OWNED BY public.cvtermpath.cvtermpath_id;


--
-- Name: cvtermprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cvtermprop (
    cvtermprop_id integer NOT NULL,
    cvterm_id integer NOT NULL,
    type_id integer NOT NULL,
    value text DEFAULT ''::text NOT NULL,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.cvtermprop OWNER TO postgres;

--
-- Name: cvtermprop_cvtermprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cvtermprop_cvtermprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cvtermprop_cvtermprop_id_seq OWNER TO postgres;

--
-- Name: cvtermprop_cvtermprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cvtermprop_cvtermprop_id_seq OWNED BY public.cvtermprop.cvtermprop_id;


--
-- Name: cvtermsynonym; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cvtermsynonym (
    cvtermsynonym_id integer NOT NULL,
    cvterm_id integer NOT NULL,
    name character varying(1024) NOT NULL,
    type_id integer
);


ALTER TABLE public.cvtermsynonym OWNER TO postgres;

--
-- Name: cvtermsynonym_cvtermsynonym_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cvtermsynonym_cvtermsynonym_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cvtermsynonym_cvtermsynonym_id_seq OWNER TO postgres;

--
-- Name: cvtermsynonym_cvtermsynonym_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cvtermsynonym_cvtermsynonym_id_seq OWNED BY public.cvtermsynonym.cvtermsynonym_id;


--
-- Name: db; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.db (
    db_id integer NOT NULL,
    name character varying(255) NOT NULL,
    contact_id integer,
    description character varying(255),
    urlprefix character varying(255),
    url character varying(255)
);


ALTER TABLE public.db OWNER TO postgres;

--
-- Name: db_db_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.db_db_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.db_db_id_seq OWNER TO postgres;

--
-- Name: db_db_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.db_db_id_seq OWNED BY public.db.db_id;


--
-- Name: dbxref; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dbxref (
    dbxref_id integer NOT NULL,
    db_id integer NOT NULL,
    accession character varying(255) NOT NULL,
    version character varying(255) DEFAULT ''::character varying NOT NULL,
    description text,
    url character varying(255)
);


ALTER TABLE public.dbxref OWNER TO postgres;

--
-- Name: dbxref_dbxref_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dbxref_dbxref_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dbxref_dbxref_id_seq OWNER TO postgres;

--
-- Name: dbxref_dbxref_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dbxref_dbxref_id_seq OWNED BY public.dbxref.dbxref_id;


--
-- Name: dbxrefprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dbxrefprop (
    dbxrefprop_id integer NOT NULL,
    dbxref_id integer NOT NULL,
    type_id integer NOT NULL,
    value text DEFAULT ''::text NOT NULL,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.dbxrefprop OWNER TO postgres;

--
-- Name: dbxrefprop_dbxrefprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dbxrefprop_dbxrefprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dbxrefprop_dbxrefprop_id_seq OWNER TO postgres;

--
-- Name: dbxrefprop_dbxrefprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dbxrefprop_dbxrefprop_id_seq OWNED BY public.dbxrefprop.dbxrefprop_id;


--
-- Name: eimage; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.eimage (
    eimage_id integer NOT NULL,
    eimage_data text,
    eimage_type character varying(255) NOT NULL,
    image_uri character varying(255)
);


ALTER TABLE public.eimage OWNER TO postgres;

--
-- Name: eimage_eimage_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.eimage_eimage_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.eimage_eimage_id_seq OWNER TO postgres;

--
-- Name: eimage_eimage_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.eimage_eimage_id_seq OWNED BY public.eimage.eimage_id;


--
-- Name: environment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.environment (
    environment_id integer NOT NULL,
    uniquename text NOT NULL,
    description text
);


ALTER TABLE public.environment OWNER TO postgres;

--
-- Name: environment_cvterm; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.environment_cvterm (
    environment_cvterm_id integer NOT NULL,
    environment_id integer NOT NULL,
    cvterm_id integer NOT NULL
);


ALTER TABLE public.environment_cvterm OWNER TO postgres;

--
-- Name: environment_cvterm_environment_cvterm_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.environment_cvterm_environment_cvterm_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.environment_cvterm_environment_cvterm_id_seq OWNER TO postgres;

--
-- Name: environment_cvterm_environment_cvterm_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.environment_cvterm_environment_cvterm_id_seq OWNED BY public.environment_cvterm.environment_cvterm_id;


--
-- Name: environment_environment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.environment_environment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.environment_environment_id_seq OWNER TO postgres;

--
-- Name: environment_environment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.environment_environment_id_seq OWNED BY public.environment.environment_id;


--
-- Name: expression; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expression (
    expression_id integer NOT NULL,
    uniquename text NOT NULL,
    md5checksum character(32),
    description text
);


ALTER TABLE public.expression OWNER TO postgres;

--
-- Name: expression_cvterm; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expression_cvterm (
    expression_cvterm_id integer NOT NULL,
    expression_id integer NOT NULL,
    cvterm_id integer NOT NULL,
    rank integer DEFAULT 0 NOT NULL,
    cvterm_type_id integer NOT NULL
);


ALTER TABLE public.expression_cvterm OWNER TO postgres;

--
-- Name: expression_cvterm_expression_cvterm_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.expression_cvterm_expression_cvterm_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.expression_cvterm_expression_cvterm_id_seq OWNER TO postgres;

--
-- Name: expression_cvterm_expression_cvterm_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.expression_cvterm_expression_cvterm_id_seq OWNED BY public.expression_cvterm.expression_cvterm_id;


--
-- Name: expression_cvtermprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expression_cvtermprop (
    expression_cvtermprop_id integer NOT NULL,
    expression_cvterm_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.expression_cvtermprop OWNER TO postgres;

--
-- Name: TABLE expression_cvtermprop; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.expression_cvtermprop IS 'Extensible properties for
expression to cvterm associations. Examples: qualifiers';


--
-- Name: COLUMN expression_cvtermprop.type_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.expression_cvtermprop.type_id IS 'The name of the
property/slot is a cvterm. The meaning of the property is defined in
that cvterm. cvterms may come from the FlyBase miscellaneous cv';


--
-- Name: COLUMN expression_cvtermprop.value; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.expression_cvtermprop.value IS 'The value of the
property, represented as text. Numeric values are converted to their
text representation. This is less efficient than using native database
types, but is easier to query.';


--
-- Name: COLUMN expression_cvtermprop.rank; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.expression_cvtermprop.rank IS 'Property-Value
ordering. Any expression_cvterm can have multiple values for any particular
property type - these are ordered in a list using rank, counting from
zero. For properties that are single-valued rather than multi-valued,
the default 0 value should be used';


--
-- Name: expression_cvtermprop_expression_cvtermprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.expression_cvtermprop_expression_cvtermprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.expression_cvtermprop_expression_cvtermprop_id_seq OWNER TO postgres;

--
-- Name: expression_cvtermprop_expression_cvtermprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.expression_cvtermprop_expression_cvtermprop_id_seq OWNED BY public.expression_cvtermprop.expression_cvtermprop_id;


--
-- Name: expression_expression_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.expression_expression_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.expression_expression_id_seq OWNER TO postgres;

--
-- Name: expression_expression_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.expression_expression_id_seq OWNED BY public.expression.expression_id;


--
-- Name: expression_image; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expression_image (
    expression_image_id integer NOT NULL,
    expression_id integer NOT NULL,
    eimage_id integer NOT NULL
);


ALTER TABLE public.expression_image OWNER TO postgres;

--
-- Name: expression_image_expression_image_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.expression_image_expression_image_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.expression_image_expression_image_id_seq OWNER TO postgres;

--
-- Name: expression_image_expression_image_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.expression_image_expression_image_id_seq OWNED BY public.expression_image.expression_image_id;


--
-- Name: expression_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expression_pub (
    expression_pub_id integer NOT NULL,
    expression_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.expression_pub OWNER TO postgres;

--
-- Name: expression_pub_expression_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.expression_pub_expression_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.expression_pub_expression_pub_id_seq OWNER TO postgres;

--
-- Name: expression_pub_expression_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.expression_pub_expression_pub_id_seq OWNED BY public.expression_pub.expression_pub_id;


--
-- Name: expressionprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expressionprop (
    expressionprop_id integer NOT NULL,
    expression_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.expressionprop OWNER TO postgres;

--
-- Name: expressionprop_expressionprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.expressionprop_expressionprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.expressionprop_expressionprop_id_seq OWNER TO postgres;

--
-- Name: expressionprop_expressionprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.expressionprop_expressionprop_id_seq OWNED BY public.expressionprop.expressionprop_id;


--
-- Name: f_type; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.f_type AS
 SELECT f.feature_id,
    f.name,
    f.uniquename,
    f.dbxref_id,
    c.name AS type,
    f.residues,
    f.seqlen,
    f.md5checksum,
    f.type_id,
    f.organism_id,
    f.is_analysis,
    f.timeaccessioned,
    f.timelastmodified
   FROM public.feature f,
    public.cvterm c
  WHERE (f.type_id = c.cvterm_id);


ALTER TABLE public.f_type OWNER TO postgres;

--
-- Name: f_loc; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.f_loc AS
 SELECT f.feature_id,
    f.name,
    f.dbxref_id,
    fl.fmin,
    fl.fmax,
    fl.strand
   FROM public.featureloc fl,
    public.f_type f
  WHERE (f.feature_id = fl.feature_id);


ALTER TABLE public.f_loc OWNER TO postgres;

--
-- Name: feature_cvterm; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feature_cvterm (
    feature_cvterm_id integer NOT NULL,
    feature_id integer NOT NULL,
    cvterm_id integer NOT NULL,
    pub_id integer NOT NULL,
    is_not boolean DEFAULT false NOT NULL
);


ALTER TABLE public.feature_cvterm OWNER TO postgres;

--
-- Name: feature_cvterm_dbxref; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feature_cvterm_dbxref (
    feature_cvterm_dbxref_id integer NOT NULL,
    feature_cvterm_id integer NOT NULL,
    dbxref_id integer NOT NULL
);


ALTER TABLE public.feature_cvterm_dbxref OWNER TO postgres;

--
-- Name: TABLE feature_cvterm_dbxref; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.feature_cvterm_dbxref IS 'Additional dbxrefs for an association. Rows in the feature_cvterm table may be backed up by dbxrefs. For example, a feature_cvterm association that was inferred via a protein-protein interaction may be backed by by refering to the dbxref for the alternate protein. Corresponds to the WITH column in a GO gene association file (but can also be used for other analagous associations). See http://www.geneontology.org/doc/GO.annotation.shtml#file for more details';


--
-- Name: feature_cvterm_dbxref_feature_cvterm_dbxref_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feature_cvterm_dbxref_feature_cvterm_dbxref_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feature_cvterm_dbxref_feature_cvterm_dbxref_id_seq OWNER TO postgres;

--
-- Name: feature_cvterm_dbxref_feature_cvterm_dbxref_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feature_cvterm_dbxref_feature_cvterm_dbxref_id_seq OWNED BY public.feature_cvterm_dbxref.feature_cvterm_dbxref_id;


--
-- Name: feature_cvterm_feature_cvterm_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feature_cvterm_feature_cvterm_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feature_cvterm_feature_cvterm_id_seq OWNER TO postgres;

--
-- Name: feature_cvterm_feature_cvterm_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feature_cvterm_feature_cvterm_id_seq OWNED BY public.feature_cvterm.feature_cvterm_id;


--
-- Name: feature_cvtermprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feature_cvtermprop (
    feature_cvtermprop_id integer NOT NULL,
    feature_cvterm_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.feature_cvtermprop OWNER TO postgres;

--
-- Name: feature_cvtermprop_feature_cvtermprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feature_cvtermprop_feature_cvtermprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feature_cvtermprop_feature_cvtermprop_id_seq OWNER TO postgres;

--
-- Name: feature_cvtermprop_feature_cvtermprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feature_cvtermprop_feature_cvtermprop_id_seq OWNED BY public.feature_cvtermprop.feature_cvtermprop_id;


--
-- Name: feature_dbxref; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feature_dbxref (
    feature_dbxref_id integer NOT NULL,
    feature_id integer NOT NULL,
    dbxref_id integer NOT NULL,
    is_current boolean DEFAULT true NOT NULL
);


ALTER TABLE public.feature_dbxref OWNER TO postgres;

--
-- Name: feature_dbxref_feature_dbxref_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feature_dbxref_feature_dbxref_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feature_dbxref_feature_dbxref_id_seq OWNER TO postgres;

--
-- Name: feature_dbxref_feature_dbxref_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feature_dbxref_feature_dbxref_id_seq OWNED BY public.feature_dbxref.feature_dbxref_id;


--
-- Name: feature_expression; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feature_expression (
    feature_expression_id integer NOT NULL,
    expression_id integer NOT NULL,
    feature_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.feature_expression OWNER TO postgres;

--
-- Name: feature_expression_feature_expression_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feature_expression_feature_expression_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feature_expression_feature_expression_id_seq OWNER TO postgres;

--
-- Name: feature_expression_feature_expression_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feature_expression_feature_expression_id_seq OWNED BY public.feature_expression.feature_expression_id;


--
-- Name: feature_expressionprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feature_expressionprop (
    feature_expressionprop_id integer NOT NULL,
    feature_expression_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.feature_expressionprop OWNER TO postgres;

--
-- Name: TABLE feature_expressionprop; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.feature_expressionprop IS 'Extensible properties for
	feature_expression text. Examples: comments';


--
-- Name: feature_expressionprop_feature_expressionprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feature_expressionprop_feature_expressionprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feature_expressionprop_feature_expressionprop_id_seq OWNER TO postgres;

--
-- Name: feature_expressionprop_feature_expressionprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feature_expressionprop_feature_expressionprop_id_seq OWNED BY public.feature_expressionprop.feature_expressionprop_id;


--
-- Name: feature_feature_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feature_feature_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feature_feature_id_seq OWNER TO postgres;

--
-- Name: feature_feature_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feature_feature_id_seq OWNED BY public.feature.feature_id;


--
-- Name: feature_genotype; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feature_genotype (
    feature_genotype_id integer NOT NULL,
    feature_id integer NOT NULL,
    genotype_id integer NOT NULL,
    chromosome_id integer,
    rank integer NOT NULL,
    cgroup integer NOT NULL,
    cvterm_id integer NOT NULL
);


ALTER TABLE public.feature_genotype OWNER TO postgres;

--
-- Name: feature_genotype_feature_genotype_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feature_genotype_feature_genotype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feature_genotype_feature_genotype_id_seq OWNER TO postgres;

--
-- Name: feature_genotype_feature_genotype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feature_genotype_feature_genotype_id_seq OWNED BY public.feature_genotype.feature_genotype_id;


--
-- Name: feature_grpmember; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feature_grpmember (
    feature_grpmember_id integer NOT NULL,
    grpmember_id integer NOT NULL,
    feature_id integer NOT NULL
);


ALTER TABLE public.feature_grpmember OWNER TO postgres;

--
-- Name: feature_grpmember_feature_grpmember_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feature_grpmember_feature_grpmember_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feature_grpmember_feature_grpmember_id_seq OWNER TO postgres;

--
-- Name: feature_grpmember_feature_grpmember_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feature_grpmember_feature_grpmember_id_seq OWNED BY public.feature_grpmember.feature_grpmember_id;


--
-- Name: feature_grpmember_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feature_grpmember_pub (
    feature_grpmember_pub_id integer NOT NULL,
    pub_id integer NOT NULL,
    feature_grpmember_id integer NOT NULL
);


ALTER TABLE public.feature_grpmember_pub OWNER TO postgres;

--
-- Name: feature_grpmember_pub_feature_grpmember_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feature_grpmember_pub_feature_grpmember_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feature_grpmember_pub_feature_grpmember_pub_id_seq OWNER TO postgres;

--
-- Name: feature_grpmember_pub_feature_grpmember_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feature_grpmember_pub_feature_grpmember_pub_id_seq OWNED BY public.feature_grpmember_pub.feature_grpmember_pub_id;


--
-- Name: feature_humanhealth_dbxref; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feature_humanhealth_dbxref (
    feature_humanhealth_dbxref_id integer NOT NULL,
    humanhealth_dbxref_id integer NOT NULL,
    feature_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.feature_humanhealth_dbxref OWNER TO postgres;

--
-- Name: TABLE feature_humanhealth_dbxref; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.feature_humanhealth_dbxref IS 'feature_humanhealth_dbxref links a humanhealth_dbxref to features associated with the humanhealth_dbxref. For example linking human_health record and HGNC accession with orthologous Dmel gene(s)';


--
-- Name: feature_humanhealth_dbxref_feature_humanhealth_dbxref_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feature_humanhealth_dbxref_feature_humanhealth_dbxref_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feature_humanhealth_dbxref_feature_humanhealth_dbxref_id_seq OWNER TO postgres;

--
-- Name: feature_humanhealth_dbxref_feature_humanhealth_dbxref_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feature_humanhealth_dbxref_feature_humanhealth_dbxref_id_seq OWNED BY public.feature_humanhealth_dbxref.feature_humanhealth_dbxref_id;


--
-- Name: feature_interaction; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feature_interaction (
    feature_interaction_id integer NOT NULL,
    feature_id integer NOT NULL,
    interaction_id integer NOT NULL,
    role_id integer NOT NULL,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.feature_interaction OWNER TO postgres;

--
-- Name: feature_interaction_feature_interaction_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feature_interaction_feature_interaction_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feature_interaction_feature_interaction_id_seq OWNER TO postgres;

--
-- Name: feature_interaction_feature_interaction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feature_interaction_feature_interaction_id_seq OWNED BY public.feature_interaction.feature_interaction_id;


--
-- Name: feature_interaction_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feature_interaction_pub (
    feature_interaction_pub_id integer NOT NULL,
    feature_interaction_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.feature_interaction_pub OWNER TO postgres;

--
-- Name: feature_interaction_pub_feature_interaction_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feature_interaction_pub_feature_interaction_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feature_interaction_pub_feature_interaction_pub_id_seq OWNER TO postgres;

--
-- Name: feature_interaction_pub_feature_interaction_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feature_interaction_pub_feature_interaction_pub_id_seq OWNED BY public.feature_interaction_pub.feature_interaction_pub_id;


--
-- Name: feature_interactionprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feature_interactionprop (
    feature_interactionprop_id integer NOT NULL,
    feature_interaction_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.feature_interactionprop OWNER TO postgres;

--
-- Name: feature_interactionprop_feature_interactionprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feature_interactionprop_feature_interactionprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feature_interactionprop_feature_interactionprop_id_seq OWNER TO postgres;

--
-- Name: feature_interactionprop_feature_interactionprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feature_interactionprop_feature_interactionprop_id_seq OWNED BY public.feature_interactionprop.feature_interactionprop_id;


--
-- Name: feature_phenotype; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feature_phenotype (
    feature_phenotype_id integer NOT NULL,
    feature_id integer NOT NULL,
    phenotype_id integer NOT NULL
);


ALTER TABLE public.feature_phenotype OWNER TO postgres;

--
-- Name: feature_phenotype_feature_phenotype_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feature_phenotype_feature_phenotype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feature_phenotype_feature_phenotype_id_seq OWNER TO postgres;

--
-- Name: feature_phenotype_feature_phenotype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feature_phenotype_feature_phenotype_id_seq OWNED BY public.feature_phenotype.feature_phenotype_id;


--
-- Name: feature_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feature_pub (
    feature_pub_id integer NOT NULL,
    feature_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.feature_pub OWNER TO postgres;

--
-- Name: feature_pub_feature_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feature_pub_feature_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feature_pub_feature_pub_id_seq OWNER TO postgres;

--
-- Name: feature_pub_feature_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feature_pub_feature_pub_id_seq OWNED BY public.feature_pub.feature_pub_id;


--
-- Name: feature_pubprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feature_pubprop (
    feature_pubprop_id integer NOT NULL,
    feature_pub_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.feature_pubprop OWNER TO postgres;

--
-- Name: TABLE feature_pubprop; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.feature_pubprop IS 'Property or attribute of a feature_pub link';


--
-- Name: feature_pubprop_feature_pubprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feature_pubprop_feature_pubprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feature_pubprop_feature_pubprop_id_seq OWNER TO postgres;

--
-- Name: feature_pubprop_feature_pubprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feature_pubprop_feature_pubprop_id_seq OWNED BY public.feature_pubprop.feature_pubprop_id;


--
-- Name: feature_relationship_feature_relationship_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feature_relationship_feature_relationship_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feature_relationship_feature_relationship_id_seq OWNER TO postgres;

--
-- Name: feature_relationship_feature_relationship_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feature_relationship_feature_relationship_id_seq OWNED BY public.feature_relationship.feature_relationship_id;


--
-- Name: feature_relationship_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feature_relationship_pub (
    feature_relationship_pub_id integer NOT NULL,
    feature_relationship_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.feature_relationship_pub OWNER TO postgres;

--
-- Name: feature_relationship_pub_feature_relationship_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feature_relationship_pub_feature_relationship_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feature_relationship_pub_feature_relationship_pub_id_seq OWNER TO postgres;

--
-- Name: feature_relationship_pub_feature_relationship_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feature_relationship_pub_feature_relationship_pub_id_seq OWNED BY public.feature_relationship_pub.feature_relationship_pub_id;


--
-- Name: feature_relationshipprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feature_relationshipprop (
    feature_relationshipprop_id integer NOT NULL,
    feature_relationship_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.feature_relationshipprop OWNER TO postgres;

--
-- Name: feature_relationshipprop_feature_relationshipprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feature_relationshipprop_feature_relationshipprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feature_relationshipprop_feature_relationshipprop_id_seq OWNER TO postgres;

--
-- Name: feature_relationshipprop_feature_relationshipprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feature_relationshipprop_feature_relationshipprop_id_seq OWNED BY public.feature_relationshipprop.feature_relationshipprop_id;


--
-- Name: feature_relationshipprop_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feature_relationshipprop_pub (
    feature_relationshipprop_pub_id integer NOT NULL,
    feature_relationshipprop_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.feature_relationshipprop_pub OWNER TO postgres;

--
-- Name: feature_relationshipprop_pub_feature_relationshipprop_pub_i_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feature_relationshipprop_pub_feature_relationshipprop_pub_i_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feature_relationshipprop_pub_feature_relationshipprop_pub_i_seq OWNER TO postgres;

--
-- Name: feature_relationshipprop_pub_feature_relationshipprop_pub_i_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feature_relationshipprop_pub_feature_relationshipprop_pub_i_seq OWNED BY public.feature_relationshipprop_pub.feature_relationshipprop_pub_id;


--
-- Name: feature_synonym; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feature_synonym (
    feature_synonym_id integer NOT NULL,
    synonym_id integer NOT NULL,
    feature_id integer NOT NULL,
    pub_id integer NOT NULL,
    is_current boolean DEFAULT true NOT NULL,
    is_internal boolean DEFAULT false NOT NULL
);


ALTER TABLE public.feature_synonym OWNER TO postgres;

--
-- Name: feature_synonym_feature_synonym_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feature_synonym_feature_synonym_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feature_synonym_feature_synonym_id_seq OWNER TO postgres;

--
-- Name: feature_synonym_feature_synonym_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feature_synonym_feature_synonym_id_seq OWNED BY public.feature_synonym.feature_synonym_id;


--
-- Name: feature_uniquename_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feature_uniquename_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feature_uniquename_seq OWNER TO postgres;

--
-- Name: featureloc_allcoords; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.featureloc_allcoords AS
 SELECT featureloc.featureloc_id,
    featureloc.feature_id,
    featureloc.srcfeature_id,
    featureloc.fmin,
    featureloc.is_fmin_partial,
    featureloc.fmax,
    featureloc.is_fmax_partial,
    featureloc.strand,
    featureloc.phase,
    featureloc.residue_info,
    featureloc.locgroup,
    featureloc.rank,
    (featureloc.fmin + 1) AS gbeg,
    featureloc.fmax AS gend,
        CASE
            WHEN (featureloc.strand = '-1'::integer) THEN (- featureloc.fmax)
            ELSE featureloc.fmin
        END AS nbeg,
        CASE
            WHEN (featureloc.strand = '-1'::integer) THEN (- featureloc.fmin)
            ELSE featureloc.fmax
        END AS nend
   FROM public.featureloc;


ALTER TABLE public.featureloc_allcoords OWNER TO postgres;

--
-- Name: featureloc_featureloc_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.featureloc_featureloc_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.featureloc_featureloc_id_seq OWNER TO postgres;

--
-- Name: featureloc_featureloc_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.featureloc_featureloc_id_seq OWNED BY public.featureloc.featureloc_id;


--
-- Name: featureloc_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.featureloc_pub (
    featureloc_pub_id integer NOT NULL,
    featureloc_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.featureloc_pub OWNER TO postgres;

--
-- Name: TABLE featureloc_pub; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.featureloc_pub IS 'Provenance of featureloc. Linking table between featurelocs and publications that mention them';


--
-- Name: featureloc_pub_featureloc_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.featureloc_pub_featureloc_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.featureloc_pub_featureloc_pub_id_seq OWNER TO postgres;

--
-- Name: featureloc_pub_featureloc_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.featureloc_pub_featureloc_pub_id_seq OWNED BY public.featureloc_pub.featureloc_pub_id;


--
-- Name: featuremap; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.featuremap (
    featuremap_id integer NOT NULL,
    name character varying(255),
    description text,
    unittype_id integer
);


ALTER TABLE public.featuremap OWNER TO postgres;

--
-- Name: featuremap_featuremap_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.featuremap_featuremap_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.featuremap_featuremap_id_seq OWNER TO postgres;

--
-- Name: featuremap_featuremap_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.featuremap_featuremap_id_seq OWNED BY public.featuremap.featuremap_id;


--
-- Name: featuremap_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.featuremap_pub (
    featuremap_pub_id integer NOT NULL,
    featuremap_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.featuremap_pub OWNER TO postgres;

--
-- Name: featuremap_pub_featuremap_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.featuremap_pub_featuremap_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.featuremap_pub_featuremap_pub_id_seq OWNER TO postgres;

--
-- Name: featuremap_pub_featuremap_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.featuremap_pub_featuremap_pub_id_seq OWNED BY public.featuremap_pub.featuremap_pub_id;


--
-- Name: featurepos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.featurepos (
    featurepos_id integer NOT NULL,
    featuremap_id integer NOT NULL,
    feature_id integer NOT NULL,
    map_feature_id integer NOT NULL,
    mappos double precision NOT NULL
);


ALTER TABLE public.featurepos OWNER TO postgres;

--
-- Name: featurepos_featuremap_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.featurepos_featuremap_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.featurepos_featuremap_id_seq OWNER TO postgres;

--
-- Name: featurepos_featuremap_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.featurepos_featuremap_id_seq OWNED BY public.featurepos.featuremap_id;


--
-- Name: featurepos_featurepos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.featurepos_featurepos_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.featurepos_featurepos_id_seq OWNER TO postgres;

--
-- Name: featurepos_featurepos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.featurepos_featurepos_id_seq OWNED BY public.featurepos.featurepos_id;


--
-- Name: featureprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.featureprop (
    featureprop_id integer NOT NULL,
    feature_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.featureprop OWNER TO postgres;

--
-- Name: featureprop_featureprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.featureprop_featureprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.featureprop_featureprop_id_seq OWNER TO postgres;

--
-- Name: featureprop_featureprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.featureprop_featureprop_id_seq OWNED BY public.featureprop.featureprop_id;


--
-- Name: featureprop_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.featureprop_pub (
    featureprop_pub_id integer NOT NULL,
    featureprop_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.featureprop_pub OWNER TO postgres;

--
-- Name: featureprop_pub_featureprop_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.featureprop_pub_featureprop_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.featureprop_pub_featureprop_pub_id_seq OWNER TO postgres;

--
-- Name: featureprop_pub_featureprop_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.featureprop_pub_featureprop_pub_id_seq OWNED BY public.featureprop_pub.featureprop_pub_id;


--
-- Name: featurerange; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.featurerange (
    featurerange_id integer NOT NULL,
    featuremap_id integer NOT NULL,
    feature_id integer NOT NULL,
    leftstartf_id integer NOT NULL,
    leftendf_id integer,
    rightstartf_id integer,
    rightendf_id integer NOT NULL,
    rangestr character varying(255)
);


ALTER TABLE public.featurerange OWNER TO postgres;

--
-- Name: featurerange_featurerange_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.featurerange_featurerange_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.featurerange_featurerange_id_seq OWNER TO postgres;

--
-- Name: featurerange_featurerange_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.featurerange_featurerange_id_seq OWNED BY public.featurerange.featurerange_id;


--
-- Name: fnr_type; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.fnr_type AS
 SELECT f.feature_id,
    f.name,
    f.uniquename,
    f.dbxref_id,
    c.name AS type,
    f.residues,
    f.seqlen,
    f.md5checksum,
    f.type_id,
    f.organism_id,
    f.timeaccessioned,
    f.timelastmodified
   FROM (public.feature f
     LEFT JOIN public.analysisfeature af ON ((f.feature_id = af.feature_id))),
    public.cvterm c
  WHERE ((f.type_id = c.cvterm_id) AND (af.feature_id IS NULL));


ALTER TABLE public.fnr_type OWNER TO postgres;

--
-- Name: fp_key; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.fp_key AS
 SELECT fp.featureprop_id,
    fp.feature_id,
    c.name AS type,
    fp.value
   FROM public.featureprop fp,
    public.cvterm c
  WHERE (fp.type_id = c.cvterm_id);


ALTER TABLE public.fp_key OWNER TO postgres;

--
-- Name: genotype; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.genotype (
    genotype_id integer NOT NULL,
    uniquename text NOT NULL,
    description character varying(255),
    name text
);


ALTER TABLE public.genotype OWNER TO postgres;

--
-- Name: genotype_genotype_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.genotype_genotype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.genotype_genotype_id_seq OWNER TO postgres;

--
-- Name: genotype_genotype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.genotype_genotype_id_seq OWNED BY public.genotype.genotype_id;


--
-- Name: gffatts_slim; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.gffatts_slim AS
 SELECT fs.feature_id,
    'dbxref'::character varying AS type,
    (((d.name)::text || (':'::character varying)::text) || (s.accession)::text) AS attribute
   FROM public.dbxref s,
    public.feature_dbxref fs,
    public.db d
  WHERE ((fs.dbxref_id = s.dbxref_id) AND (s.db_id = d.db_id))
UNION ALL
 SELECT fp.feature_id,
    cv.name AS type,
    fp.value AS attribute
   FROM public.featureprop fp,
    public.cvterm cv
  WHERE ((fp.type_id = cv.cvterm_id) AND (((cv.name)::text = ('cyto_range'::character varying)::text) OR ((cv.name)::text = ('gbunit'::character varying)::text)));


ALTER TABLE public.gffatts_slim OWNER TO postgres;

--
-- Name: gffatts_slpar; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.gffatts_slpar AS
 SELECT fs.feature_id,
    'dbxref'::character varying AS type,
    (((d.name)::text || (':'::character varying)::text) || (s.accession)::text) AS attribute
   FROM public.dbxref s,
    public.feature_dbxref fs,
    public.db d
  WHERE ((fs.dbxref_id = s.dbxref_id) AND (s.db_id = d.db_id))
UNION ALL
 SELECT fp.feature_id,
    cv.name AS type,
    fp.value AS attribute
   FROM public.featureprop fp,
    public.cvterm cv
  WHERE ((fp.type_id = cv.cvterm_id) AND (((cv.name)::text = ('cyto_range'::character varying)::text) OR ((cv.name)::text = ('gbunit'::character varying)::text)))
UNION ALL
 SELECT pk.subject_id AS feature_id,
    'parent_oid'::character varying AS type,
        CASE
            WHEN (pk.rank IS NULL) THEN (pk.object_id)::text
            ELSE (((pk.object_id)::text || ':'::text) || (pk.rank)::text)
        END AS attribute
   FROM public.feature_relationship pk;


ALTER TABLE public.gffatts_slpar OWNER TO postgres;

--
-- Name: grp; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.grp (
    grp_id integer NOT NULL,
    name character varying(255),
    uniquename text NOT NULL,
    type_id integer NOT NULL,
    is_analysis boolean DEFAULT false NOT NULL,
    is_obsolete boolean DEFAULT false NOT NULL
);


ALTER TABLE public.grp OWNER TO postgres;

--
-- Name: grp_cvterm; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.grp_cvterm (
    grp_cvterm_id integer NOT NULL,
    is_not boolean DEFAULT false NOT NULL,
    cvterm_id integer NOT NULL,
    grp_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.grp_cvterm OWNER TO postgres;

--
-- Name: grp_cvterm_grp_cvterm_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.grp_cvterm_grp_cvterm_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.grp_cvterm_grp_cvterm_id_seq OWNER TO postgres;

--
-- Name: grp_cvterm_grp_cvterm_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.grp_cvterm_grp_cvterm_id_seq OWNED BY public.grp_cvterm.grp_cvterm_id;


--
-- Name: grp_dbxref; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.grp_dbxref (
    grp_dbxref_id integer NOT NULL,
    is_current boolean DEFAULT true NOT NULL,
    dbxref_id integer NOT NULL,
    grp_id integer NOT NULL
);


ALTER TABLE public.grp_dbxref OWNER TO postgres;

--
-- Name: grp_dbxref_grp_dbxref_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.grp_dbxref_grp_dbxref_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.grp_dbxref_grp_dbxref_id_seq OWNER TO postgres;

--
-- Name: grp_dbxref_grp_dbxref_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.grp_dbxref_grp_dbxref_id_seq OWNED BY public.grp_dbxref.grp_dbxref_id;


--
-- Name: grp_grp_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.grp_grp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.grp_grp_id_seq OWNER TO postgres;

--
-- Name: grp_grp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.grp_grp_id_seq OWNED BY public.grp.grp_id;


--
-- Name: grp_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.grp_pub (
    grp_pub_id integer NOT NULL,
    pub_id integer NOT NULL,
    grp_id integer NOT NULL
);


ALTER TABLE public.grp_pub OWNER TO postgres;

--
-- Name: grp_pub_grp_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.grp_pub_grp_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.grp_pub_grp_pub_id_seq OWNER TO postgres;

--
-- Name: grp_pub_grp_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.grp_pub_grp_pub_id_seq OWNED BY public.grp_pub.grp_pub_id;


--
-- Name: grp_pubprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.grp_pubprop (
    grp_pubprop_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL,
    type_id integer NOT NULL,
    grp_pub_id integer NOT NULL
);


ALTER TABLE public.grp_pubprop OWNER TO postgres;

--
-- Name: grp_pubprop_grp_pubprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.grp_pubprop_grp_pubprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.grp_pubprop_grp_pubprop_id_seq OWNER TO postgres;

--
-- Name: grp_pubprop_grp_pubprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.grp_pubprop_grp_pubprop_id_seq OWNED BY public.grp_pubprop.grp_pubprop_id;


--
-- Name: grp_relationship; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.grp_relationship (
    grp_relationship_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL,
    type_id integer NOT NULL,
    subject_id integer NOT NULL,
    object_id integer NOT NULL
);


ALTER TABLE public.grp_relationship OWNER TO postgres;

--
-- Name: grp_relationship_grp_relationship_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.grp_relationship_grp_relationship_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.grp_relationship_grp_relationship_id_seq OWNER TO postgres;

--
-- Name: grp_relationship_grp_relationship_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.grp_relationship_grp_relationship_id_seq OWNED BY public.grp_relationship.grp_relationship_id;


--
-- Name: grp_relationship_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.grp_relationship_pub (
    grp_relationship_pub_id integer NOT NULL,
    pub_id integer NOT NULL,
    grp_relationship_id integer NOT NULL
);


ALTER TABLE public.grp_relationship_pub OWNER TO postgres;

--
-- Name: grp_relationship_pub_grp_relationship_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.grp_relationship_pub_grp_relationship_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.grp_relationship_pub_grp_relationship_pub_id_seq OWNER TO postgres;

--
-- Name: grp_relationship_pub_grp_relationship_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.grp_relationship_pub_grp_relationship_pub_id_seq OWNED BY public.grp_relationship_pub.grp_relationship_pub_id;


--
-- Name: grp_relationshipprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.grp_relationshipprop (
    grp_relationshipprop_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL,
    type_id integer NOT NULL,
    grp_relationship_id integer NOT NULL
);


ALTER TABLE public.grp_relationshipprop OWNER TO postgres;

--
-- Name: grp_relationshipprop_grp_relationshipprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.grp_relationshipprop_grp_relationshipprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.grp_relationshipprop_grp_relationshipprop_id_seq OWNER TO postgres;

--
-- Name: grp_relationshipprop_grp_relationshipprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.grp_relationshipprop_grp_relationshipprop_id_seq OWNED BY public.grp_relationshipprop.grp_relationshipprop_id;


--
-- Name: grp_synonym; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.grp_synonym (
    grp_synonym_id integer NOT NULL,
    synonym_id integer NOT NULL,
    grp_id integer NOT NULL,
    pub_id integer NOT NULL,
    is_current boolean DEFAULT false NOT NULL,
    is_internal boolean DEFAULT false NOT NULL
);


ALTER TABLE public.grp_synonym OWNER TO postgres;

--
-- Name: grp_synonym_grp_synonym_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.grp_synonym_grp_synonym_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.grp_synonym_grp_synonym_id_seq OWNER TO postgres;

--
-- Name: grp_synonym_grp_synonym_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.grp_synonym_grp_synonym_id_seq OWNED BY public.grp_synonym.grp_synonym_id;


--
-- Name: grpmember; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.grpmember (
    grpmember_id integer NOT NULL,
    rank integer DEFAULT 0 NOT NULL,
    type_id integer NOT NULL,
    grp_id integer NOT NULL
);


ALTER TABLE public.grpmember OWNER TO postgres;

--
-- Name: grpmember_cvterm; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.grpmember_cvterm (
    grpmember_cvterm_id integer NOT NULL,
    is_not boolean DEFAULT false NOT NULL,
    cvterm_id integer NOT NULL,
    grpmember_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.grpmember_cvterm OWNER TO postgres;

--
-- Name: grpmember_cvterm_grpmember_cvterm_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.grpmember_cvterm_grpmember_cvterm_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.grpmember_cvterm_grpmember_cvterm_id_seq OWNER TO postgres;

--
-- Name: grpmember_cvterm_grpmember_cvterm_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.grpmember_cvterm_grpmember_cvterm_id_seq OWNED BY public.grpmember_cvterm.grpmember_cvterm_id;


--
-- Name: grpmember_grpmember_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.grpmember_grpmember_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.grpmember_grpmember_id_seq OWNER TO postgres;

--
-- Name: grpmember_grpmember_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.grpmember_grpmember_id_seq OWNED BY public.grpmember.grpmember_id;


--
-- Name: grpmember_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.grpmember_pub (
    grpmember_pub_id integer NOT NULL,
    pub_id integer NOT NULL,
    grpmember_id integer NOT NULL
);


ALTER TABLE public.grpmember_pub OWNER TO postgres;

--
-- Name: grpmember_pub_grpmember_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.grpmember_pub_grpmember_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.grpmember_pub_grpmember_pub_id_seq OWNER TO postgres;

--
-- Name: grpmember_pub_grpmember_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.grpmember_pub_grpmember_pub_id_seq OWNED BY public.grpmember_pub.grpmember_pub_id;


--
-- Name: grpmemberprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.grpmemberprop (
    grpmemberprop_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL,
    type_id integer NOT NULL,
    grpmember_id integer NOT NULL
);


ALTER TABLE public.grpmemberprop OWNER TO postgres;

--
-- Name: grpmemberprop_grpmemberprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.grpmemberprop_grpmemberprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.grpmemberprop_grpmemberprop_id_seq OWNER TO postgres;

--
-- Name: grpmemberprop_grpmemberprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.grpmemberprop_grpmemberprop_id_seq OWNED BY public.grpmemberprop.grpmemberprop_id;


--
-- Name: grpmemberprop_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.grpmemberprop_pub (
    grpmemberprop_pub_id integer NOT NULL,
    pub_id integer NOT NULL,
    grpmemberprop_id integer NOT NULL
);


ALTER TABLE public.grpmemberprop_pub OWNER TO postgres;

--
-- Name: grpmemberprop_pub_grpmemberprop_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.grpmemberprop_pub_grpmemberprop_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.grpmemberprop_pub_grpmemberprop_pub_id_seq OWNER TO postgres;

--
-- Name: grpmemberprop_pub_grpmemberprop_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.grpmemberprop_pub_grpmemberprop_pub_id_seq OWNED BY public.grpmemberprop_pub.grpmemberprop_pub_id;


--
-- Name: grpprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.grpprop (
    grpprop_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL,
    type_id integer NOT NULL,
    grp_id integer NOT NULL
);


ALTER TABLE public.grpprop OWNER TO postgres;

--
-- Name: grpprop_grpprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.grpprop_grpprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.grpprop_grpprop_id_seq OWNER TO postgres;

--
-- Name: grpprop_grpprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.grpprop_grpprop_id_seq OWNED BY public.grpprop.grpprop_id;


--
-- Name: grpprop_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.grpprop_pub (
    grpprop_pub_id integer NOT NULL,
    pub_id integer NOT NULL,
    grpprop_id integer NOT NULL
);


ALTER TABLE public.grpprop_pub OWNER TO postgres;

--
-- Name: grpprop_pub_grpprop_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.grpprop_pub_grpprop_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.grpprop_pub_grpprop_pub_id_seq OWNER TO postgres;

--
-- Name: grpprop_pub_grpprop_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.grpprop_pub_grpprop_pub_id_seq OWNED BY public.grpprop_pub.grpprop_pub_id;


--
-- Name: humanhealth; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.humanhealth (
    humanhealth_id integer NOT NULL,
    name character varying(255),
    uniquename text NOT NULL,
    organism_id integer NOT NULL,
    dbxref_id integer,
    is_obsolete boolean DEFAULT false NOT NULL
);


ALTER TABLE public.humanhealth OWNER TO postgres;

--
-- Name: TABLE humanhealth; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.humanhealth IS 'A characterized humanhealth of a given organism.';


--
-- Name: humanhealth_cvterm; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.humanhealth_cvterm (
    humanhealth_cvterm_id integer NOT NULL,
    humanhealth_id integer NOT NULL,
    cvterm_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.humanhealth_cvterm OWNER TO postgres;

--
-- Name: TABLE humanhealth_cvterm; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.humanhealth_cvterm IS 'humanhealth to cvterm associations. Examples: term from GO biological process';


--
-- Name: humanhealth_cvterm_humanhealth_cvterm_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.humanhealth_cvterm_humanhealth_cvterm_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.humanhealth_cvterm_humanhealth_cvterm_id_seq OWNER TO postgres;

--
-- Name: humanhealth_cvterm_humanhealth_cvterm_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.humanhealth_cvterm_humanhealth_cvterm_id_seq OWNED BY public.humanhealth_cvterm.humanhealth_cvterm_id;


--
-- Name: humanhealth_cvtermprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.humanhealth_cvtermprop (
    humanhealth_cvtermprop_id integer NOT NULL,
    humanhealth_cvterm_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.humanhealth_cvtermprop OWNER TO postgres;

--
-- Name: TABLE humanhealth_cvtermprop; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.humanhealth_cvtermprop IS 'Extensible properties for
humanhealth to cvterm associations. Examples: qualifiers';


--
-- Name: COLUMN humanhealth_cvtermprop.type_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.humanhealth_cvtermprop.type_id IS 'The name of the
property/slot is a cvterm. The meaning of the property is defined in
that cvterm. ';


--
-- Name: COLUMN humanhealth_cvtermprop.value; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.humanhealth_cvtermprop.value IS 'The value of the
property, represented as text. Numeric values are converted to their
text representation. This is less efficient than using native database
types, but is easier to query.';


--
-- Name: COLUMN humanhealth_cvtermprop.rank; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.humanhealth_cvtermprop.rank IS 'Property-Value
ordering. Any humanhealth_cvterm can have multiple values for any particular
property type - these are ordered in a list using rank, counting from
zero. For properties that are single-valued rather than multi-valued,
the default 0 value should be used';


--
-- Name: humanhealth_cvtermprop_humanhealth_cvtermprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.humanhealth_cvtermprop_humanhealth_cvtermprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.humanhealth_cvtermprop_humanhealth_cvtermprop_id_seq OWNER TO postgres;

--
-- Name: humanhealth_cvtermprop_humanhealth_cvtermprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.humanhealth_cvtermprop_humanhealth_cvtermprop_id_seq OWNED BY public.humanhealth_cvtermprop.humanhealth_cvtermprop_id;


--
-- Name: humanhealth_dbxref; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.humanhealth_dbxref (
    humanhealth_dbxref_id integer NOT NULL,
    humanhealth_id integer NOT NULL,
    dbxref_id integer NOT NULL,
    is_current boolean DEFAULT true NOT NULL
);


ALTER TABLE public.humanhealth_dbxref OWNER TO postgres;

--
-- Name: humanhealth_dbxref_humanhealth_dbxref_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.humanhealth_dbxref_humanhealth_dbxref_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.humanhealth_dbxref_humanhealth_dbxref_id_seq OWNER TO postgres;

--
-- Name: humanhealth_dbxref_humanhealth_dbxref_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.humanhealth_dbxref_humanhealth_dbxref_id_seq OWNED BY public.humanhealth_dbxref.humanhealth_dbxref_id;


--
-- Name: humanhealth_dbxrefprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.humanhealth_dbxrefprop (
    humanhealth_dbxrefprop_id integer NOT NULL,
    humanhealth_dbxref_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.humanhealth_dbxrefprop OWNER TO postgres;

--
-- Name: TABLE humanhealth_dbxrefprop; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.humanhealth_dbxrefprop IS 'Attributes of a humanhealth_dbxref relationship.  Eg, URL, data_origin, owner';


--
-- Name: humanhealth_dbxrefprop_humanhealth_dbxrefprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.humanhealth_dbxrefprop_humanhealth_dbxrefprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.humanhealth_dbxrefprop_humanhealth_dbxrefprop_id_seq OWNER TO postgres;

--
-- Name: humanhealth_dbxrefprop_humanhealth_dbxrefprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.humanhealth_dbxrefprop_humanhealth_dbxrefprop_id_seq OWNED BY public.humanhealth_dbxrefprop.humanhealth_dbxrefprop_id;


--
-- Name: humanhealth_dbxrefprop_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.humanhealth_dbxrefprop_pub (
    humanhealth_dbxrefprop_pub_id integer NOT NULL,
    humanhealth_dbxrefprop_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.humanhealth_dbxrefprop_pub OWNER TO postgres;

--
-- Name: TABLE humanhealth_dbxrefprop_pub; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.humanhealth_dbxrefprop_pub IS 'attribution if need';


--
-- Name: humanhealth_dbxrefprop_pub_humanhealth_dbxrefprop_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.humanhealth_dbxrefprop_pub_humanhealth_dbxrefprop_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.humanhealth_dbxrefprop_pub_humanhealth_dbxrefprop_pub_id_seq OWNER TO postgres;

--
-- Name: humanhealth_dbxrefprop_pub_humanhealth_dbxrefprop_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.humanhealth_dbxrefprop_pub_humanhealth_dbxrefprop_pub_id_seq OWNED BY public.humanhealth_dbxrefprop_pub.humanhealth_dbxrefprop_pub_id;


--
-- Name: humanhealth_feature; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.humanhealth_feature (
    humanhealth_feature_id integer NOT NULL,
    humanhealth_id integer NOT NULL,
    feature_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.humanhealth_feature OWNER TO postgres;

--
-- Name: TABLE humanhealth_feature; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.humanhealth_feature IS 'humanhealth_feature links a humanhealth to features associated with the humanhealth.  Type may be, eg, "homozygous" or "heterozygous".';


--
-- Name: humanhealth_feature_humanhealth_feature_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.humanhealth_feature_humanhealth_feature_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.humanhealth_feature_humanhealth_feature_id_seq OWNER TO postgres;

--
-- Name: humanhealth_feature_humanhealth_feature_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.humanhealth_feature_humanhealth_feature_id_seq OWNED BY public.humanhealth_feature.humanhealth_feature_id;


--
-- Name: humanhealth_featureprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.humanhealth_featureprop (
    humanhealth_featureprop_id integer NOT NULL,
    humanhealth_feature_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.humanhealth_featureprop OWNER TO postgres;

--
-- Name: TABLE humanhealth_featureprop; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.humanhealth_featureprop IS 'Attributes of a humanhealth_feature relationship.  Eg, a comment';


--
-- Name: humanhealth_featureprop_humanhealth_featureprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.humanhealth_featureprop_humanhealth_featureprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.humanhealth_featureprop_humanhealth_featureprop_id_seq OWNER TO postgres;

--
-- Name: humanhealth_featureprop_humanhealth_featureprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.humanhealth_featureprop_humanhealth_featureprop_id_seq OWNED BY public.humanhealth_featureprop.humanhealth_featureprop_id;


--
-- Name: humanhealth_humanhealth_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.humanhealth_humanhealth_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.humanhealth_humanhealth_id_seq OWNER TO postgres;

--
-- Name: humanhealth_humanhealth_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.humanhealth_humanhealth_id_seq OWNED BY public.humanhealth.humanhealth_id;


--
-- Name: humanhealth_phenotype; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.humanhealth_phenotype (
    humanhealth_phenotype_id integer NOT NULL,
    humanhealth_id integer NOT NULL,
    phenotype_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.humanhealth_phenotype OWNER TO postgres;

--
-- Name: TABLE humanhealth_phenotype; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.humanhealth_phenotype IS 'Links phenotype(s) associated with a given humanhealth. ';


--
-- Name: humanhealth_phenotype_humanhealth_phenotype_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.humanhealth_phenotype_humanhealth_phenotype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.humanhealth_phenotype_humanhealth_phenotype_id_seq OWNER TO postgres;

--
-- Name: humanhealth_phenotype_humanhealth_phenotype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.humanhealth_phenotype_humanhealth_phenotype_id_seq OWNED BY public.humanhealth_phenotype.humanhealth_phenotype_id;


--
-- Name: humanhealth_phenotypeprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.humanhealth_phenotypeprop (
    humanhealth_phenotypeprop_id integer NOT NULL,
    humanhealth_phenotype_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.humanhealth_phenotypeprop OWNER TO postgres;

--
-- Name: TABLE humanhealth_phenotypeprop; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.humanhealth_phenotypeprop IS 'Attributes of a humanhealth_phenotype relationship.  Eg, a comment';


--
-- Name: humanhealth_phenotypeprop_humanhealth_phenotypeprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.humanhealth_phenotypeprop_humanhealth_phenotypeprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.humanhealth_phenotypeprop_humanhealth_phenotypeprop_id_seq OWNER TO postgres;

--
-- Name: humanhealth_phenotypeprop_humanhealth_phenotypeprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.humanhealth_phenotypeprop_humanhealth_phenotypeprop_id_seq OWNED BY public.humanhealth_phenotypeprop.humanhealth_phenotypeprop_id;


--
-- Name: humanhealth_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.humanhealth_pub (
    humanhealth_pub_id integer NOT NULL,
    humanhealth_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.humanhealth_pub OWNER TO postgres;

--
-- Name: humanhealth_pub_humanhealth_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.humanhealth_pub_humanhealth_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.humanhealth_pub_humanhealth_pub_id_seq OWNER TO postgres;

--
-- Name: humanhealth_pub_humanhealth_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.humanhealth_pub_humanhealth_pub_id_seq OWNED BY public.humanhealth_pub.humanhealth_pub_id;


--
-- Name: humanhealth_pubprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.humanhealth_pubprop (
    humanhealth_pubprop_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL,
    type_id integer NOT NULL,
    humanhealth_pub_id integer NOT NULL
);


ALTER TABLE public.humanhealth_pubprop OWNER TO postgres;

--
-- Name: humanhealth_pubprop_humanhealth_pubprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.humanhealth_pubprop_humanhealth_pubprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.humanhealth_pubprop_humanhealth_pubprop_id_seq OWNER TO postgres;

--
-- Name: humanhealth_pubprop_humanhealth_pubprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.humanhealth_pubprop_humanhealth_pubprop_id_seq OWNED BY public.humanhealth_pubprop.humanhealth_pubprop_id;


--
-- Name: humanhealth_relationship; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.humanhealth_relationship (
    humanhealth_relationship_id integer NOT NULL,
    subject_id integer NOT NULL,
    object_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.humanhealth_relationship OWNER TO postgres;

--
-- Name: TABLE humanhealth_relationship; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.humanhealth_relationship IS 'Relationships between humanhealths, eg, parent, sub disease.';


--
-- Name: humanhealth_relationship_humanhealth_relationship_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.humanhealth_relationship_humanhealth_relationship_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.humanhealth_relationship_humanhealth_relationship_id_seq OWNER TO postgres;

--
-- Name: humanhealth_relationship_humanhealth_relationship_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.humanhealth_relationship_humanhealth_relationship_id_seq OWNED BY public.humanhealth_relationship.humanhealth_relationship_id;


--
-- Name: humanhealth_relationship_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.humanhealth_relationship_pub (
    humanhealth_relationship_pub_id integer NOT NULL,
    humanhealth_relationship_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.humanhealth_relationship_pub OWNER TO postgres;

--
-- Name: TABLE humanhealth_relationship_pub; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.humanhealth_relationship_pub IS 'Provenance. Attach optional evidence to a humanhealth_relationship in the form of a publication.';


--
-- Name: humanhealth_relationship_pub_humanhealth_relationship_pub_i_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.humanhealth_relationship_pub_humanhealth_relationship_pub_i_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.humanhealth_relationship_pub_humanhealth_relationship_pub_i_seq OWNER TO postgres;

--
-- Name: humanhealth_relationship_pub_humanhealth_relationship_pub_i_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.humanhealth_relationship_pub_humanhealth_relationship_pub_i_seq OWNED BY public.humanhealth_relationship_pub.humanhealth_relationship_pub_id;


--
-- Name: humanhealth_synonym; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.humanhealth_synonym (
    humanhealth_synonym_id integer NOT NULL,
    humanhealth_id integer NOT NULL,
    synonym_id integer NOT NULL,
    pub_id integer NOT NULL,
    is_current boolean DEFAULT false NOT NULL,
    is_internal boolean DEFAULT false NOT NULL
);


ALTER TABLE public.humanhealth_synonym OWNER TO postgres;

--
-- Name: TABLE humanhealth_synonym; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.humanhealth_synonym IS 'Linking table between humanhealth and synonym.';


--
-- Name: humanhealth_synonym_humanhealth_synonym_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.humanhealth_synonym_humanhealth_synonym_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.humanhealth_synonym_humanhealth_synonym_id_seq OWNER TO postgres;

--
-- Name: humanhealth_synonym_humanhealth_synonym_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.humanhealth_synonym_humanhealth_synonym_id_seq OWNED BY public.humanhealth_synonym.humanhealth_synonym_id;


--
-- Name: humanhealthprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.humanhealthprop (
    humanhealthprop_id integer NOT NULL,
    humanhealth_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.humanhealthprop OWNER TO postgres;

--
-- Name: humanhealthprop_humanhealthprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.humanhealthprop_humanhealthprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.humanhealthprop_humanhealthprop_id_seq OWNER TO postgres;

--
-- Name: humanhealthprop_humanhealthprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.humanhealthprop_humanhealthprop_id_seq OWNED BY public.humanhealthprop.humanhealthprop_id;


--
-- Name: humanhealthprop_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.humanhealthprop_pub (
    humanhealthprop_pub_id integer NOT NULL,
    humanhealthprop_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.humanhealthprop_pub OWNER TO postgres;

--
-- Name: TABLE humanhealthprop_pub; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.humanhealthprop_pub IS 'Provenance.  Any humanhealthprop assignment can optionally be supported by a publication.';


--
-- Name: humanhealthprop_pub_humanhealthprop_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.humanhealthprop_pub_humanhealthprop_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.humanhealthprop_pub_humanhealthprop_pub_id_seq OWNER TO postgres;

--
-- Name: humanhealthprop_pub_humanhealthprop_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.humanhealthprop_pub_humanhealthprop_pub_id_seq OWNED BY public.humanhealthprop_pub.humanhealthprop_pub_id;


--
-- Name: interaction; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interaction (
    interaction_id integer NOT NULL,
    uniquename text NOT NULL,
    type_id integer NOT NULL,
    description text,
    is_obsolete boolean DEFAULT false NOT NULL
);


ALTER TABLE public.interaction OWNER TO postgres;

--
-- Name: interaction_cell_line; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interaction_cell_line (
    interaction_cell_line_id integer NOT NULL,
    cell_line_id integer NOT NULL,
    interaction_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.interaction_cell_line OWNER TO postgres;

--
-- Name: interaction_cell_line_interaction_cell_line_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.interaction_cell_line_interaction_cell_line_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.interaction_cell_line_interaction_cell_line_id_seq OWNER TO postgres;

--
-- Name: interaction_cell_line_interaction_cell_line_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.interaction_cell_line_interaction_cell_line_id_seq OWNED BY public.interaction_cell_line.interaction_cell_line_id;


--
-- Name: interaction_cvterm; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interaction_cvterm (
    interaction_cvterm_id integer NOT NULL,
    interaction_id integer NOT NULL,
    cvterm_id integer NOT NULL
);


ALTER TABLE public.interaction_cvterm OWNER TO postgres;

--
-- Name: interaction_cvterm_interaction_cvterm_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.interaction_cvterm_interaction_cvterm_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.interaction_cvterm_interaction_cvterm_id_seq OWNER TO postgres;

--
-- Name: interaction_cvterm_interaction_cvterm_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.interaction_cvterm_interaction_cvterm_id_seq OWNED BY public.interaction_cvterm.interaction_cvterm_id;


--
-- Name: interaction_cvtermprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interaction_cvtermprop (
    interaction_cvtermprop_id integer NOT NULL,
    interaction_cvterm_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.interaction_cvtermprop OWNER TO postgres;

--
-- Name: interaction_cvtermprop_interaction_cvtermprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.interaction_cvtermprop_interaction_cvtermprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.interaction_cvtermprop_interaction_cvtermprop_id_seq OWNER TO postgres;

--
-- Name: interaction_cvtermprop_interaction_cvtermprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.interaction_cvtermprop_interaction_cvtermprop_id_seq OWNED BY public.interaction_cvtermprop.interaction_cvtermprop_id;


--
-- Name: interaction_expression; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interaction_expression (
    interaction_expression_id integer NOT NULL,
    expression_id integer NOT NULL,
    interaction_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.interaction_expression OWNER TO postgres;

--
-- Name: interaction_expression_interaction_expression_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.interaction_expression_interaction_expression_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.interaction_expression_interaction_expression_id_seq OWNER TO postgres;

--
-- Name: interaction_expression_interaction_expression_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.interaction_expression_interaction_expression_id_seq OWNED BY public.interaction_expression.interaction_expression_id;


--
-- Name: interaction_expressionprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interaction_expressionprop (
    interaction_expressionprop_id integer NOT NULL,
    interaction_expression_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.interaction_expressionprop OWNER TO postgres;

--
-- Name: interaction_expressionprop_interaction_expressionprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.interaction_expressionprop_interaction_expressionprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.interaction_expressionprop_interaction_expressionprop_id_seq OWNER TO postgres;

--
-- Name: interaction_expressionprop_interaction_expressionprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.interaction_expressionprop_interaction_expressionprop_id_seq OWNED BY public.interaction_expressionprop.interaction_expressionprop_id;


--
-- Name: interaction_group; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interaction_group (
    interaction_group_id integer NOT NULL,
    uniquename text NOT NULL,
    is_obsolete boolean DEFAULT false NOT NULL,
    description text
);


ALTER TABLE public.interaction_group OWNER TO postgres;

--
-- Name: interaction_group_feature_interaction; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interaction_group_feature_interaction (
    interaction_group_feature_interaction_id integer NOT NULL,
    interaction_group_id integer NOT NULL,
    feature_interaction_id integer NOT NULL,
    rank integer DEFAULT 0 NOT NULL,
    ftype character varying(255)
);


ALTER TABLE public.interaction_group_feature_interaction OWNER TO postgres;

--
-- Name: interaction_group_feature_int_interaction_group_feature_int_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.interaction_group_feature_int_interaction_group_feature_int_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.interaction_group_feature_int_interaction_group_feature_int_seq OWNER TO postgres;

--
-- Name: interaction_group_feature_int_interaction_group_feature_int_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.interaction_group_feature_int_interaction_group_feature_int_seq OWNED BY public.interaction_group_feature_interaction.interaction_group_feature_interaction_id;


--
-- Name: interaction_group_interaction_group_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.interaction_group_interaction_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.interaction_group_interaction_group_id_seq OWNER TO postgres;

--
-- Name: interaction_group_interaction_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.interaction_group_interaction_group_id_seq OWNED BY public.interaction_group.interaction_group_id;


--
-- Name: interaction_interaction_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.interaction_interaction_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.interaction_interaction_id_seq OWNER TO postgres;

--
-- Name: interaction_interaction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.interaction_interaction_id_seq OWNED BY public.interaction.interaction_id;


--
-- Name: interaction_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interaction_pub (
    interaction_pub_id integer NOT NULL,
    interaction_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.interaction_pub OWNER TO postgres;

--
-- Name: interaction_pub_interaction_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.interaction_pub_interaction_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.interaction_pub_interaction_pub_id_seq OWNER TO postgres;

--
-- Name: interaction_pub_interaction_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.interaction_pub_interaction_pub_id_seq OWNED BY public.interaction_pub.interaction_pub_id;


--
-- Name: interactionprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interactionprop (
    interactionprop_id integer NOT NULL,
    interaction_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.interactionprop OWNER TO postgres;

--
-- Name: interactionprop_interactionprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.interactionprop_interactionprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.interactionprop_interactionprop_id_seq OWNER TO postgres;

--
-- Name: interactionprop_interactionprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.interactionprop_interactionprop_id_seq OWNED BY public.interactionprop.interactionprop_id;


--
-- Name: interactionprop_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interactionprop_pub (
    interactionprop_pub_id integer NOT NULL,
    interactionprop_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.interactionprop_pub OWNER TO postgres;

--
-- Name: interactionprop_pub_interactionprop_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.interactionprop_pub_interactionprop_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.interactionprop_pub_interactionprop_pub_id_seq OWNER TO postgres;

--
-- Name: interactionprop_pub_interactionprop_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.interactionprop_pub_interactionprop_pub_id_seq OWNED BY public.interactionprop_pub.interactionprop_pub_id;


--
-- Name: library; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.library (
    library_id integer NOT NULL,
    organism_id integer NOT NULL,
    name character varying(255),
    uniquename text NOT NULL,
    type_id integer NOT NULL,
    is_obsolete boolean DEFAULT false NOT NULL,
    timeaccessioned timestamp without time zone DEFAULT now() NOT NULL,
    timelastmodified timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.library OWNER TO postgres;

--
-- Name: library_cvterm; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.library_cvterm (
    library_cvterm_id integer NOT NULL,
    library_id integer NOT NULL,
    cvterm_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.library_cvterm OWNER TO postgres;

--
-- Name: library_cvterm_library_cvterm_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.library_cvterm_library_cvterm_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.library_cvterm_library_cvterm_id_seq OWNER TO postgres;

--
-- Name: library_cvterm_library_cvterm_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.library_cvterm_library_cvterm_id_seq OWNED BY public.library_cvterm.library_cvterm_id;


--
-- Name: library_cvtermprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.library_cvtermprop (
    library_cvtermprop_id integer NOT NULL,
    library_cvterm_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.library_cvtermprop OWNER TO postgres;

--
-- Name: library_cvtermprop_library_cvtermprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.library_cvtermprop_library_cvtermprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.library_cvtermprop_library_cvtermprop_id_seq OWNER TO postgres;

--
-- Name: library_cvtermprop_library_cvtermprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.library_cvtermprop_library_cvtermprop_id_seq OWNED BY public.library_cvtermprop.library_cvtermprop_id;


--
-- Name: library_dbxref; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.library_dbxref (
    library_dbxref_id integer NOT NULL,
    library_id integer NOT NULL,
    dbxref_id integer NOT NULL,
    is_current boolean DEFAULT true NOT NULL
);


ALTER TABLE public.library_dbxref OWNER TO postgres;

--
-- Name: library_dbxref_library_dbxref_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.library_dbxref_library_dbxref_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.library_dbxref_library_dbxref_id_seq OWNER TO postgres;

--
-- Name: library_dbxref_library_dbxref_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.library_dbxref_library_dbxref_id_seq OWNED BY public.library_dbxref.library_dbxref_id;


--
-- Name: library_dbxrefprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.library_dbxrefprop (
    library_dbxrefprop_id integer NOT NULL,
    library_dbxref_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.library_dbxrefprop OWNER TO postgres;

--
-- Name: TABLE library_dbxrefprop; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.library_dbxrefprop IS 'Attributes of a library_dbxref relationship.  Eg, URL, data_origin, owner';


--
-- Name: library_dbxrefprop_library_dbxrefprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.library_dbxrefprop_library_dbxrefprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.library_dbxrefprop_library_dbxrefprop_id_seq OWNER TO postgres;

--
-- Name: library_dbxrefprop_library_dbxrefprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.library_dbxrefprop_library_dbxrefprop_id_seq OWNED BY public.library_dbxrefprop.library_dbxrefprop_id;


--
-- Name: library_expression; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.library_expression (
    library_expression_id integer NOT NULL,
    expression_id integer NOT NULL,
    library_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.library_expression OWNER TO postgres;

--
-- Name: library_expression_library_expression_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.library_expression_library_expression_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.library_expression_library_expression_id_seq OWNER TO postgres;

--
-- Name: library_expression_library_expression_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.library_expression_library_expression_id_seq OWNED BY public.library_expression.library_expression_id;


--
-- Name: library_expressionprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.library_expressionprop (
    library_expressionprop_id integer NOT NULL,
    library_expression_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.library_expressionprop OWNER TO postgres;

--
-- Name: library_expressionprop_library_expressionprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.library_expressionprop_library_expressionprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.library_expressionprop_library_expressionprop_id_seq OWNER TO postgres;

--
-- Name: library_expressionprop_library_expressionprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.library_expressionprop_library_expressionprop_id_seq OWNED BY public.library_expressionprop.library_expressionprop_id;


--
-- Name: library_feature; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.library_feature (
    library_feature_id integer NOT NULL,
    library_id integer NOT NULL,
    feature_id integer NOT NULL
);


ALTER TABLE public.library_feature OWNER TO postgres;

--
-- Name: library_feature_library_feature_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.library_feature_library_feature_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.library_feature_library_feature_id_seq OWNER TO postgres;

--
-- Name: library_feature_library_feature_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.library_feature_library_feature_id_seq OWNED BY public.library_feature.library_feature_id;


--
-- Name: library_featureprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.library_featureprop (
    library_featureprop_id integer NOT NULL,
    library_feature_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.library_featureprop OWNER TO postgres;

--
-- Name: TABLE library_featureprop; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.library_featureprop IS 'Extensible properties for library to feature associations. Examples: metadata such as number of reads for an RNA-Seq junction from a particular library/collection.';


--
-- Name: COLUMN library_featureprop.type_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.library_featureprop.type_id IS 'The name of the property/slot is a cvterm. The meaning of the property is defined in that cvterm. cvterms will typically come from the library_featureprop cv';


--
-- Name: library_featureprop_library_featureprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.library_featureprop_library_featureprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.library_featureprop_library_featureprop_id_seq OWNER TO postgres;

--
-- Name: library_featureprop_library_featureprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.library_featureprop_library_featureprop_id_seq OWNED BY public.library_featureprop.library_featureprop_id;


--
-- Name: library_grpmember; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.library_grpmember (
    library_grpmember_id integer NOT NULL,
    grpmember_id integer NOT NULL,
    library_id integer NOT NULL
);


ALTER TABLE public.library_grpmember OWNER TO postgres;

--
-- Name: library_grpmember_library_grpmember_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.library_grpmember_library_grpmember_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.library_grpmember_library_grpmember_id_seq OWNER TO postgres;

--
-- Name: library_grpmember_library_grpmember_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.library_grpmember_library_grpmember_id_seq OWNED BY public.library_grpmember.library_grpmember_id;


--
-- Name: library_humanhealth; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.library_humanhealth (
    library_humanhealth_id integer NOT NULL,
    humanhealth_id integer NOT NULL,
    library_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.library_humanhealth OWNER TO postgres;

--
-- Name: TABLE library_humanhealth; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.library_humanhealth IS 'Links library(s) associated with a given humanhealth.';


--
-- Name: library_humanhealth_library_humanhealth_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.library_humanhealth_library_humanhealth_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.library_humanhealth_library_humanhealth_id_seq OWNER TO postgres;

--
-- Name: library_humanhealth_library_humanhealth_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.library_humanhealth_library_humanhealth_id_seq OWNED BY public.library_humanhealth.library_humanhealth_id;


--
-- Name: library_humanhealthprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.library_humanhealthprop (
    library_humanhealthprop_id integer NOT NULL,
    library_humanhealth_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.library_humanhealthprop OWNER TO postgres;

--
-- Name: TABLE library_humanhealthprop; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.library_humanhealthprop IS 'Attributes of a library_humanhealth relationship.  Eg, types of relationships, comments.';


--
-- Name: library_humanhealthprop_library_humanhealthprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.library_humanhealthprop_library_humanhealthprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.library_humanhealthprop_library_humanhealthprop_id_seq OWNER TO postgres;

--
-- Name: library_humanhealthprop_library_humanhealthprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.library_humanhealthprop_library_humanhealthprop_id_seq OWNED BY public.library_humanhealthprop.library_humanhealthprop_id;


--
-- Name: library_interaction; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.library_interaction (
    library_interaction_id integer NOT NULL,
    interaction_id integer NOT NULL,
    library_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.library_interaction OWNER TO postgres;

--
-- Name: library_interaction_library_interaction_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.library_interaction_library_interaction_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.library_interaction_library_interaction_id_seq OWNER TO postgres;

--
-- Name: library_interaction_library_interaction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.library_interaction_library_interaction_id_seq OWNED BY public.library_interaction.library_interaction_id;


--
-- Name: library_library_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.library_library_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.library_library_id_seq OWNER TO postgres;

--
-- Name: library_library_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.library_library_id_seq OWNED BY public.library.library_id;


--
-- Name: library_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.library_pub (
    library_pub_id integer NOT NULL,
    library_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.library_pub OWNER TO postgres;

--
-- Name: library_pub_library_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.library_pub_library_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.library_pub_library_pub_id_seq OWNER TO postgres;

--
-- Name: library_pub_library_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.library_pub_library_pub_id_seq OWNED BY public.library_pub.library_pub_id;


--
-- Name: library_relationship; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.library_relationship (
    library_relationship_id integer NOT NULL,
    subject_id integer NOT NULL,
    object_id integer NOT NULL,
    type_id integer NOT NULL
);


ALTER TABLE public.library_relationship OWNER TO postgres;

--
-- Name: library_relationship_library_relationship_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.library_relationship_library_relationship_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.library_relationship_library_relationship_id_seq OWNER TO postgres;

--
-- Name: library_relationship_library_relationship_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.library_relationship_library_relationship_id_seq OWNED BY public.library_relationship.library_relationship_id;


--
-- Name: library_relationship_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.library_relationship_pub (
    library_relationship_pub_id integer NOT NULL,
    library_relationship_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.library_relationship_pub OWNER TO postgres;

--
-- Name: library_relationship_pub_library_relationship_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.library_relationship_pub_library_relationship_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.library_relationship_pub_library_relationship_pub_id_seq OWNER TO postgres;

--
-- Name: library_relationship_pub_library_relationship_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.library_relationship_pub_library_relationship_pub_id_seq OWNED BY public.library_relationship_pub.library_relationship_pub_id;


--
-- Name: library_strain; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.library_strain (
    library_strain_id integer NOT NULL,
    strain_id integer NOT NULL,
    library_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.library_strain OWNER TO postgres;

--
-- Name: TABLE library_strain; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.library_strain IS 'library_strain links a strain to librarys associated with the strain/pub.';


--
-- Name: library_strain_library_strain_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.library_strain_library_strain_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.library_strain_library_strain_id_seq OWNER TO postgres;

--
-- Name: library_strain_library_strain_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.library_strain_library_strain_id_seq OWNED BY public.library_strain.library_strain_id;


--
-- Name: library_strainprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.library_strainprop (
    library_strainprop_id integer NOT NULL,
    library_strain_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.library_strainprop OWNER TO postgres;

--
-- Name: TABLE library_strainprop; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.library_strainprop IS 'Attributes of a library_strain relationship.  Eg, types of relationships, comments.';


--
-- Name: library_strainprop_library_strainprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.library_strainprop_library_strainprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.library_strainprop_library_strainprop_id_seq OWNER TO postgres;

--
-- Name: library_strainprop_library_strainprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.library_strainprop_library_strainprop_id_seq OWNED BY public.library_strainprop.library_strainprop_id;


--
-- Name: library_synonym; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.library_synonym (
    library_synonym_id integer NOT NULL,
    synonym_id integer NOT NULL,
    library_id integer NOT NULL,
    pub_id integer NOT NULL,
    is_current boolean DEFAULT true NOT NULL,
    is_internal boolean DEFAULT false NOT NULL
);


ALTER TABLE public.library_synonym OWNER TO postgres;

--
-- Name: library_synonym_library_synonym_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.library_synonym_library_synonym_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.library_synonym_library_synonym_id_seq OWNER TO postgres;

--
-- Name: library_synonym_library_synonym_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.library_synonym_library_synonym_id_seq OWNED BY public.library_synonym.library_synonym_id;


--
-- Name: libraryprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.libraryprop (
    libraryprop_id integer NOT NULL,
    library_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.libraryprop OWNER TO postgres;

--
-- Name: libraryprop_libraryprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.libraryprop_libraryprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.libraryprop_libraryprop_id_seq OWNER TO postgres;

--
-- Name: libraryprop_libraryprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.libraryprop_libraryprop_id_seq OWNED BY public.libraryprop.libraryprop_id;


--
-- Name: libraryprop_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.libraryprop_pub (
    libraryprop_pub_id integer NOT NULL,
    libraryprop_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.libraryprop_pub OWNER TO postgres;

--
-- Name: libraryprop_pub_libraryprop_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.libraryprop_pub_libraryprop_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.libraryprop_pub_libraryprop_pub_id_seq OWNER TO postgres;

--
-- Name: libraryprop_pub_libraryprop_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.libraryprop_pub_libraryprop_pub_id_seq OWNED BY public.libraryprop_pub.libraryprop_pub_id;


--
-- Name: lock; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lock (
    lock_id integer NOT NULL,
    username character varying(20) DEFAULT 'administrator'::character varying NOT NULL,
    locktype character varying(20) DEFAULT 'write'::character varying NOT NULL,
    lockname character varying(100) NOT NULL,
    lockrank integer DEFAULT 0 NOT NULL,
    lockstatus boolean DEFAULT false NOT NULL,
    timeaccessioend timestamp without time zone DEFAULT now() NOT NULL,
    timelastmodified timestamp without time zone DEFAULT now() NOT NULL,
    chadoxmlfile character varying(100),
    comment character varying(100),
    task character varying(50) DEFAULT 'modify gene model'::character varying NOT NULL
);


ALTER TABLE public.lock OWNER TO postgres;

--
-- Name: lock_lock_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.lock_lock_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lock_lock_id_seq OWNER TO postgres;

--
-- Name: lock_lock_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.lock_lock_id_seq OWNED BY public.lock.lock_id;


--
-- Name: organism; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.organism (
    organism_id integer NOT NULL,
    abbreviation character varying(255),
    genus character varying(255) NOT NULL,
    species character varying(255) NOT NULL,
    common_name character varying(255),
    comment text
);


ALTER TABLE public.organism OWNER TO postgres;

--
-- Name: organism_cvterm; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.organism_cvterm (
    organism_cvterm_id integer NOT NULL,
    organism_id integer NOT NULL,
    cvterm_id integer NOT NULL,
    rank integer DEFAULT 0 NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.organism_cvterm OWNER TO postgres;

--
-- Name: TABLE organism_cvterm; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.organism_cvterm IS 'organism to cvterm associations. Examples: taxonomic name';


--
-- Name: COLUMN organism_cvterm.rank; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.organism_cvterm.rank IS 'Property-Value
ordering. Any organism_cvterm can have multiple values for any particular
property type - these are ordered in a list using rank, counting from
zero. For properties that are single-valued rather than multi-valued,
the default 0 value should be used';


--
-- Name: organism_cvterm_organism_cvterm_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.organism_cvterm_organism_cvterm_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.organism_cvterm_organism_cvterm_id_seq OWNER TO postgres;

--
-- Name: organism_cvterm_organism_cvterm_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.organism_cvterm_organism_cvterm_id_seq OWNED BY public.organism_cvterm.organism_cvterm_id;


--
-- Name: organism_cvtermprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.organism_cvtermprop (
    organism_cvtermprop_id integer NOT NULL,
    organism_cvterm_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.organism_cvtermprop OWNER TO postgres;

--
-- Name: TABLE organism_cvtermprop; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.organism_cvtermprop IS 'Extensible properties for
organism to cvterm associations. Examples: qualifiers';


--
-- Name: COLUMN organism_cvtermprop.type_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.organism_cvtermprop.type_id IS 'The name of the
property/slot is a cvterm. The meaning of the property is defined in
that cvterm. ';


--
-- Name: COLUMN organism_cvtermprop.value; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.organism_cvtermprop.value IS 'The value of the
property, represented as text. Numeric values are converted to their
text representation. This is less efficient than using native database
types, but is easier to query.';


--
-- Name: COLUMN organism_cvtermprop.rank; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.organism_cvtermprop.rank IS 'Property-Value
ordering. Any organism_cvterm can have multiple values for any particular
property type - these are ordered in a list using rank, counting from
zero. For properties that are single-valued rather than multi-valued,
the default 0 value should be used';


--
-- Name: organism_cvtermprop_organism_cvtermprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.organism_cvtermprop_organism_cvtermprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.organism_cvtermprop_organism_cvtermprop_id_seq OWNER TO postgres;

--
-- Name: organism_cvtermprop_organism_cvtermprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.organism_cvtermprop_organism_cvtermprop_id_seq OWNED BY public.organism_cvtermprop.organism_cvtermprop_id;


--
-- Name: organism_dbxref; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.organism_dbxref (
    organism_dbxref_id integer NOT NULL,
    organism_id integer NOT NULL,
    dbxref_id integer NOT NULL,
    is_current boolean DEFAULT true NOT NULL
);


ALTER TABLE public.organism_dbxref OWNER TO postgres;

--
-- Name: organism_dbxref_organism_dbxref_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.organism_dbxref_organism_dbxref_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.organism_dbxref_organism_dbxref_id_seq OWNER TO postgres;

--
-- Name: organism_dbxref_organism_dbxref_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.organism_dbxref_organism_dbxref_id_seq OWNED BY public.organism_dbxref.organism_dbxref_id;


--
-- Name: organism_grpmember; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.organism_grpmember (
    organism_grpmember_id integer NOT NULL,
    grpmember_id integer NOT NULL,
    organism_id integer NOT NULL
);


ALTER TABLE public.organism_grpmember OWNER TO postgres;

--
-- Name: organism_grpmember_organism_grpmember_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.organism_grpmember_organism_grpmember_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.organism_grpmember_organism_grpmember_id_seq OWNER TO postgres;

--
-- Name: organism_grpmember_organism_grpmember_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.organism_grpmember_organism_grpmember_id_seq OWNED BY public.organism_grpmember.organism_grpmember_id;


--
-- Name: organism_library; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.organism_library (
    organism_library_id integer NOT NULL,
    organism_id integer NOT NULL,
    library_id integer NOT NULL
);


ALTER TABLE public.organism_library OWNER TO postgres;

--
-- Name: organism_library_organism_library_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.organism_library_organism_library_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.organism_library_organism_library_id_seq OWNER TO postgres;

--
-- Name: organism_library_organism_library_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.organism_library_organism_library_id_seq OWNED BY public.organism_library.organism_library_id;


--
-- Name: organism_organism_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.organism_organism_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.organism_organism_id_seq OWNER TO postgres;

--
-- Name: organism_organism_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.organism_organism_id_seq OWNED BY public.organism.organism_id;


--
-- Name: organism_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.organism_pub (
    organism_pub_id integer NOT NULL,
    organism_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.organism_pub OWNER TO postgres;

--
-- Name: organism_pub_organism_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.organism_pub_organism_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.organism_pub_organism_pub_id_seq OWNER TO postgres;

--
-- Name: organism_pub_organism_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.organism_pub_organism_pub_id_seq OWNED BY public.organism_pub.organism_pub_id;


--
-- Name: organismprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.organismprop (
    organismprop_id integer NOT NULL,
    organism_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.organismprop OWNER TO postgres;

--
-- Name: organismprop_organismprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.organismprop_organismprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.organismprop_organismprop_id_seq OWNER TO postgres;

--
-- Name: organismprop_organismprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.organismprop_organismprop_id_seq OWNED BY public.organismprop.organismprop_id;


--
-- Name: organismprop_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.organismprop_pub (
    organismprop_pub_id integer NOT NULL,
    organismprop_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.organismprop_pub OWNER TO postgres;

--
-- Name: TABLE organismprop_pub; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.organismprop_pub IS 'Attribution for organismprop.';


--
-- Name: organismprop_pub_organismprop_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.organismprop_pub_organismprop_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.organismprop_pub_organismprop_pub_id_seq OWNER TO postgres;

--
-- Name: organismprop_pub_organismprop_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.organismprop_pub_organismprop_pub_id_seq OWNED BY public.organismprop_pub.organismprop_pub_id;


--
-- Name: phendesc; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.phendesc (
    phendesc_id integer NOT NULL,
    genotype_id integer NOT NULL,
    environment_id integer NOT NULL,
    description text NOT NULL,
    type_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.phendesc OWNER TO postgres;

--
-- Name: phendesc_phendesc_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.phendesc_phendesc_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.phendesc_phendesc_id_seq OWNER TO postgres;

--
-- Name: phendesc_phendesc_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.phendesc_phendesc_id_seq OWNED BY public.phendesc.phendesc_id;


--
-- Name: phenotype; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.phenotype (
    phenotype_id integer NOT NULL,
    uniquename text NOT NULL,
    observable_id integer,
    attr_id integer,
    value text,
    cvalue_id integer,
    assay_id integer
);


ALTER TABLE public.phenotype OWNER TO postgres;

--
-- Name: phenotype_comparison; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.phenotype_comparison (
    phenotype_comparison_id integer NOT NULL,
    genotype1_id integer NOT NULL,
    environment1_id integer NOT NULL,
    genotype2_id integer NOT NULL,
    environment2_id integer NOT NULL,
    phenotype1_id integer NOT NULL,
    phenotype2_id integer,
    pub_id integer NOT NULL,
    organism_id integer NOT NULL
);


ALTER TABLE public.phenotype_comparison OWNER TO postgres;

--
-- Name: phenotype_comparison_cvterm; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.phenotype_comparison_cvterm (
    phenotype_comparison_cvterm_id integer NOT NULL,
    phenotype_comparison_id integer NOT NULL,
    cvterm_id integer NOT NULL,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.phenotype_comparison_cvterm OWNER TO postgres;

--
-- Name: phenotype_comparison_cvterm_phenotype_comparison_cvterm_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.phenotype_comparison_cvterm_phenotype_comparison_cvterm_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.phenotype_comparison_cvterm_phenotype_comparison_cvterm_id_seq OWNER TO postgres;

--
-- Name: phenotype_comparison_cvterm_phenotype_comparison_cvterm_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.phenotype_comparison_cvterm_phenotype_comparison_cvterm_id_seq OWNED BY public.phenotype_comparison_cvterm.phenotype_comparison_cvterm_id;


--
-- Name: phenotype_comparison_phenotype_comparison_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.phenotype_comparison_phenotype_comparison_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.phenotype_comparison_phenotype_comparison_id_seq OWNER TO postgres;

--
-- Name: phenotype_comparison_phenotype_comparison_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.phenotype_comparison_phenotype_comparison_id_seq OWNED BY public.phenotype_comparison.phenotype_comparison_id;


--
-- Name: phenotype_cvterm; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.phenotype_cvterm (
    phenotype_cvterm_id integer NOT NULL,
    phenotype_id integer NOT NULL,
    cvterm_id integer NOT NULL,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.phenotype_cvterm OWNER TO postgres;

--
-- Name: phenotype_cvterm_phenotype_cvterm_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.phenotype_cvterm_phenotype_cvterm_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.phenotype_cvterm_phenotype_cvterm_id_seq OWNER TO postgres;

--
-- Name: phenotype_cvterm_phenotype_cvterm_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.phenotype_cvterm_phenotype_cvterm_id_seq OWNED BY public.phenotype_cvterm.phenotype_cvterm_id;


--
-- Name: phenotype_phenotype_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.phenotype_phenotype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.phenotype_phenotype_id_seq OWNER TO postgres;

--
-- Name: phenotype_phenotype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.phenotype_phenotype_id_seq OWNED BY public.phenotype.phenotype_id;


--
-- Name: phenstatement; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.phenstatement (
    phenstatement_id integer NOT NULL,
    genotype_id integer NOT NULL,
    environment_id integer NOT NULL,
    phenotype_id integer NOT NULL,
    type_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.phenstatement OWNER TO postgres;

--
-- Name: phenstatement_phenstatement_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.phenstatement_phenstatement_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.phenstatement_phenstatement_id_seq OWNER TO postgres;

--
-- Name: phenstatement_phenstatement_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.phenstatement_phenstatement_id_seq OWNED BY public.phenstatement.phenstatement_id;


--
-- Name: prediction_evidence; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.prediction_evidence AS
 SELECT (((((anchor.feature_id)::text || ':'::text) || (evloc.feature_id)::text) || ':'::text) || (af.analysis_id)::text) AS prediction_evidence_id,
    anchor.feature_id,
    evloc.feature_id AS evidence_id,
    af.analysis_id
   FROM public.featureloc anchor,
    public.featureloc evloc,
    public.analysisfeature af
  WHERE ((anchor.srcfeature_id = evloc.srcfeature_id) AND (anchor.strand = evloc.strand) AND (evloc.feature_id = af.feature_id) AND ((evloc.fmin <= anchor.fmax) AND (evloc.fmax >= anchor.fmin)));


ALTER TABLE public.prediction_evidence OWNER TO postgres;

--
-- Name: project; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.project (
    project_id integer NOT NULL,
    name character varying(255) NOT NULL,
    description character varying(255) NOT NULL
);


ALTER TABLE public.project OWNER TO postgres;

--
-- Name: project_project_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.project_project_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.project_project_id_seq OWNER TO postgres;

--
-- Name: project_project_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.project_project_id_seq OWNED BY public.project.project_id;


--
-- Name: pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pub (
    pub_id integer NOT NULL,
    title text,
    volumetitle text,
    volume character varying(255),
    series_name character varying(255),
    issue character varying(255),
    pyear character varying(255),
    pages character varying(255),
    miniref character varying(255),
    type_id integer NOT NULL,
    is_obsolete boolean DEFAULT false,
    publisher character varying(255),
    pubplace character varying(255),
    uniquename text NOT NULL
);


ALTER TABLE public.pub OWNER TO postgres;

--
-- Name: pub_dbxref; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pub_dbxref (
    pub_dbxref_id integer NOT NULL,
    pub_id integer NOT NULL,
    dbxref_id integer NOT NULL,
    is_current boolean DEFAULT true NOT NULL
);


ALTER TABLE public.pub_dbxref OWNER TO postgres;

--
-- Name: pub_dbxref_pub_dbxref_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pub_dbxref_pub_dbxref_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pub_dbxref_pub_dbxref_id_seq OWNER TO postgres;

--
-- Name: pub_dbxref_pub_dbxref_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pub_dbxref_pub_dbxref_id_seq OWNED BY public.pub_dbxref.pub_dbxref_id;


--
-- Name: pub_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pub_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pub_pub_id_seq OWNER TO postgres;

--
-- Name: pub_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pub_pub_id_seq OWNED BY public.pub.pub_id;


--
-- Name: pub_relationship; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pub_relationship (
    pub_relationship_id integer NOT NULL,
    type_id integer NOT NULL,
    subject_id integer NOT NULL,
    object_id integer NOT NULL
);


ALTER TABLE public.pub_relationship OWNER TO postgres;

--
-- Name: pub_relationship_pub_relationship_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pub_relationship_pub_relationship_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pub_relationship_pub_relationship_id_seq OWNER TO postgres;

--
-- Name: pub_relationship_pub_relationship_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pub_relationship_pub_relationship_id_seq OWNED BY public.pub_relationship.pub_relationship_id;


--
-- Name: pubauthor; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pubauthor (
    pubauthor_id integer NOT NULL,
    pub_id integer NOT NULL,
    rank integer NOT NULL,
    editor boolean DEFAULT false,
    surname character varying(100) NOT NULL,
    givennames character varying(100),
    suffix character varying(100)
);


ALTER TABLE public.pubauthor OWNER TO postgres;

--
-- Name: pubauthor_pubauthor_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pubauthor_pubauthor_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pubauthor_pubauthor_id_seq OWNER TO postgres;

--
-- Name: pubauthor_pubauthor_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pubauthor_pubauthor_id_seq OWNED BY public.pubauthor.pubauthor_id;


--
-- Name: pubprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pubprop (
    pubprop_id integer NOT NULL,
    pub_id integer NOT NULL,
    type_id integer NOT NULL,
    value text NOT NULL,
    rank integer
);


ALTER TABLE public.pubprop OWNER TO postgres;

--
-- Name: pubprop_pubprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pubprop_pubprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pubprop_pubprop_id_seq OWNER TO postgres;

--
-- Name: pubprop_pubprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pubprop_pubprop_id_seq OWNED BY public.pubprop.pubprop_id;


--
-- Name: strain; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.strain (
    strain_id integer NOT NULL,
    name character varying(255),
    uniquename text NOT NULL,
    organism_id integer NOT NULL,
    dbxref_id integer,
    is_obsolete boolean DEFAULT false NOT NULL
);


ALTER TABLE public.strain OWNER TO postgres;

--
-- Name: TABLE strain; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.strain IS 'A characterized strain of a given organism.';


--
-- Name: strain_cvterm; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.strain_cvterm (
    strain_cvterm_id integer NOT NULL,
    strain_id integer NOT NULL,
    cvterm_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.strain_cvterm OWNER TO postgres;

--
-- Name: TABLE strain_cvterm; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.strain_cvterm IS 'strain to cvterm associations. Examples: GOid';


--
-- Name: strain_cvterm_strain_cvterm_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.strain_cvterm_strain_cvterm_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.strain_cvterm_strain_cvterm_id_seq OWNER TO postgres;

--
-- Name: strain_cvterm_strain_cvterm_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.strain_cvterm_strain_cvterm_id_seq OWNED BY public.strain_cvterm.strain_cvterm_id;


--
-- Name: strain_cvtermprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.strain_cvtermprop (
    strain_cvtermprop_id integer NOT NULL,
    strain_cvterm_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.strain_cvtermprop OWNER TO postgres;

--
-- Name: TABLE strain_cvtermprop; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.strain_cvtermprop IS 'Extensible properties for
strain to cvterm associations. Examples: qualifiers';


--
-- Name: COLUMN strain_cvtermprop.type_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.strain_cvtermprop.type_id IS 'The name of the
property/slot is a cvterm. The meaning of the property is defined in
that cvterm. ';


--
-- Name: COLUMN strain_cvtermprop.value; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.strain_cvtermprop.value IS 'The value of the
property, represented as text. Numeric values are converted to their
text representation. This is less efficient than using native database
types, but is easier to query.';


--
-- Name: COLUMN strain_cvtermprop.rank; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.strain_cvtermprop.rank IS 'Property-Value
ordering. Any strain_cvterm can have multiple values for any particular
property type - these are ordered in a list using rank, counting from
zero. For properties that are single-valued rather than multi-valued,
the default 0 value should be used';


--
-- Name: strain_cvtermprop_strain_cvtermprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.strain_cvtermprop_strain_cvtermprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.strain_cvtermprop_strain_cvtermprop_id_seq OWNER TO postgres;

--
-- Name: strain_cvtermprop_strain_cvtermprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.strain_cvtermprop_strain_cvtermprop_id_seq OWNED BY public.strain_cvtermprop.strain_cvtermprop_id;


--
-- Name: strain_dbxref; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.strain_dbxref (
    strain_dbxref_id integer NOT NULL,
    strain_id integer NOT NULL,
    dbxref_id integer NOT NULL,
    is_current boolean DEFAULT true NOT NULL
);


ALTER TABLE public.strain_dbxref OWNER TO postgres;

--
-- Name: strain_dbxref_strain_dbxref_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.strain_dbxref_strain_dbxref_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.strain_dbxref_strain_dbxref_id_seq OWNER TO postgres;

--
-- Name: strain_dbxref_strain_dbxref_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.strain_dbxref_strain_dbxref_id_seq OWNED BY public.strain_dbxref.strain_dbxref_id;


--
-- Name: strain_feature; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.strain_feature (
    strain_feature_id integer NOT NULL,
    strain_id integer NOT NULL,
    feature_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.strain_feature OWNER TO postgres;

--
-- Name: TABLE strain_feature; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.strain_feature IS 'strain_feature links a strain to features associated with the strain.  Type may be, eg, "homozygous" or "heterozygous".';


--
-- Name: strain_feature_strain_feature_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.strain_feature_strain_feature_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.strain_feature_strain_feature_id_seq OWNER TO postgres;

--
-- Name: strain_feature_strain_feature_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.strain_feature_strain_feature_id_seq OWNED BY public.strain_feature.strain_feature_id;


--
-- Name: strain_featureprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.strain_featureprop (
    strain_featureprop_id integer NOT NULL,
    strain_feature_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.strain_featureprop OWNER TO postgres;

--
-- Name: TABLE strain_featureprop; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.strain_featureprop IS 'Attributes of a strain_feature relationship.  Eg, a comment';


--
-- Name: strain_featureprop_strain_featureprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.strain_featureprop_strain_featureprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.strain_featureprop_strain_featureprop_id_seq OWNER TO postgres;

--
-- Name: strain_featureprop_strain_featureprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.strain_featureprop_strain_featureprop_id_seq OWNED BY public.strain_featureprop.strain_featureprop_id;


--
-- Name: strain_phenotype; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.strain_phenotype (
    strain_phenotype_id integer NOT NULL,
    strain_id integer NOT NULL,
    phenotype_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.strain_phenotype OWNER TO postgres;

--
-- Name: TABLE strain_phenotype; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.strain_phenotype IS 'Links phenotype(s) associated with a given strain.  Types may be, eg, "selected" or "unassigned".';


--
-- Name: strain_phenotype_strain_phenotype_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.strain_phenotype_strain_phenotype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.strain_phenotype_strain_phenotype_id_seq OWNER TO postgres;

--
-- Name: strain_phenotype_strain_phenotype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.strain_phenotype_strain_phenotype_id_seq OWNED BY public.strain_phenotype.strain_phenotype_id;


--
-- Name: strain_phenotypeprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.strain_phenotypeprop (
    strain_phenotypeprop_id integer NOT NULL,
    strain_phenotype_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.strain_phenotypeprop OWNER TO postgres;

--
-- Name: TABLE strain_phenotypeprop; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.strain_phenotypeprop IS 'Attributes of a strain_phenotype relationship.  Eg, a comment';


--
-- Name: strain_phenotypeprop_strain_phenotypeprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.strain_phenotypeprop_strain_phenotypeprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.strain_phenotypeprop_strain_phenotypeprop_id_seq OWNER TO postgres;

--
-- Name: strain_phenotypeprop_strain_phenotypeprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.strain_phenotypeprop_strain_phenotypeprop_id_seq OWNED BY public.strain_phenotypeprop.strain_phenotypeprop_id;


--
-- Name: strain_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.strain_pub (
    strain_pub_id integer NOT NULL,
    strain_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.strain_pub OWNER TO postgres;

--
-- Name: strain_pub_strain_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.strain_pub_strain_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.strain_pub_strain_pub_id_seq OWNER TO postgres;

--
-- Name: strain_pub_strain_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.strain_pub_strain_pub_id_seq OWNED BY public.strain_pub.strain_pub_id;


--
-- Name: strain_relationship; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.strain_relationship (
    strain_relationship_id integer NOT NULL,
    subject_id integer NOT NULL,
    object_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.strain_relationship OWNER TO postgres;

--
-- Name: TABLE strain_relationship; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.strain_relationship IS 'Relationships between strains, eg, progenitor.';


--
-- Name: strain_relationship_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.strain_relationship_pub (
    strain_relationship_pub_id integer NOT NULL,
    strain_relationship_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.strain_relationship_pub OWNER TO postgres;

--
-- Name: TABLE strain_relationship_pub; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.strain_relationship_pub IS 'Provenance. Attach optional evidence to a strain_relationship in the form of a publication.';


--
-- Name: strain_relationship_pub_strain_relationship_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.strain_relationship_pub_strain_relationship_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.strain_relationship_pub_strain_relationship_pub_id_seq OWNER TO postgres;

--
-- Name: strain_relationship_pub_strain_relationship_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.strain_relationship_pub_strain_relationship_pub_id_seq OWNED BY public.strain_relationship_pub.strain_relationship_pub_id;


--
-- Name: strain_relationship_strain_relationship_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.strain_relationship_strain_relationship_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.strain_relationship_strain_relationship_id_seq OWNER TO postgres;

--
-- Name: strain_relationship_strain_relationship_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.strain_relationship_strain_relationship_id_seq OWNED BY public.strain_relationship.strain_relationship_id;


--
-- Name: strain_strain_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.strain_strain_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.strain_strain_id_seq OWNER TO postgres;

--
-- Name: strain_strain_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.strain_strain_id_seq OWNED BY public.strain.strain_id;


--
-- Name: strain_synonym; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.strain_synonym (
    strain_synonym_id integer NOT NULL,
    strain_id integer NOT NULL,
    synonym_id integer NOT NULL,
    pub_id integer NOT NULL,
    is_current boolean DEFAULT false NOT NULL,
    is_internal boolean DEFAULT false NOT NULL
);


ALTER TABLE public.strain_synonym OWNER TO postgres;

--
-- Name: TABLE strain_synonym; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.strain_synonym IS 'Linking table between strain and synonym.';


--
-- Name: strain_synonym_strain_synonym_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.strain_synonym_strain_synonym_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.strain_synonym_strain_synonym_id_seq OWNER TO postgres;

--
-- Name: strain_synonym_strain_synonym_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.strain_synonym_strain_synonym_id_seq OWNED BY public.strain_synonym.strain_synonym_id;


--
-- Name: strainprop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.strainprop (
    strainprop_id integer NOT NULL,
    strain_id integer NOT NULL,
    type_id integer NOT NULL,
    value text,
    rank integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.strainprop OWNER TO postgres;

--
-- Name: TABLE strainprop; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.strainprop IS 'Attributes of a given strain';


--
-- Name: strainprop_pub; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.strainprop_pub (
    strainprop_pub_id integer NOT NULL,
    strainprop_id integer NOT NULL,
    pub_id integer NOT NULL
);


ALTER TABLE public.strainprop_pub OWNER TO postgres;

--
-- Name: TABLE strainprop_pub; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.strainprop_pub IS 'Provenance.  Any strainprop assignment can optionally be supported by a publication.';


--
-- Name: strainprop_pub_strainprop_pub_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.strainprop_pub_strainprop_pub_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.strainprop_pub_strainprop_pub_id_seq OWNER TO postgres;

--
-- Name: strainprop_pub_strainprop_pub_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.strainprop_pub_strainprop_pub_id_seq OWNED BY public.strainprop_pub.strainprop_pub_id;


--
-- Name: strainprop_strainprop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.strainprop_strainprop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.strainprop_strainprop_id_seq OWNER TO postgres;

--
-- Name: strainprop_strainprop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.strainprop_strainprop_id_seq OWNED BY public.strainprop.strainprop_id;


--
-- Name: synonym; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.synonym (
    synonym_id integer NOT NULL,
    name character varying(255) NOT NULL,
    type_id integer NOT NULL,
    synonym_sgml character varying(255) NOT NULL
);


ALTER TABLE public.synonym OWNER TO postgres;

--
-- Name: synonym_synonym_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.synonym_synonym_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.synonym_synonym_id_seq OWNER TO postgres;

--
-- Name: synonym_synonym_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.synonym_synonym_id_seq OWNED BY public.synonym.synonym_id;


--
-- Name: tableinfo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tableinfo (
    tableinfo_id integer NOT NULL,
    name character varying(30) NOT NULL,
    primary_key_column character varying(30),
    is_view integer DEFAULT 0 NOT NULL,
    view_on_table_id integer,
    superclass_table_id integer,
    is_updateable integer DEFAULT 1 NOT NULL,
    modification_date date DEFAULT now() NOT NULL
);


ALTER TABLE public.tableinfo OWNER TO postgres;

--
-- Name: tableinfo_tableinfo_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tableinfo_tableinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tableinfo_tableinfo_id_seq OWNER TO postgres;

--
-- Name: tableinfo_tableinfo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tableinfo_tableinfo_id_seq OWNED BY public.tableinfo.tableinfo_id;


--
-- Name: update_track; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.update_track (
    update_track_id integer NOT NULL,
    release character varying(20) NOT NULL,
    fbid character varying(50) NOT NULL,
    time_update timestamp without time zone DEFAULT now() NOT NULL,
    author character varying(20) NOT NULL,
    statement character varying(255) NOT NULL,
    comment text DEFAULT ''::text NOT NULL,
    annotation_id character varying(50)
);


ALTER TABLE public.update_track OWNER TO postgres;

--
-- Name: update_track_update_track_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.update_track_update_track_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.update_track_update_track_id_seq OWNER TO postgres;

--
-- Name: update_track_update_track_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.update_track_update_track_id_seq OWNED BY public.update_track.update_track_id;


--
-- Name: analysis analysis_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysis ALTER COLUMN analysis_id SET DEFAULT nextval('public.analysis_analysis_id_seq'::regclass);


--
-- Name: analysisfeature analysisfeature_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisfeature ALTER COLUMN analysisfeature_id SET DEFAULT nextval('public.analysisfeature_analysisfeature_id_seq'::regclass);


--
-- Name: analysisgrp analysisgrp_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisgrp ALTER COLUMN analysisgrp_id SET DEFAULT nextval('public.analysisgrp_analysisgrp_id_seq'::regclass);


--
-- Name: analysisgrpmember analysisgrpmember_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisgrpmember ALTER COLUMN analysisgrpmember_id SET DEFAULT nextval('public.analysisgrpmember_analysisgrpmember_id_seq'::regclass);


--
-- Name: analysisprop analysisprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisprop ALTER COLUMN analysisprop_id SET DEFAULT nextval('public.analysisprop_analysisprop_id_seq'::regclass);


--
-- Name: cell_line cell_line_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line ALTER COLUMN cell_line_id SET DEFAULT nextval('public.cell_line_cell_line_id_seq'::regclass);


--
-- Name: cell_line_cvterm cell_line_cvterm_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_cvterm ALTER COLUMN cell_line_cvterm_id SET DEFAULT nextval('public.cell_line_cvterm_cell_line_cvterm_id_seq'::regclass);


--
-- Name: cell_line_cvtermprop cell_line_cvtermprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_cvtermprop ALTER COLUMN cell_line_cvtermprop_id SET DEFAULT nextval('public.cell_line_cvtermprop_cell_line_cvtermprop_id_seq'::regclass);


--
-- Name: cell_line_dbxref cell_line_dbxref_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_dbxref ALTER COLUMN cell_line_dbxref_id SET DEFAULT nextval('public.cell_line_dbxref_cell_line_dbxref_id_seq'::regclass);


--
-- Name: cell_line_feature cell_line_feature_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_feature ALTER COLUMN cell_line_feature_id SET DEFAULT nextval('public.cell_line_feature_cell_line_feature_id_seq'::regclass);


--
-- Name: cell_line_library cell_line_library_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_library ALTER COLUMN cell_line_library_id SET DEFAULT nextval('public.cell_line_library_cell_line_library_id_seq'::regclass);


--
-- Name: cell_line_libraryprop cell_line_libraryprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_libraryprop ALTER COLUMN cell_line_libraryprop_id SET DEFAULT nextval('public.cell_line_libraryprop_cell_line_libraryprop_id_seq'::regclass);


--
-- Name: cell_line_pub cell_line_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_pub ALTER COLUMN cell_line_pub_id SET DEFAULT nextval('public.cell_line_pub_cell_line_pub_id_seq'::regclass);


--
-- Name: cell_line_relationship cell_line_relationship_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_relationship ALTER COLUMN cell_line_relationship_id SET DEFAULT nextval('public.cell_line_relationship_cell_line_relationship_id_seq'::regclass);


--
-- Name: cell_line_strain cell_line_strain_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_strain ALTER COLUMN cell_line_strain_id SET DEFAULT nextval('public.cell_line_strain_cell_line_strain_id_seq'::regclass);


--
-- Name: cell_line_strainprop cell_line_strainprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_strainprop ALTER COLUMN cell_line_strainprop_id SET DEFAULT nextval('public.cell_line_strainprop_cell_line_strainprop_id_seq'::regclass);


--
-- Name: cell_line_synonym cell_line_synonym_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_synonym ALTER COLUMN cell_line_synonym_id SET DEFAULT nextval('public.cell_line_synonym_cell_line_synonym_id_seq'::regclass);


--
-- Name: cell_lineprop cell_lineprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_lineprop ALTER COLUMN cell_lineprop_id SET DEFAULT nextval('public.cell_lineprop_cell_lineprop_id_seq'::regclass);


--
-- Name: cell_lineprop_pub cell_lineprop_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_lineprop_pub ALTER COLUMN cell_lineprop_pub_id SET DEFAULT nextval('public.cell_lineprop_pub_cell_lineprop_pub_id_seq'::regclass);


--
-- Name: contact contact_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contact ALTER COLUMN contact_id SET DEFAULT nextval('public.contact_contact_id_seq'::regclass);


--
-- Name: cv cv_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cv ALTER COLUMN cv_id SET DEFAULT nextval('public.cv_cv_id_seq'::regclass);


--
-- Name: cvterm cvterm_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvterm ALTER COLUMN cvterm_id SET DEFAULT nextval('public.cvterm_cvterm_id_seq'::regclass);


--
-- Name: cvterm_dbxref cvterm_dbxref_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvterm_dbxref ALTER COLUMN cvterm_dbxref_id SET DEFAULT nextval('public.cvterm_dbxref_cvterm_dbxref_id_seq'::regclass);


--
-- Name: cvterm_relationship cvterm_relationship_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvterm_relationship ALTER COLUMN cvterm_relationship_id SET DEFAULT nextval('public.cvterm_relationship_cvterm_relationship_id_seq'::regclass);


--
-- Name: cvtermpath cvtermpath_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvtermpath ALTER COLUMN cvtermpath_id SET DEFAULT nextval('public.cvtermpath_cvtermpath_id_seq'::regclass);


--
-- Name: cvtermprop cvtermprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvtermprop ALTER COLUMN cvtermprop_id SET DEFAULT nextval('public.cvtermprop_cvtermprop_id_seq'::regclass);


--
-- Name: cvtermsynonym cvtermsynonym_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvtermsynonym ALTER COLUMN cvtermsynonym_id SET DEFAULT nextval('public.cvtermsynonym_cvtermsynonym_id_seq'::regclass);


--
-- Name: db db_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.db ALTER COLUMN db_id SET DEFAULT nextval('public.db_db_id_seq'::regclass);


--
-- Name: dbxref dbxref_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dbxref ALTER COLUMN dbxref_id SET DEFAULT nextval('public.dbxref_dbxref_id_seq'::regclass);


--
-- Name: dbxrefprop dbxrefprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dbxrefprop ALTER COLUMN dbxrefprop_id SET DEFAULT nextval('public.dbxrefprop_dbxrefprop_id_seq'::regclass);


--
-- Name: eimage eimage_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eimage ALTER COLUMN eimage_id SET DEFAULT nextval('public.eimage_eimage_id_seq'::regclass);


--
-- Name: environment environment_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.environment ALTER COLUMN environment_id SET DEFAULT nextval('public.environment_environment_id_seq'::regclass);


--
-- Name: environment_cvterm environment_cvterm_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.environment_cvterm ALTER COLUMN environment_cvterm_id SET DEFAULT nextval('public.environment_cvterm_environment_cvterm_id_seq'::regclass);


--
-- Name: expression expression_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expression ALTER COLUMN expression_id SET DEFAULT nextval('public.expression_expression_id_seq'::regclass);


--
-- Name: expression_cvterm expression_cvterm_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expression_cvterm ALTER COLUMN expression_cvterm_id SET DEFAULT nextval('public.expression_cvterm_expression_cvterm_id_seq'::regclass);


--
-- Name: expression_cvtermprop expression_cvtermprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expression_cvtermprop ALTER COLUMN expression_cvtermprop_id SET DEFAULT nextval('public.expression_cvtermprop_expression_cvtermprop_id_seq'::regclass);


--
-- Name: expression_image expression_image_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expression_image ALTER COLUMN expression_image_id SET DEFAULT nextval('public.expression_image_expression_image_id_seq'::regclass);


--
-- Name: expression_pub expression_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expression_pub ALTER COLUMN expression_pub_id SET DEFAULT nextval('public.expression_pub_expression_pub_id_seq'::regclass);


--
-- Name: expressionprop expressionprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expressionprop ALTER COLUMN expressionprop_id SET DEFAULT nextval('public.expressionprop_expressionprop_id_seq'::regclass);


--
-- Name: feature feature_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature ALTER COLUMN feature_id SET DEFAULT nextval('public.feature_feature_id_seq'::regclass);


--
-- Name: feature_cvterm feature_cvterm_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_cvterm ALTER COLUMN feature_cvterm_id SET DEFAULT nextval('public.feature_cvterm_feature_cvterm_id_seq'::regclass);


--
-- Name: feature_cvterm_dbxref feature_cvterm_dbxref_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_cvterm_dbxref ALTER COLUMN feature_cvterm_dbxref_id SET DEFAULT nextval('public.feature_cvterm_dbxref_feature_cvterm_dbxref_id_seq'::regclass);


--
-- Name: feature_cvtermprop feature_cvtermprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_cvtermprop ALTER COLUMN feature_cvtermprop_id SET DEFAULT nextval('public.feature_cvtermprop_feature_cvtermprop_id_seq'::regclass);


--
-- Name: feature_dbxref feature_dbxref_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_dbxref ALTER COLUMN feature_dbxref_id SET DEFAULT nextval('public.feature_dbxref_feature_dbxref_id_seq'::regclass);


--
-- Name: feature_expression feature_expression_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_expression ALTER COLUMN feature_expression_id SET DEFAULT nextval('public.feature_expression_feature_expression_id_seq'::regclass);


--
-- Name: feature_expressionprop feature_expressionprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_expressionprop ALTER COLUMN feature_expressionprop_id SET DEFAULT nextval('public.feature_expressionprop_feature_expressionprop_id_seq'::regclass);


--
-- Name: feature_genotype feature_genotype_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_genotype ALTER COLUMN feature_genotype_id SET DEFAULT nextval('public.feature_genotype_feature_genotype_id_seq'::regclass);


--
-- Name: feature_grpmember feature_grpmember_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_grpmember ALTER COLUMN feature_grpmember_id SET DEFAULT nextval('public.feature_grpmember_feature_grpmember_id_seq'::regclass);


--
-- Name: feature_grpmember_pub feature_grpmember_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_grpmember_pub ALTER COLUMN feature_grpmember_pub_id SET DEFAULT nextval('public.feature_grpmember_pub_feature_grpmember_pub_id_seq'::regclass);


--
-- Name: feature_humanhealth_dbxref feature_humanhealth_dbxref_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_humanhealth_dbxref ALTER COLUMN feature_humanhealth_dbxref_id SET DEFAULT nextval('public.feature_humanhealth_dbxref_feature_humanhealth_dbxref_id_seq'::regclass);


--
-- Name: feature_interaction feature_interaction_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_interaction ALTER COLUMN feature_interaction_id SET DEFAULT nextval('public.feature_interaction_feature_interaction_id_seq'::regclass);


--
-- Name: feature_interaction_pub feature_interaction_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_interaction_pub ALTER COLUMN feature_interaction_pub_id SET DEFAULT nextval('public.feature_interaction_pub_feature_interaction_pub_id_seq'::regclass);


--
-- Name: feature_interactionprop feature_interactionprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_interactionprop ALTER COLUMN feature_interactionprop_id SET DEFAULT nextval('public.feature_interactionprop_feature_interactionprop_id_seq'::regclass);


--
-- Name: feature_phenotype feature_phenotype_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_phenotype ALTER COLUMN feature_phenotype_id SET DEFAULT nextval('public.feature_phenotype_feature_phenotype_id_seq'::regclass);


--
-- Name: feature_pub feature_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_pub ALTER COLUMN feature_pub_id SET DEFAULT nextval('public.feature_pub_feature_pub_id_seq'::regclass);


--
-- Name: feature_pubprop feature_pubprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_pubprop ALTER COLUMN feature_pubprop_id SET DEFAULT nextval('public.feature_pubprop_feature_pubprop_id_seq'::regclass);


--
-- Name: feature_relationship feature_relationship_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_relationship ALTER COLUMN feature_relationship_id SET DEFAULT nextval('public.feature_relationship_feature_relationship_id_seq'::regclass);


--
-- Name: feature_relationship_pub feature_relationship_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_relationship_pub ALTER COLUMN feature_relationship_pub_id SET DEFAULT nextval('public.feature_relationship_pub_feature_relationship_pub_id_seq'::regclass);


--
-- Name: feature_relationshipprop feature_relationshipprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_relationshipprop ALTER COLUMN feature_relationshipprop_id SET DEFAULT nextval('public.feature_relationshipprop_feature_relationshipprop_id_seq'::regclass);


--
-- Name: feature_relationshipprop_pub feature_relationshipprop_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_relationshipprop_pub ALTER COLUMN feature_relationshipprop_pub_id SET DEFAULT nextval('public.feature_relationshipprop_pub_feature_relationshipprop_pub_i_seq'::regclass);


--
-- Name: feature_synonym feature_synonym_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_synonym ALTER COLUMN feature_synonym_id SET DEFAULT nextval('public.feature_synonym_feature_synonym_id_seq'::regclass);


--
-- Name: featureloc featureloc_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featureloc ALTER COLUMN featureloc_id SET DEFAULT nextval('public.featureloc_featureloc_id_seq'::regclass);


--
-- Name: featureloc_pub featureloc_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featureloc_pub ALTER COLUMN featureloc_pub_id SET DEFAULT nextval('public.featureloc_pub_featureloc_pub_id_seq'::regclass);


--
-- Name: featuremap featuremap_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featuremap ALTER COLUMN featuremap_id SET DEFAULT nextval('public.featuremap_featuremap_id_seq'::regclass);


--
-- Name: featuremap_pub featuremap_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featuremap_pub ALTER COLUMN featuremap_pub_id SET DEFAULT nextval('public.featuremap_pub_featuremap_pub_id_seq'::regclass);


--
-- Name: featurepos featurepos_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featurepos ALTER COLUMN featurepos_id SET DEFAULT nextval('public.featurepos_featurepos_id_seq'::regclass);


--
-- Name: featurepos featuremap_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featurepos ALTER COLUMN featuremap_id SET DEFAULT nextval('public.featurepos_featuremap_id_seq'::regclass);


--
-- Name: featureprop featureprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featureprop ALTER COLUMN featureprop_id SET DEFAULT nextval('public.featureprop_featureprop_id_seq'::regclass);


--
-- Name: featureprop_pub featureprop_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featureprop_pub ALTER COLUMN featureprop_pub_id SET DEFAULT nextval('public.featureprop_pub_featureprop_pub_id_seq'::regclass);


--
-- Name: featurerange featurerange_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featurerange ALTER COLUMN featurerange_id SET DEFAULT nextval('public.featurerange_featurerange_id_seq'::regclass);


--
-- Name: genotype genotype_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genotype ALTER COLUMN genotype_id SET DEFAULT nextval('public.genotype_genotype_id_seq'::regclass);


--
-- Name: grp grp_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp ALTER COLUMN grp_id SET DEFAULT nextval('public.grp_grp_id_seq'::regclass);


--
-- Name: grp_cvterm grp_cvterm_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_cvterm ALTER COLUMN grp_cvterm_id SET DEFAULT nextval('public.grp_cvterm_grp_cvterm_id_seq'::regclass);


--
-- Name: grp_dbxref grp_dbxref_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_dbxref ALTER COLUMN grp_dbxref_id SET DEFAULT nextval('public.grp_dbxref_grp_dbxref_id_seq'::regclass);


--
-- Name: grp_pub grp_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_pub ALTER COLUMN grp_pub_id SET DEFAULT nextval('public.grp_pub_grp_pub_id_seq'::regclass);


--
-- Name: grp_pubprop grp_pubprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_pubprop ALTER COLUMN grp_pubprop_id SET DEFAULT nextval('public.grp_pubprop_grp_pubprop_id_seq'::regclass);


--
-- Name: grp_relationship grp_relationship_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_relationship ALTER COLUMN grp_relationship_id SET DEFAULT nextval('public.grp_relationship_grp_relationship_id_seq'::regclass);


--
-- Name: grp_relationship_pub grp_relationship_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_relationship_pub ALTER COLUMN grp_relationship_pub_id SET DEFAULT nextval('public.grp_relationship_pub_grp_relationship_pub_id_seq'::regclass);


--
-- Name: grp_relationshipprop grp_relationshipprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_relationshipprop ALTER COLUMN grp_relationshipprop_id SET DEFAULT nextval('public.grp_relationshipprop_grp_relationshipprop_id_seq'::regclass);


--
-- Name: grp_synonym grp_synonym_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_synonym ALTER COLUMN grp_synonym_id SET DEFAULT nextval('public.grp_synonym_grp_synonym_id_seq'::regclass);


--
-- Name: grpmember grpmember_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmember ALTER COLUMN grpmember_id SET DEFAULT nextval('public.grpmember_grpmember_id_seq'::regclass);


--
-- Name: grpmember_cvterm grpmember_cvterm_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmember_cvterm ALTER COLUMN grpmember_cvterm_id SET DEFAULT nextval('public.grpmember_cvterm_grpmember_cvterm_id_seq'::regclass);


--
-- Name: grpmember_pub grpmember_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmember_pub ALTER COLUMN grpmember_pub_id SET DEFAULT nextval('public.grpmember_pub_grpmember_pub_id_seq'::regclass);


--
-- Name: grpmemberprop grpmemberprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmemberprop ALTER COLUMN grpmemberprop_id SET DEFAULT nextval('public.grpmemberprop_grpmemberprop_id_seq'::regclass);


--
-- Name: grpmemberprop_pub grpmemberprop_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmemberprop_pub ALTER COLUMN grpmemberprop_pub_id SET DEFAULT nextval('public.grpmemberprop_pub_grpmemberprop_pub_id_seq'::regclass);


--
-- Name: grpprop grpprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpprop ALTER COLUMN grpprop_id SET DEFAULT nextval('public.grpprop_grpprop_id_seq'::regclass);


--
-- Name: grpprop_pub grpprop_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpprop_pub ALTER COLUMN grpprop_pub_id SET DEFAULT nextval('public.grpprop_pub_grpprop_pub_id_seq'::regclass);


--
-- Name: humanhealth humanhealth_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth ALTER COLUMN humanhealth_id SET DEFAULT nextval('public.humanhealth_humanhealth_id_seq'::regclass);


--
-- Name: humanhealth_cvterm humanhealth_cvterm_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_cvterm ALTER COLUMN humanhealth_cvterm_id SET DEFAULT nextval('public.humanhealth_cvterm_humanhealth_cvterm_id_seq'::regclass);


--
-- Name: humanhealth_cvtermprop humanhealth_cvtermprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_cvtermprop ALTER COLUMN humanhealth_cvtermprop_id SET DEFAULT nextval('public.humanhealth_cvtermprop_humanhealth_cvtermprop_id_seq'::regclass);


--
-- Name: humanhealth_dbxref humanhealth_dbxref_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_dbxref ALTER COLUMN humanhealth_dbxref_id SET DEFAULT nextval('public.humanhealth_dbxref_humanhealth_dbxref_id_seq'::regclass);


--
-- Name: humanhealth_dbxrefprop humanhealth_dbxrefprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_dbxrefprop ALTER COLUMN humanhealth_dbxrefprop_id SET DEFAULT nextval('public.humanhealth_dbxrefprop_humanhealth_dbxrefprop_id_seq'::regclass);


--
-- Name: humanhealth_dbxrefprop_pub humanhealth_dbxrefprop_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_dbxrefprop_pub ALTER COLUMN humanhealth_dbxrefprop_pub_id SET DEFAULT nextval('public.humanhealth_dbxrefprop_pub_humanhealth_dbxrefprop_pub_id_seq'::regclass);


--
-- Name: humanhealth_feature humanhealth_feature_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_feature ALTER COLUMN humanhealth_feature_id SET DEFAULT nextval('public.humanhealth_feature_humanhealth_feature_id_seq'::regclass);


--
-- Name: humanhealth_featureprop humanhealth_featureprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_featureprop ALTER COLUMN humanhealth_featureprop_id SET DEFAULT nextval('public.humanhealth_featureprop_humanhealth_featureprop_id_seq'::regclass);


--
-- Name: humanhealth_phenotype humanhealth_phenotype_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_phenotype ALTER COLUMN humanhealth_phenotype_id SET DEFAULT nextval('public.humanhealth_phenotype_humanhealth_phenotype_id_seq'::regclass);


--
-- Name: humanhealth_phenotypeprop humanhealth_phenotypeprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_phenotypeprop ALTER COLUMN humanhealth_phenotypeprop_id SET DEFAULT nextval('public.humanhealth_phenotypeprop_humanhealth_phenotypeprop_id_seq'::regclass);


--
-- Name: humanhealth_pub humanhealth_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_pub ALTER COLUMN humanhealth_pub_id SET DEFAULT nextval('public.humanhealth_pub_humanhealth_pub_id_seq'::regclass);


--
-- Name: humanhealth_pubprop humanhealth_pubprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_pubprop ALTER COLUMN humanhealth_pubprop_id SET DEFAULT nextval('public.humanhealth_pubprop_humanhealth_pubprop_id_seq'::regclass);


--
-- Name: humanhealth_relationship humanhealth_relationship_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_relationship ALTER COLUMN humanhealth_relationship_id SET DEFAULT nextval('public.humanhealth_relationship_humanhealth_relationship_id_seq'::regclass);


--
-- Name: humanhealth_relationship_pub humanhealth_relationship_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_relationship_pub ALTER COLUMN humanhealth_relationship_pub_id SET DEFAULT nextval('public.humanhealth_relationship_pub_humanhealth_relationship_pub_i_seq'::regclass);


--
-- Name: humanhealth_synonym humanhealth_synonym_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_synonym ALTER COLUMN humanhealth_synonym_id SET DEFAULT nextval('public.humanhealth_synonym_humanhealth_synonym_id_seq'::regclass);


--
-- Name: humanhealthprop humanhealthprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealthprop ALTER COLUMN humanhealthprop_id SET DEFAULT nextval('public.humanhealthprop_humanhealthprop_id_seq'::regclass);


--
-- Name: humanhealthprop_pub humanhealthprop_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealthprop_pub ALTER COLUMN humanhealthprop_pub_id SET DEFAULT nextval('public.humanhealthprop_pub_humanhealthprop_pub_id_seq'::regclass);


--
-- Name: interaction interaction_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction ALTER COLUMN interaction_id SET DEFAULT nextval('public.interaction_interaction_id_seq'::regclass);


--
-- Name: interaction_cell_line interaction_cell_line_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_cell_line ALTER COLUMN interaction_cell_line_id SET DEFAULT nextval('public.interaction_cell_line_interaction_cell_line_id_seq'::regclass);


--
-- Name: interaction_cvterm interaction_cvterm_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_cvterm ALTER COLUMN interaction_cvterm_id SET DEFAULT nextval('public.interaction_cvterm_interaction_cvterm_id_seq'::regclass);


--
-- Name: interaction_cvtermprop interaction_cvtermprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_cvtermprop ALTER COLUMN interaction_cvtermprop_id SET DEFAULT nextval('public.interaction_cvtermprop_interaction_cvtermprop_id_seq'::regclass);


--
-- Name: interaction_expression interaction_expression_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_expression ALTER COLUMN interaction_expression_id SET DEFAULT nextval('public.interaction_expression_interaction_expression_id_seq'::regclass);


--
-- Name: interaction_expressionprop interaction_expressionprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_expressionprop ALTER COLUMN interaction_expressionprop_id SET DEFAULT nextval('public.interaction_expressionprop_interaction_expressionprop_id_seq'::regclass);


--
-- Name: interaction_group interaction_group_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_group ALTER COLUMN interaction_group_id SET DEFAULT nextval('public.interaction_group_interaction_group_id_seq'::regclass);


--
-- Name: interaction_group_feature_interaction interaction_group_feature_interaction_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_group_feature_interaction ALTER COLUMN interaction_group_feature_interaction_id SET DEFAULT nextval('public.interaction_group_feature_int_interaction_group_feature_int_seq'::regclass);


--
-- Name: interaction_pub interaction_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_pub ALTER COLUMN interaction_pub_id SET DEFAULT nextval('public.interaction_pub_interaction_pub_id_seq'::regclass);


--
-- Name: interactionprop interactionprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interactionprop ALTER COLUMN interactionprop_id SET DEFAULT nextval('public.interactionprop_interactionprop_id_seq'::regclass);


--
-- Name: interactionprop_pub interactionprop_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interactionprop_pub ALTER COLUMN interactionprop_pub_id SET DEFAULT nextval('public.interactionprop_pub_interactionprop_pub_id_seq'::regclass);


--
-- Name: library library_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library ALTER COLUMN library_id SET DEFAULT nextval('public.library_library_id_seq'::regclass);


--
-- Name: library_cvterm library_cvterm_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_cvterm ALTER COLUMN library_cvterm_id SET DEFAULT nextval('public.library_cvterm_library_cvterm_id_seq'::regclass);


--
-- Name: library_cvtermprop library_cvtermprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_cvtermprop ALTER COLUMN library_cvtermprop_id SET DEFAULT nextval('public.library_cvtermprop_library_cvtermprop_id_seq'::regclass);


--
-- Name: library_dbxref library_dbxref_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_dbxref ALTER COLUMN library_dbxref_id SET DEFAULT nextval('public.library_dbxref_library_dbxref_id_seq'::regclass);


--
-- Name: library_dbxrefprop library_dbxrefprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_dbxrefprop ALTER COLUMN library_dbxrefprop_id SET DEFAULT nextval('public.library_dbxrefprop_library_dbxrefprop_id_seq'::regclass);


--
-- Name: library_expression library_expression_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_expression ALTER COLUMN library_expression_id SET DEFAULT nextval('public.library_expression_library_expression_id_seq'::regclass);


--
-- Name: library_expressionprop library_expressionprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_expressionprop ALTER COLUMN library_expressionprop_id SET DEFAULT nextval('public.library_expressionprop_library_expressionprop_id_seq'::regclass);


--
-- Name: library_feature library_feature_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_feature ALTER COLUMN library_feature_id SET DEFAULT nextval('public.library_feature_library_feature_id_seq'::regclass);


--
-- Name: library_featureprop library_featureprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_featureprop ALTER COLUMN library_featureprop_id SET DEFAULT nextval('public.library_featureprop_library_featureprop_id_seq'::regclass);


--
-- Name: library_grpmember library_grpmember_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_grpmember ALTER COLUMN library_grpmember_id SET DEFAULT nextval('public.library_grpmember_library_grpmember_id_seq'::regclass);


--
-- Name: library_humanhealth library_humanhealth_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_humanhealth ALTER COLUMN library_humanhealth_id SET DEFAULT nextval('public.library_humanhealth_library_humanhealth_id_seq'::regclass);


--
-- Name: library_humanhealthprop library_humanhealthprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_humanhealthprop ALTER COLUMN library_humanhealthprop_id SET DEFAULT nextval('public.library_humanhealthprop_library_humanhealthprop_id_seq'::regclass);


--
-- Name: library_interaction library_interaction_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_interaction ALTER COLUMN library_interaction_id SET DEFAULT nextval('public.library_interaction_library_interaction_id_seq'::regclass);


--
-- Name: library_pub library_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_pub ALTER COLUMN library_pub_id SET DEFAULT nextval('public.library_pub_library_pub_id_seq'::regclass);


--
-- Name: library_relationship library_relationship_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_relationship ALTER COLUMN library_relationship_id SET DEFAULT nextval('public.library_relationship_library_relationship_id_seq'::regclass);


--
-- Name: library_relationship_pub library_relationship_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_relationship_pub ALTER COLUMN library_relationship_pub_id SET DEFAULT nextval('public.library_relationship_pub_library_relationship_pub_id_seq'::regclass);


--
-- Name: library_strain library_strain_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_strain ALTER COLUMN library_strain_id SET DEFAULT nextval('public.library_strain_library_strain_id_seq'::regclass);


--
-- Name: library_strainprop library_strainprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_strainprop ALTER COLUMN library_strainprop_id SET DEFAULT nextval('public.library_strainprop_library_strainprop_id_seq'::regclass);


--
-- Name: library_synonym library_synonym_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_synonym ALTER COLUMN library_synonym_id SET DEFAULT nextval('public.library_synonym_library_synonym_id_seq'::regclass);


--
-- Name: libraryprop libraryprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.libraryprop ALTER COLUMN libraryprop_id SET DEFAULT nextval('public.libraryprop_libraryprop_id_seq'::regclass);


--
-- Name: libraryprop_pub libraryprop_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.libraryprop_pub ALTER COLUMN libraryprop_pub_id SET DEFAULT nextval('public.libraryprop_pub_libraryprop_pub_id_seq'::regclass);


--
-- Name: lock lock_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lock ALTER COLUMN lock_id SET DEFAULT nextval('public.lock_lock_id_seq'::regclass);


--
-- Name: organism organism_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism ALTER COLUMN organism_id SET DEFAULT nextval('public.organism_organism_id_seq'::regclass);


--
-- Name: organism_cvterm organism_cvterm_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_cvterm ALTER COLUMN organism_cvterm_id SET DEFAULT nextval('public.organism_cvterm_organism_cvterm_id_seq'::regclass);


--
-- Name: organism_cvtermprop organism_cvtermprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_cvtermprop ALTER COLUMN organism_cvtermprop_id SET DEFAULT nextval('public.organism_cvtermprop_organism_cvtermprop_id_seq'::regclass);


--
-- Name: organism_dbxref organism_dbxref_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_dbxref ALTER COLUMN organism_dbxref_id SET DEFAULT nextval('public.organism_dbxref_organism_dbxref_id_seq'::regclass);


--
-- Name: organism_grpmember organism_grpmember_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_grpmember ALTER COLUMN organism_grpmember_id SET DEFAULT nextval('public.organism_grpmember_organism_grpmember_id_seq'::regclass);


--
-- Name: organism_library organism_library_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_library ALTER COLUMN organism_library_id SET DEFAULT nextval('public.organism_library_organism_library_id_seq'::regclass);


--
-- Name: organism_pub organism_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_pub ALTER COLUMN organism_pub_id SET DEFAULT nextval('public.organism_pub_organism_pub_id_seq'::regclass);


--
-- Name: organismprop organismprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organismprop ALTER COLUMN organismprop_id SET DEFAULT nextval('public.organismprop_organismprop_id_seq'::regclass);


--
-- Name: organismprop_pub organismprop_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organismprop_pub ALTER COLUMN organismprop_pub_id SET DEFAULT nextval('public.organismprop_pub_organismprop_pub_id_seq'::regclass);


--
-- Name: phendesc phendesc_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phendesc ALTER COLUMN phendesc_id SET DEFAULT nextval('public.phendesc_phendesc_id_seq'::regclass);


--
-- Name: phenotype phenotype_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype ALTER COLUMN phenotype_id SET DEFAULT nextval('public.phenotype_phenotype_id_seq'::regclass);


--
-- Name: phenotype_comparison phenotype_comparison_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype_comparison ALTER COLUMN phenotype_comparison_id SET DEFAULT nextval('public.phenotype_comparison_phenotype_comparison_id_seq'::regclass);


--
-- Name: phenotype_comparison_cvterm phenotype_comparison_cvterm_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype_comparison_cvterm ALTER COLUMN phenotype_comparison_cvterm_id SET DEFAULT nextval('public.phenotype_comparison_cvterm_phenotype_comparison_cvterm_id_seq'::regclass);


--
-- Name: phenotype_cvterm phenotype_cvterm_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype_cvterm ALTER COLUMN phenotype_cvterm_id SET DEFAULT nextval('public.phenotype_cvterm_phenotype_cvterm_id_seq'::regclass);


--
-- Name: phenstatement phenstatement_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenstatement ALTER COLUMN phenstatement_id SET DEFAULT nextval('public.phenstatement_phenstatement_id_seq'::regclass);


--
-- Name: project project_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project ALTER COLUMN project_id SET DEFAULT nextval('public.project_project_id_seq'::regclass);


--
-- Name: pub pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pub ALTER COLUMN pub_id SET DEFAULT nextval('public.pub_pub_id_seq'::regclass);


--
-- Name: pub_dbxref pub_dbxref_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pub_dbxref ALTER COLUMN pub_dbxref_id SET DEFAULT nextval('public.pub_dbxref_pub_dbxref_id_seq'::regclass);


--
-- Name: pub_relationship pub_relationship_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pub_relationship ALTER COLUMN pub_relationship_id SET DEFAULT nextval('public.pub_relationship_pub_relationship_id_seq'::regclass);


--
-- Name: pubauthor pubauthor_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pubauthor ALTER COLUMN pubauthor_id SET DEFAULT nextval('public.pubauthor_pubauthor_id_seq'::regclass);


--
-- Name: pubprop pubprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pubprop ALTER COLUMN pubprop_id SET DEFAULT nextval('public.pubprop_pubprop_id_seq'::regclass);


--
-- Name: strain strain_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain ALTER COLUMN strain_id SET DEFAULT nextval('public.strain_strain_id_seq'::regclass);


--
-- Name: strain_cvterm strain_cvterm_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_cvterm ALTER COLUMN strain_cvterm_id SET DEFAULT nextval('public.strain_cvterm_strain_cvterm_id_seq'::regclass);


--
-- Name: strain_cvtermprop strain_cvtermprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_cvtermprop ALTER COLUMN strain_cvtermprop_id SET DEFAULT nextval('public.strain_cvtermprop_strain_cvtermprop_id_seq'::regclass);


--
-- Name: strain_dbxref strain_dbxref_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_dbxref ALTER COLUMN strain_dbxref_id SET DEFAULT nextval('public.strain_dbxref_strain_dbxref_id_seq'::regclass);


--
-- Name: strain_feature strain_feature_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_feature ALTER COLUMN strain_feature_id SET DEFAULT nextval('public.strain_feature_strain_feature_id_seq'::regclass);


--
-- Name: strain_featureprop strain_featureprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_featureprop ALTER COLUMN strain_featureprop_id SET DEFAULT nextval('public.strain_featureprop_strain_featureprop_id_seq'::regclass);


--
-- Name: strain_phenotype strain_phenotype_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_phenotype ALTER COLUMN strain_phenotype_id SET DEFAULT nextval('public.strain_phenotype_strain_phenotype_id_seq'::regclass);


--
-- Name: strain_phenotypeprop strain_phenotypeprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_phenotypeprop ALTER COLUMN strain_phenotypeprop_id SET DEFAULT nextval('public.strain_phenotypeprop_strain_phenotypeprop_id_seq'::regclass);


--
-- Name: strain_pub strain_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_pub ALTER COLUMN strain_pub_id SET DEFAULT nextval('public.strain_pub_strain_pub_id_seq'::regclass);


--
-- Name: strain_relationship strain_relationship_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_relationship ALTER COLUMN strain_relationship_id SET DEFAULT nextval('public.strain_relationship_strain_relationship_id_seq'::regclass);


--
-- Name: strain_relationship_pub strain_relationship_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_relationship_pub ALTER COLUMN strain_relationship_pub_id SET DEFAULT nextval('public.strain_relationship_pub_strain_relationship_pub_id_seq'::regclass);


--
-- Name: strain_synonym strain_synonym_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_synonym ALTER COLUMN strain_synonym_id SET DEFAULT nextval('public.strain_synonym_strain_synonym_id_seq'::regclass);


--
-- Name: strainprop strainprop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strainprop ALTER COLUMN strainprop_id SET DEFAULT nextval('public.strainprop_strainprop_id_seq'::regclass);


--
-- Name: strainprop_pub strainprop_pub_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strainprop_pub ALTER COLUMN strainprop_pub_id SET DEFAULT nextval('public.strainprop_pub_strainprop_pub_id_seq'::regclass);


--
-- Name: synonym synonym_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.synonym ALTER COLUMN synonym_id SET DEFAULT nextval('public.synonym_synonym_id_seq'::regclass);


--
-- Name: tableinfo tableinfo_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tableinfo ALTER COLUMN tableinfo_id SET DEFAULT nextval('public.tableinfo_tableinfo_id_seq'::regclass);


--
-- Name: update_track update_track_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.update_track ALTER COLUMN update_track_id SET DEFAULT nextval('public.update_track_update_track_id_seq'::regclass);


--
-- Name: analysis analysis_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysis
    ADD CONSTRAINT analysis_pkey PRIMARY KEY (analysis_id);


--
-- Name: analysis analysis_program_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysis
    ADD CONSTRAINT analysis_program_key UNIQUE (program, programversion, sourcename);


--
-- Name: analysisfeature analysisfeature_feature_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisfeature
    ADD CONSTRAINT analysisfeature_feature_id_key UNIQUE (feature_id, analysis_id);


--
-- Name: analysisfeature analysisfeature_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisfeature
    ADD CONSTRAINT analysisfeature_pkey PRIMARY KEY (analysisfeature_id);


--
-- Name: analysisgrp analysisgrp_analysis_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisgrp
    ADD CONSTRAINT analysisgrp_analysis_id_key UNIQUE (analysis_id, grp_id);


--
-- Name: analysisgrp analysisgrp_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisgrp
    ADD CONSTRAINT analysisgrp_pkey PRIMARY KEY (analysisgrp_id);


--
-- Name: analysisgrpmember analysisgrpmember_analysis_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisgrpmember
    ADD CONSTRAINT analysisgrpmember_analysis_id_key UNIQUE (analysis_id, grpmember_id);


--
-- Name: analysisgrpmember analysisgrpmember_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisgrpmember
    ADD CONSTRAINT analysisgrpmember_pkey PRIMARY KEY (analysisgrpmember_id);


--
-- Name: analysisprop analysisprop_analysis_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisprop
    ADD CONSTRAINT analysisprop_analysis_id_key UNIQUE (analysis_id, type_id, value);


--
-- Name: analysisprop analysisprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisprop
    ADD CONSTRAINT analysisprop_pkey PRIMARY KEY (analysisprop_id);


--
-- Name: cell_line cell_line_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line
    ADD CONSTRAINT cell_line_c1 UNIQUE (uniquename, organism_id);


--
-- Name: cell_line_cvterm cell_line_cvterm_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_cvterm
    ADD CONSTRAINT cell_line_cvterm_c1 UNIQUE (cell_line_id, cvterm_id, pub_id, rank);


--
-- Name: cell_line_cvterm cell_line_cvterm_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_cvterm
    ADD CONSTRAINT cell_line_cvterm_pkey PRIMARY KEY (cell_line_cvterm_id);


--
-- Name: cell_line_cvtermprop cell_line_cvtermprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_cvtermprop
    ADD CONSTRAINT cell_line_cvtermprop_c1 UNIQUE (cell_line_cvterm_id, type_id, rank);


--
-- Name: cell_line_cvtermprop cell_line_cvtermprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_cvtermprop
    ADD CONSTRAINT cell_line_cvtermprop_pkey PRIMARY KEY (cell_line_cvtermprop_id);


--
-- Name: cell_line_dbxref cell_line_dbxref_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_dbxref
    ADD CONSTRAINT cell_line_dbxref_c1 UNIQUE (cell_line_id, dbxref_id);


--
-- Name: cell_line_dbxref cell_line_dbxref_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_dbxref
    ADD CONSTRAINT cell_line_dbxref_pkey PRIMARY KEY (cell_line_dbxref_id);


--
-- Name: cell_line_feature cell_line_feature_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_feature
    ADD CONSTRAINT cell_line_feature_c1 UNIQUE (cell_line_id, feature_id, pub_id);


--
-- Name: cell_line_feature cell_line_feature_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_feature
    ADD CONSTRAINT cell_line_feature_pkey PRIMARY KEY (cell_line_feature_id);


--
-- Name: cell_line_library cell_line_library_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_library
    ADD CONSTRAINT cell_line_library_c1 UNIQUE (cell_line_id, library_id, pub_id);


--
-- Name: cell_line_library cell_line_library_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_library
    ADD CONSTRAINT cell_line_library_pkey PRIMARY KEY (cell_line_library_id);


--
-- Name: cell_line_libraryprop cell_line_libraryprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_libraryprop
    ADD CONSTRAINT cell_line_libraryprop_c1 UNIQUE (cell_line_library_id, type_id, rank);


--
-- Name: cell_line_libraryprop cell_line_libraryprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_libraryprop
    ADD CONSTRAINT cell_line_libraryprop_pkey PRIMARY KEY (cell_line_libraryprop_id);


--
-- Name: cell_line cell_line_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line
    ADD CONSTRAINT cell_line_pkey PRIMARY KEY (cell_line_id);


--
-- Name: cell_line_pub cell_line_pub_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_pub
    ADD CONSTRAINT cell_line_pub_c1 UNIQUE (cell_line_id, pub_id);


--
-- Name: cell_line_pub cell_line_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_pub
    ADD CONSTRAINT cell_line_pub_pkey PRIMARY KEY (cell_line_pub_id);


--
-- Name: cell_line_relationship cell_line_relationship_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_relationship
    ADD CONSTRAINT cell_line_relationship_c1 UNIQUE (subject_id, object_id, type_id);


--
-- Name: cell_line_relationship cell_line_relationship_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_relationship
    ADD CONSTRAINT cell_line_relationship_pkey PRIMARY KEY (cell_line_relationship_id);


--
-- Name: cell_line_strain cell_line_strain_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_strain
    ADD CONSTRAINT cell_line_strain_c1 UNIQUE (strain_id, cell_line_id, pub_id);


--
-- Name: cell_line_strain cell_line_strain_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_strain
    ADD CONSTRAINT cell_line_strain_pkey PRIMARY KEY (cell_line_strain_id);


--
-- Name: cell_line_strainprop cell_line_strainprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_strainprop
    ADD CONSTRAINT cell_line_strainprop_c1 UNIQUE (cell_line_strain_id, type_id, rank);


--
-- Name: cell_line_strainprop cell_line_strainprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_strainprop
    ADD CONSTRAINT cell_line_strainprop_pkey PRIMARY KEY (cell_line_strainprop_id);


--
-- Name: cell_line_synonym cell_line_synonym_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_synonym
    ADD CONSTRAINT cell_line_synonym_c1 UNIQUE (synonym_id, cell_line_id, pub_id);


--
-- Name: cell_line_synonym cell_line_synonym_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_synonym
    ADD CONSTRAINT cell_line_synonym_pkey PRIMARY KEY (cell_line_synonym_id);


--
-- Name: cell_lineprop cell_lineprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_lineprop
    ADD CONSTRAINT cell_lineprop_c1 UNIQUE (cell_line_id, type_id, rank);


--
-- Name: cell_lineprop cell_lineprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_lineprop
    ADD CONSTRAINT cell_lineprop_pkey PRIMARY KEY (cell_lineprop_id);


--
-- Name: cell_lineprop_pub cell_lineprop_pub_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_lineprop_pub
    ADD CONSTRAINT cell_lineprop_pub_c1 UNIQUE (cell_lineprop_id, pub_id);


--
-- Name: cell_lineprop_pub cell_lineprop_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_lineprop_pub
    ADD CONSTRAINT cell_lineprop_pub_pkey PRIMARY KEY (cell_lineprop_pub_id);


--
-- Name: contact contact_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contact
    ADD CONSTRAINT contact_c1 UNIQUE (name);


--
-- Name: contact contact_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contact
    ADD CONSTRAINT contact_pkey PRIMARY KEY (contact_id);


--
-- Name: cv cv_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cv
    ADD CONSTRAINT cv_name_key UNIQUE (name);


--
-- Name: cv cv_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cv
    ADD CONSTRAINT cv_pkey PRIMARY KEY (cv_id);


--
-- Name: cvterm cvterm_c1_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvterm
    ADD CONSTRAINT cvterm_c1_unique UNIQUE (cv_id, name, is_obsolete);


--
-- Name: cvterm cvterm_c2_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvterm
    ADD CONSTRAINT cvterm_c2_unique UNIQUE (dbxref_id);


--
-- Name: cvterm_dbxref cvterm_dbxref_cvterm_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvterm_dbxref
    ADD CONSTRAINT cvterm_dbxref_cvterm_id_key UNIQUE (cvterm_id, dbxref_id);


--
-- Name: cvterm_dbxref cvterm_dbxref_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvterm_dbxref
    ADD CONSTRAINT cvterm_dbxref_pkey PRIMARY KEY (cvterm_dbxref_id);


--
-- Name: cvterm cvterm_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvterm
    ADD CONSTRAINT cvterm_pkey PRIMARY KEY (cvterm_id);


--
-- Name: cvterm_relationship cvterm_relationship_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvterm_relationship
    ADD CONSTRAINT cvterm_relationship_pkey PRIMARY KEY (cvterm_relationship_id);


--
-- Name: cvterm_relationship cvterm_relationship_type_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvterm_relationship
    ADD CONSTRAINT cvterm_relationship_type_id_key UNIQUE (type_id, subject_id, object_id);


--
-- Name: cvtermpath cvtermpath_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvtermpath
    ADD CONSTRAINT cvtermpath_pkey PRIMARY KEY (cvtermpath_id);


--
-- Name: cvtermpath cvtermpath_subject_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvtermpath
    ADD CONSTRAINT cvtermpath_subject_id_key UNIQUE (subject_id, object_id);


--
-- Name: cvtermprop cvtermprop_cvterm_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvtermprop
    ADD CONSTRAINT cvtermprop_cvterm_id_key UNIQUE (cvterm_id, type_id, value, rank);


--
-- Name: cvtermprop cvtermprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvtermprop
    ADD CONSTRAINT cvtermprop_pkey PRIMARY KEY (cvtermprop_id);


--
-- Name: cvtermsynonym cvtermsynonym_cvterm_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvtermsynonym
    ADD CONSTRAINT cvtermsynonym_cvterm_id_key UNIQUE (cvterm_id, name);


--
-- Name: cvtermsynonym cvtermsynonym_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvtermsynonym
    ADD CONSTRAINT cvtermsynonym_pkey PRIMARY KEY (cvtermsynonym_id);


--
-- Name: db db_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.db
    ADD CONSTRAINT db_name_key UNIQUE (name);


--
-- Name: db db_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.db
    ADD CONSTRAINT db_pkey PRIMARY KEY (db_id);


--
-- Name: dbxref dbxref_db_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dbxref
    ADD CONSTRAINT dbxref_db_id_key UNIQUE (db_id, accession, version);


--
-- Name: dbxref dbxref_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dbxref
    ADD CONSTRAINT dbxref_pkey PRIMARY KEY (dbxref_id);


--
-- Name: dbxrefprop dbxrefprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dbxrefprop
    ADD CONSTRAINT dbxrefprop_c1 UNIQUE (dbxref_id, type_id, rank);


--
-- Name: dbxrefprop dbxrefprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dbxrefprop
    ADD CONSTRAINT dbxrefprop_pkey PRIMARY KEY (dbxrefprop_id);


--
-- Name: eimage eimage_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eimage
    ADD CONSTRAINT eimage_pkey PRIMARY KEY (eimage_id);


--
-- Name: environment environment_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.environment
    ADD CONSTRAINT environment_c1 UNIQUE (uniquename);


--
-- Name: environment_cvterm environment_cvterm_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.environment_cvterm
    ADD CONSTRAINT environment_cvterm_c1 UNIQUE (environment_id, cvterm_id);


--
-- Name: environment_cvterm environment_cvterm_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.environment_cvterm
    ADD CONSTRAINT environment_cvterm_pkey PRIMARY KEY (environment_cvterm_id);


--
-- Name: environment environment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.environment
    ADD CONSTRAINT environment_pkey PRIMARY KEY (environment_id);


--
-- Name: expression expression_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expression
    ADD CONSTRAINT expression_c1 UNIQUE (uniquename);


--
-- Name: expression_cvterm expression_cvterm_expression_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expression_cvterm
    ADD CONSTRAINT expression_cvterm_expression_id_key UNIQUE (expression_id, cvterm_id, rank, cvterm_type_id);


--
-- Name: expression_cvterm expression_cvterm_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expression_cvterm
    ADD CONSTRAINT expression_cvterm_pkey PRIMARY KEY (expression_cvterm_id);


--
-- Name: expression_cvtermprop expression_cvtermprop_expression_cvterm_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expression_cvtermprop
    ADD CONSTRAINT expression_cvtermprop_expression_cvterm_id_key UNIQUE (expression_cvterm_id, type_id, rank);


--
-- Name: expression_cvtermprop expression_cvtermprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expression_cvtermprop
    ADD CONSTRAINT expression_cvtermprop_pkey PRIMARY KEY (expression_cvtermprop_id);


--
-- Name: expression_image expression_image_expression_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expression_image
    ADD CONSTRAINT expression_image_expression_id_key UNIQUE (expression_id, eimage_id);


--
-- Name: expression_image expression_image_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expression_image
    ADD CONSTRAINT expression_image_pkey PRIMARY KEY (expression_image_id);


--
-- Name: expression expression_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expression
    ADD CONSTRAINT expression_pkey PRIMARY KEY (expression_id);


--
-- Name: expression_pub expression_pub_expression_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expression_pub
    ADD CONSTRAINT expression_pub_expression_id_key UNIQUE (expression_id, pub_id);


--
-- Name: expression_pub expression_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expression_pub
    ADD CONSTRAINT expression_pub_pkey PRIMARY KEY (expression_pub_id);


--
-- Name: expressionprop expressionprop_expression_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expressionprop
    ADD CONSTRAINT expressionprop_expression_id_key UNIQUE (expression_id, type_id, rank);


--
-- Name: expressionprop expressionprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expressionprop
    ADD CONSTRAINT expressionprop_pkey PRIMARY KEY (expressionprop_id);


--
-- Name: feature_cvterm_dbxref feature_cvterm_dbxref_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_cvterm_dbxref
    ADD CONSTRAINT feature_cvterm_dbxref_c1 UNIQUE (feature_cvterm_id, dbxref_id);


--
-- Name: feature_cvterm_dbxref feature_cvterm_dbxref_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_cvterm_dbxref
    ADD CONSTRAINT feature_cvterm_dbxref_pkey PRIMARY KEY (feature_cvterm_dbxref_id);


--
-- Name: feature_cvterm feature_cvterm_feature_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_cvterm
    ADD CONSTRAINT feature_cvterm_feature_id_key UNIQUE (feature_id, cvterm_id, pub_id);


--
-- Name: feature_cvterm feature_cvterm_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_cvterm
    ADD CONSTRAINT feature_cvterm_pkey PRIMARY KEY (feature_cvterm_id);


--
-- Name: feature_cvtermprop feature_cvtermprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_cvtermprop
    ADD CONSTRAINT feature_cvtermprop_c1 UNIQUE (feature_cvterm_id, type_id, rank);


--
-- Name: feature_cvtermprop feature_cvtermprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_cvtermprop
    ADD CONSTRAINT feature_cvtermprop_pkey PRIMARY KEY (feature_cvtermprop_id);


--
-- Name: feature_dbxref feature_dbxref_feature_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_dbxref
    ADD CONSTRAINT feature_dbxref_feature_id_key UNIQUE (feature_id, dbxref_id);


--
-- Name: feature_dbxref feature_dbxref_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_dbxref
    ADD CONSTRAINT feature_dbxref_pkey PRIMARY KEY (feature_dbxref_id);


--
-- Name: feature_expression feature_expression_expression_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_expression
    ADD CONSTRAINT feature_expression_expression_id_key UNIQUE (expression_id, feature_id, pub_id);


--
-- Name: feature_expression feature_expression_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_expression
    ADD CONSTRAINT feature_expression_pkey PRIMARY KEY (feature_expression_id);


--
-- Name: feature_expressionprop feature_expressionprop_feature_expression_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_expressionprop
    ADD CONSTRAINT feature_expressionprop_feature_expression_id_key UNIQUE (feature_expression_id, type_id, rank);


--
-- Name: feature_expressionprop feature_expressionprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_expressionprop
    ADD CONSTRAINT feature_expressionprop_pkey PRIMARY KEY (feature_expressionprop_id);


--
-- Name: feature_genotype feature_genotype_feature_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_genotype
    ADD CONSTRAINT feature_genotype_feature_id_key UNIQUE (feature_id, genotype_id, cvterm_id, chromosome_id, rank, cgroup);


--
-- Name: feature_genotype feature_genotype_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_genotype
    ADD CONSTRAINT feature_genotype_pkey PRIMARY KEY (feature_genotype_id);


--
-- Name: feature_grpmember feature_grpmember_grpmember_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_grpmember
    ADD CONSTRAINT feature_grpmember_grpmember_id_key UNIQUE (grpmember_id, feature_id);


--
-- Name: feature_grpmember feature_grpmember_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_grpmember
    ADD CONSTRAINT feature_grpmember_pkey PRIMARY KEY (feature_grpmember_id);


--
-- Name: feature_grpmember_pub feature_grpmember_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_grpmember_pub
    ADD CONSTRAINT feature_grpmember_pub_pkey PRIMARY KEY (feature_grpmember_pub_id);


--
-- Name: feature_grpmember_pub feature_grpmember_pub_pub_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_grpmember_pub
    ADD CONSTRAINT feature_grpmember_pub_pub_id_key UNIQUE (pub_id, feature_grpmember_id);


--
-- Name: feature_humanhealth_dbxref feature_humanhealth_dbxref_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_humanhealth_dbxref
    ADD CONSTRAINT feature_humanhealth_dbxref_c1 UNIQUE (humanhealth_dbxref_id, feature_id, pub_id);


--
-- Name: feature_humanhealth_dbxref feature_humanhealth_dbxref_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_humanhealth_dbxref
    ADD CONSTRAINT feature_humanhealth_dbxref_pkey PRIMARY KEY (feature_humanhealth_dbxref_id);


--
-- Name: feature_interaction feature_interaction_feature_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_interaction
    ADD CONSTRAINT feature_interaction_feature_id_key UNIQUE (feature_id, interaction_id, role_id);


--
-- Name: feature_interaction feature_interaction_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_interaction
    ADD CONSTRAINT feature_interaction_pkey PRIMARY KEY (feature_interaction_id);


--
-- Name: feature_interaction_pub feature_interaction_pub_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_interaction_pub
    ADD CONSTRAINT feature_interaction_pub_c1 UNIQUE (feature_interaction_id, pub_id);


--
-- Name: feature_interaction_pub feature_interaction_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_interaction_pub
    ADD CONSTRAINT feature_interaction_pub_pkey PRIMARY KEY (feature_interaction_pub_id);


--
-- Name: feature_interactionprop feature_interactionprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_interactionprop
    ADD CONSTRAINT feature_interactionprop_c1 UNIQUE (feature_interaction_id, type_id, rank);


--
-- Name: feature_interactionprop feature_interactionprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_interactionprop
    ADD CONSTRAINT feature_interactionprop_pkey PRIMARY KEY (feature_interactionprop_id);


--
-- Name: feature feature_organism_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature
    ADD CONSTRAINT feature_organism_id_key UNIQUE (organism_id, uniquename, type_id);


--
-- Name: feature_phenotype feature_phenotype_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_phenotype
    ADD CONSTRAINT feature_phenotype_c1 UNIQUE (feature_id, phenotype_id);


--
-- Name: feature_phenotype feature_phenotype_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_phenotype
    ADD CONSTRAINT feature_phenotype_pkey PRIMARY KEY (feature_phenotype_id);


--
-- Name: feature feature_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature
    ADD CONSTRAINT feature_pkey PRIMARY KEY (feature_id);


--
-- Name: feature_pub feature_pub_feature_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_pub
    ADD CONSTRAINT feature_pub_feature_id_key UNIQUE (feature_id, pub_id);


--
-- Name: feature_pub feature_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_pub
    ADD CONSTRAINT feature_pub_pkey PRIMARY KEY (feature_pub_id);


--
-- Name: feature_pubprop feature_pubprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_pubprop
    ADD CONSTRAINT feature_pubprop_c1 UNIQUE (feature_pub_id, type_id, rank);


--
-- Name: feature_pubprop feature_pubprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_pubprop
    ADD CONSTRAINT feature_pubprop_pkey PRIMARY KEY (feature_pubprop_id);


--
-- Name: feature_relationship feature_relationship_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_relationship
    ADD CONSTRAINT feature_relationship_c1 UNIQUE (subject_id, object_id, type_id, rank);


--
-- Name: feature_relationship feature_relationship_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_relationship
    ADD CONSTRAINT feature_relationship_pkey PRIMARY KEY (feature_relationship_id);


--
-- Name: feature_relationship_pub feature_relationship_pub_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_relationship_pub
    ADD CONSTRAINT feature_relationship_pub_c1 UNIQUE (feature_relationship_id, pub_id);


--
-- Name: feature_relationship_pub feature_relationship_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_relationship_pub
    ADD CONSTRAINT feature_relationship_pub_pkey PRIMARY KEY (feature_relationship_pub_id);


--
-- Name: feature_relationshipprop feature_relationshipprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_relationshipprop
    ADD CONSTRAINT feature_relationshipprop_c1 UNIQUE (feature_relationship_id, type_id, rank);


--
-- Name: feature_relationshipprop feature_relationshipprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_relationshipprop
    ADD CONSTRAINT feature_relationshipprop_pkey PRIMARY KEY (feature_relationshipprop_id);


--
-- Name: feature_relationshipprop_pub feature_relationshipprop_pub_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_relationshipprop_pub
    ADD CONSTRAINT feature_relationshipprop_pub_c1 UNIQUE (feature_relationshipprop_id, pub_id);


--
-- Name: feature_relationshipprop_pub feature_relationshipprop_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_relationshipprop_pub
    ADD CONSTRAINT feature_relationshipprop_pub_pkey PRIMARY KEY (feature_relationshipprop_pub_id);


--
-- Name: feature_synonym feature_synonym_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_synonym
    ADD CONSTRAINT feature_synonym_pkey PRIMARY KEY (feature_synonym_id);


--
-- Name: feature_synonym feature_synonym_synonym_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_synonym
    ADD CONSTRAINT feature_synonym_synonym_id_key UNIQUE (synonym_id, feature_id, pub_id);


--
-- Name: featureloc featureloc_feature_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featureloc
    ADD CONSTRAINT featureloc_feature_id_key UNIQUE (feature_id, locgroup, rank);


--
-- Name: featureloc featureloc_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featureloc
    ADD CONSTRAINT featureloc_pkey PRIMARY KEY (featureloc_id);


--
-- Name: featureloc_pub featureloc_pub_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featureloc_pub
    ADD CONSTRAINT featureloc_pub_c1 UNIQUE (featureloc_id, pub_id);


--
-- Name: featureloc_pub featureloc_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featureloc_pub
    ADD CONSTRAINT featureloc_pub_pkey PRIMARY KEY (featureloc_pub_id);


--
-- Name: featuremap featuremap_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featuremap
    ADD CONSTRAINT featuremap_c1 UNIQUE (name);


--
-- Name: featuremap featuremap_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featuremap
    ADD CONSTRAINT featuremap_pkey PRIMARY KEY (featuremap_id);


--
-- Name: featuremap_pub featuremap_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featuremap_pub
    ADD CONSTRAINT featuremap_pub_pkey PRIMARY KEY (featuremap_pub_id);


--
-- Name: featurepos featurepos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featurepos
    ADD CONSTRAINT featurepos_pkey PRIMARY KEY (featurepos_id);


--
-- Name: featureprop featureprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featureprop
    ADD CONSTRAINT featureprop_c1 UNIQUE (feature_id, type_id, rank);


--
-- Name: featureprop featureprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featureprop
    ADD CONSTRAINT featureprop_pkey PRIMARY KEY (featureprop_id);


--
-- Name: featureprop_pub featureprop_pub_featureprop_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featureprop_pub
    ADD CONSTRAINT featureprop_pub_featureprop_id_key UNIQUE (featureprop_id, pub_id);


--
-- Name: featureprop_pub featureprop_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featureprop_pub
    ADD CONSTRAINT featureprop_pub_pkey PRIMARY KEY (featureprop_pub_id);


--
-- Name: featurerange featurerange_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featurerange
    ADD CONSTRAINT featurerange_pkey PRIMARY KEY (featurerange_id);


--
-- Name: genotype genotype_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genotype
    ADD CONSTRAINT genotype_c1 UNIQUE (uniquename);


--
-- Name: genotype genotype_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genotype
    ADD CONSTRAINT genotype_pkey PRIMARY KEY (genotype_id);


--
-- Name: grp_cvterm grp_cvterm_cvterm_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_cvterm
    ADD CONSTRAINT grp_cvterm_cvterm_id_key UNIQUE (cvterm_id, grp_id, pub_id);


--
-- Name: grp_cvterm grp_cvterm_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_cvterm
    ADD CONSTRAINT grp_cvterm_pkey PRIMARY KEY (grp_cvterm_id);


--
-- Name: grp_dbxref grp_dbxref_dbxref_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_dbxref
    ADD CONSTRAINT grp_dbxref_dbxref_id_key UNIQUE (dbxref_id, grp_id);


--
-- Name: grp_dbxref grp_dbxref_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_dbxref
    ADD CONSTRAINT grp_dbxref_pkey PRIMARY KEY (grp_dbxref_id);


--
-- Name: grp grp_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp
    ADD CONSTRAINT grp_pkey PRIMARY KEY (grp_id);


--
-- Name: grp_pub grp_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_pub
    ADD CONSTRAINT grp_pub_pkey PRIMARY KEY (grp_pub_id);


--
-- Name: grp_pub grp_pub_pub_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_pub
    ADD CONSTRAINT grp_pub_pub_id_key UNIQUE (pub_id, grp_id);


--
-- Name: grp_pubprop grp_pubprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_pubprop
    ADD CONSTRAINT grp_pubprop_pkey PRIMARY KEY (grp_pubprop_id);


--
-- Name: grp_pubprop grp_pubprop_rank_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_pubprop
    ADD CONSTRAINT grp_pubprop_rank_key UNIQUE (rank, type_id, grp_pub_id);


--
-- Name: grp_relationship grp_relationship_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_relationship
    ADD CONSTRAINT grp_relationship_pkey PRIMARY KEY (grp_relationship_id);


--
-- Name: grp_relationship_pub grp_relationship_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_relationship_pub
    ADD CONSTRAINT grp_relationship_pub_pkey PRIMARY KEY (grp_relationship_pub_id);


--
-- Name: grp_relationship_pub grp_relationship_pub_pub_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_relationship_pub
    ADD CONSTRAINT grp_relationship_pub_pub_id_key UNIQUE (pub_id, grp_relationship_id);


--
-- Name: grp_relationship grp_relationship_rank_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_relationship
    ADD CONSTRAINT grp_relationship_rank_key UNIQUE (rank, type_id, subject_id, object_id);


--
-- Name: grp_relationshipprop grp_relationshipprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_relationshipprop
    ADD CONSTRAINT grp_relationshipprop_pkey PRIMARY KEY (grp_relationshipprop_id);


--
-- Name: grp_relationshipprop grp_relationshipprop_rank_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_relationshipprop
    ADD CONSTRAINT grp_relationshipprop_rank_key UNIQUE (rank, type_id, grp_relationship_id);


--
-- Name: grp_synonym grp_synonym_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_synonym
    ADD CONSTRAINT grp_synonym_pkey PRIMARY KEY (grp_synonym_id);


--
-- Name: grp_synonym grp_synonym_synonym_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_synonym
    ADD CONSTRAINT grp_synonym_synonym_id_key UNIQUE (synonym_id, grp_id, pub_id);


--
-- Name: grp grp_uniquename_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp
    ADD CONSTRAINT grp_uniquename_key UNIQUE (uniquename, type_id);


--
-- Name: grpmember_cvterm grpmember_cvterm_cvterm_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmember_cvterm
    ADD CONSTRAINT grpmember_cvterm_cvterm_id_key UNIQUE (cvterm_id, grpmember_id, pub_id);


--
-- Name: grpmember_cvterm grpmember_cvterm_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmember_cvterm
    ADD CONSTRAINT grpmember_cvterm_pkey PRIMARY KEY (grpmember_cvterm_id);


--
-- Name: grpmember grpmember_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmember
    ADD CONSTRAINT grpmember_pkey PRIMARY KEY (grpmember_id);


--
-- Name: grpmember_pub grpmember_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmember_pub
    ADD CONSTRAINT grpmember_pub_pkey PRIMARY KEY (grpmember_pub_id);


--
-- Name: grpmember_pub grpmember_pub_pub_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmember_pub
    ADD CONSTRAINT grpmember_pub_pub_id_key UNIQUE (pub_id, grpmember_id);


--
-- Name: grpmember grpmember_rank_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmember
    ADD CONSTRAINT grpmember_rank_key UNIQUE (rank, type_id, grp_id);


--
-- Name: grpmemberprop grpmemberprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmemberprop
    ADD CONSTRAINT grpmemberprop_pkey PRIMARY KEY (grpmemberprop_id);


--
-- Name: grpmemberprop_pub grpmemberprop_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmemberprop_pub
    ADD CONSTRAINT grpmemberprop_pub_pkey PRIMARY KEY (grpmemberprop_pub_id);


--
-- Name: grpmemberprop_pub grpmemberprop_pub_pub_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmemberprop_pub
    ADD CONSTRAINT grpmemberprop_pub_pub_id_key UNIQUE (pub_id, grpmemberprop_id);


--
-- Name: grpmemberprop grpmemberprop_rank_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmemberprop
    ADD CONSTRAINT grpmemberprop_rank_key UNIQUE (rank, type_id, grpmember_id);


--
-- Name: grpprop grpprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpprop
    ADD CONSTRAINT grpprop_pkey PRIMARY KEY (grpprop_id);


--
-- Name: grpprop_pub grpprop_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpprop_pub
    ADD CONSTRAINT grpprop_pub_pkey PRIMARY KEY (grpprop_pub_id);


--
-- Name: grpprop_pub grpprop_pub_pub_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpprop_pub
    ADD CONSTRAINT grpprop_pub_pub_id_key UNIQUE (pub_id, grpprop_id);


--
-- Name: grpprop grpprop_rank_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpprop
    ADD CONSTRAINT grpprop_rank_key UNIQUE (rank, type_id, grp_id);


--
-- Name: humanhealth humanhealth_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth
    ADD CONSTRAINT humanhealth_c1 UNIQUE (organism_id, uniquename);


--
-- Name: humanhealth_cvterm humanhealth_cvterm_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_cvterm
    ADD CONSTRAINT humanhealth_cvterm_c1 UNIQUE (humanhealth_id, cvterm_id, pub_id);


--
-- Name: humanhealth_cvterm humanhealth_cvterm_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_cvterm
    ADD CONSTRAINT humanhealth_cvterm_pkey PRIMARY KEY (humanhealth_cvterm_id);


--
-- Name: humanhealth_cvtermprop humanhealth_cvtermprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_cvtermprop
    ADD CONSTRAINT humanhealth_cvtermprop_c1 UNIQUE (humanhealth_cvterm_id, type_id, rank);


--
-- Name: humanhealth_cvtermprop humanhealth_cvtermprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_cvtermprop
    ADD CONSTRAINT humanhealth_cvtermprop_pkey PRIMARY KEY (humanhealth_cvtermprop_id);


--
-- Name: humanhealth_dbxref humanhealth_dbxref_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_dbxref
    ADD CONSTRAINT humanhealth_dbxref_c1 UNIQUE (humanhealth_id, dbxref_id);


--
-- Name: humanhealth_dbxref humanhealth_dbxref_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_dbxref
    ADD CONSTRAINT humanhealth_dbxref_pkey PRIMARY KEY (humanhealth_dbxref_id);


--
-- Name: humanhealth_dbxrefprop humanhealth_dbxrefprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_dbxrefprop
    ADD CONSTRAINT humanhealth_dbxrefprop_c1 UNIQUE (humanhealth_dbxref_id, type_id, rank);


--
-- Name: humanhealth_dbxrefprop humanhealth_dbxrefprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_dbxrefprop
    ADD CONSTRAINT humanhealth_dbxrefprop_pkey PRIMARY KEY (humanhealth_dbxrefprop_id);


--
-- Name: humanhealth_dbxrefprop_pub humanhealth_dbxrefprop_pub_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_dbxrefprop_pub
    ADD CONSTRAINT humanhealth_dbxrefprop_pub_c1 UNIQUE (humanhealth_dbxrefprop_id, pub_id);


--
-- Name: humanhealth_dbxrefprop_pub humanhealth_dbxrefprop_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_dbxrefprop_pub
    ADD CONSTRAINT humanhealth_dbxrefprop_pub_pkey PRIMARY KEY (humanhealth_dbxrefprop_pub_id);


--
-- Name: humanhealth_feature humanhealth_feature_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_feature
    ADD CONSTRAINT humanhealth_feature_c1 UNIQUE (humanhealth_id, feature_id, pub_id);


--
-- Name: humanhealth_feature humanhealth_feature_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_feature
    ADD CONSTRAINT humanhealth_feature_pkey PRIMARY KEY (humanhealth_feature_id);


--
-- Name: humanhealth_featureprop humanhealth_featureprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_featureprop
    ADD CONSTRAINT humanhealth_featureprop_c1 UNIQUE (humanhealth_feature_id, type_id, rank);


--
-- Name: humanhealth_featureprop humanhealth_featureprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_featureprop
    ADD CONSTRAINT humanhealth_featureprop_pkey PRIMARY KEY (humanhealth_featureprop_id);


--
-- Name: humanhealth_phenotype humanhealth_phenotype_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_phenotype
    ADD CONSTRAINT humanhealth_phenotype_c1 UNIQUE (humanhealth_id, phenotype_id, pub_id);


--
-- Name: humanhealth_phenotype humanhealth_phenotype_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_phenotype
    ADD CONSTRAINT humanhealth_phenotype_pkey PRIMARY KEY (humanhealth_phenotype_id);


--
-- Name: humanhealth_phenotypeprop humanhealth_phenotypeprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_phenotypeprop
    ADD CONSTRAINT humanhealth_phenotypeprop_c1 UNIQUE (humanhealth_phenotype_id, type_id, rank);


--
-- Name: humanhealth_phenotypeprop humanhealth_phenotypeprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_phenotypeprop
    ADD CONSTRAINT humanhealth_phenotypeprop_pkey PRIMARY KEY (humanhealth_phenotypeprop_id);


--
-- Name: humanhealth humanhealth_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth
    ADD CONSTRAINT humanhealth_pkey PRIMARY KEY (humanhealth_id);


--
-- Name: humanhealth_pub humanhealth_pub_humanhealth_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_pub
    ADD CONSTRAINT humanhealth_pub_humanhealth_id_key UNIQUE (humanhealth_id, pub_id);


--
-- Name: humanhealth_pub humanhealth_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_pub
    ADD CONSTRAINT humanhealth_pub_pkey PRIMARY KEY (humanhealth_pub_id);


--
-- Name: humanhealth_pubprop humanhealth_pubprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_pubprop
    ADD CONSTRAINT humanhealth_pubprop_pkey PRIMARY KEY (humanhealth_pubprop_id);


--
-- Name: humanhealth_pubprop humanhealth_pubprop_rank_type_id_humanhealth_pub_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_pubprop
    ADD CONSTRAINT humanhealth_pubprop_rank_type_id_humanhealth_pub_id_key UNIQUE (rank, type_id, humanhealth_pub_id);


--
-- Name: humanhealth_relationship humanhealth_relationship_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_relationship
    ADD CONSTRAINT humanhealth_relationship_c1 UNIQUE (subject_id, object_id, type_id, rank);


--
-- Name: humanhealth_relationship humanhealth_relationship_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_relationship
    ADD CONSTRAINT humanhealth_relationship_pkey PRIMARY KEY (humanhealth_relationship_id);


--
-- Name: humanhealth_relationship_pub humanhealth_relationship_pub_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_relationship_pub
    ADD CONSTRAINT humanhealth_relationship_pub_c1 UNIQUE (humanhealth_relationship_id, pub_id);


--
-- Name: humanhealth_relationship_pub humanhealth_relationship_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_relationship_pub
    ADD CONSTRAINT humanhealth_relationship_pub_pkey PRIMARY KEY (humanhealth_relationship_pub_id);


--
-- Name: humanhealth_synonym humanhealth_synonym_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_synonym
    ADD CONSTRAINT humanhealth_synonym_c1 UNIQUE (synonym_id, humanhealth_id, pub_id);


--
-- Name: humanhealth_synonym humanhealth_synonym_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_synonym
    ADD CONSTRAINT humanhealth_synonym_pkey PRIMARY KEY (humanhealth_synonym_id);


--
-- Name: humanhealthprop humanhealthprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealthprop
    ADD CONSTRAINT humanhealthprop_c1 UNIQUE (humanhealth_id, type_id, rank);


--
-- Name: humanhealthprop humanhealthprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealthprop
    ADD CONSTRAINT humanhealthprop_pkey PRIMARY KEY (humanhealthprop_id);


--
-- Name: humanhealthprop_pub humanhealthprop_pub_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealthprop_pub
    ADD CONSTRAINT humanhealthprop_pub_c1 UNIQUE (humanhealthprop_id, pub_id);


--
-- Name: humanhealthprop_pub humanhealthprop_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealthprop_pub
    ADD CONSTRAINT humanhealthprop_pub_pkey PRIMARY KEY (humanhealthprop_pub_id);


--
-- Name: interaction interaction_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction
    ADD CONSTRAINT interaction_c1 UNIQUE (uniquename, type_id);


--
-- Name: interaction_cell_line interaction_cell_line_cell_line_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_cell_line
    ADD CONSTRAINT interaction_cell_line_cell_line_id_key UNIQUE (cell_line_id, interaction_id, pub_id);


--
-- Name: interaction_cell_line interaction_cell_line_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_cell_line
    ADD CONSTRAINT interaction_cell_line_pkey PRIMARY KEY (interaction_cell_line_id);


--
-- Name: interaction_cvterm interaction_cvterm_interaction_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_cvterm
    ADD CONSTRAINT interaction_cvterm_interaction_id_key UNIQUE (interaction_id, cvterm_id);


--
-- Name: interaction_cvterm interaction_cvterm_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_cvterm
    ADD CONSTRAINT interaction_cvterm_pkey PRIMARY KEY (interaction_cvterm_id);


--
-- Name: interaction_cvtermprop interaction_cvtermprop_interaction_cvterm_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_cvtermprop
    ADD CONSTRAINT interaction_cvtermprop_interaction_cvterm_id_key UNIQUE (interaction_cvterm_id, type_id, rank);


--
-- Name: interaction_cvtermprop interaction_cvtermprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_cvtermprop
    ADD CONSTRAINT interaction_cvtermprop_pkey PRIMARY KEY (interaction_cvtermprop_id);


--
-- Name: interaction_expression interaction_expression_expression_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_expression
    ADD CONSTRAINT interaction_expression_expression_id_key UNIQUE (expression_id, interaction_id, pub_id);


--
-- Name: interaction_expression interaction_expression_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_expression
    ADD CONSTRAINT interaction_expression_pkey PRIMARY KEY (interaction_expression_id);


--
-- Name: interaction_expressionprop interaction_expressionprop_interaction_expression_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_expressionprop
    ADD CONSTRAINT interaction_expressionprop_interaction_expression_id_key UNIQUE (interaction_expression_id, type_id, rank);


--
-- Name: interaction_expressionprop interaction_expressionprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_expressionprop
    ADD CONSTRAINT interaction_expressionprop_pkey PRIMARY KEY (interaction_expressionprop_id);


--
-- Name: interaction_group interaction_group_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_group
    ADD CONSTRAINT interaction_group_c1 UNIQUE (uniquename);


--
-- Name: interaction_group_feature_interaction interaction_group_feature_interaction_interaction_group_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_group_feature_interaction
    ADD CONSTRAINT interaction_group_feature_interaction_interaction_group_id_key UNIQUE (interaction_group_id, feature_interaction_id, rank);


--
-- Name: interaction_group_feature_interaction interaction_group_feature_interaction_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_group_feature_interaction
    ADD CONSTRAINT interaction_group_feature_interaction_pkey PRIMARY KEY (interaction_group_feature_interaction_id);


--
-- Name: interaction_group interaction_group_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_group
    ADD CONSTRAINT interaction_group_pkey PRIMARY KEY (interaction_group_id);


--
-- Name: interaction interaction_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction
    ADD CONSTRAINT interaction_pkey PRIMARY KEY (interaction_id);


--
-- Name: interaction_pub interaction_pub_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_pub
    ADD CONSTRAINT interaction_pub_c1 UNIQUE (interaction_id, pub_id);


--
-- Name: interaction_pub interaction_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_pub
    ADD CONSTRAINT interaction_pub_pkey PRIMARY KEY (interaction_pub_id);


--
-- Name: interactionprop interactionprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interactionprop
    ADD CONSTRAINT interactionprop_c1 UNIQUE (interaction_id, type_id, rank);


--
-- Name: interactionprop interactionprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interactionprop
    ADD CONSTRAINT interactionprop_pkey PRIMARY KEY (interactionprop_id);


--
-- Name: interactionprop_pub interactionprop_pub_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interactionprop_pub
    ADD CONSTRAINT interactionprop_pub_c1 UNIQUE (interactionprop_id, pub_id);


--
-- Name: interactionprop_pub interactionprop_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interactionprop_pub
    ADD CONSTRAINT interactionprop_pub_pkey PRIMARY KEY (interactionprop_pub_id);


--
-- Name: library library_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library
    ADD CONSTRAINT library_c1 UNIQUE (organism_id, uniquename, type_id);


--
-- Name: library_cvterm library_cvterm_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_cvterm
    ADD CONSTRAINT library_cvterm_c1 UNIQUE (library_id, cvterm_id, pub_id);


--
-- Name: library_cvterm library_cvterm_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_cvterm
    ADD CONSTRAINT library_cvterm_pkey PRIMARY KEY (library_cvterm_id);


--
-- Name: library_cvtermprop library_cvtermprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_cvtermprop
    ADD CONSTRAINT library_cvtermprop_c1 UNIQUE (library_cvterm_id, type_id, rank);


--
-- Name: library_cvtermprop library_cvtermprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_cvtermprop
    ADD CONSTRAINT library_cvtermprop_pkey PRIMARY KEY (library_cvtermprop_id);


--
-- Name: library_dbxref library_dbxref_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_dbxref
    ADD CONSTRAINT library_dbxref_c1 UNIQUE (library_id, dbxref_id);


--
-- Name: library_dbxref library_dbxref_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_dbxref
    ADD CONSTRAINT library_dbxref_pkey PRIMARY KEY (library_dbxref_id);


--
-- Name: library_dbxrefprop library_dbxrefprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_dbxrefprop
    ADD CONSTRAINT library_dbxrefprop_c1 UNIQUE (library_dbxref_id, type_id, rank);


--
-- Name: library_dbxrefprop library_dbxrefprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_dbxrefprop
    ADD CONSTRAINT library_dbxrefprop_pkey PRIMARY KEY (library_dbxrefprop_id);


--
-- Name: library_expression library_expression_expression_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_expression
    ADD CONSTRAINT library_expression_expression_id_key UNIQUE (expression_id, library_id, pub_id);


--
-- Name: library_expression library_expression_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_expression
    ADD CONSTRAINT library_expression_pkey PRIMARY KEY (library_expression_id);


--
-- Name: library_expressionprop library_expressionprop_library_expression_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_expressionprop
    ADD CONSTRAINT library_expressionprop_library_expression_id_key UNIQUE (library_expression_id, type_id, rank);


--
-- Name: library_expressionprop library_expressionprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_expressionprop
    ADD CONSTRAINT library_expressionprop_pkey PRIMARY KEY (library_expressionprop_id);


--
-- Name: library_feature library_feature_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_feature
    ADD CONSTRAINT library_feature_c1 UNIQUE (library_id, feature_id);


--
-- Name: library_feature library_feature_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_feature
    ADD CONSTRAINT library_feature_pkey PRIMARY KEY (library_feature_id);


--
-- Name: library_featureprop library_featureprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_featureprop
    ADD CONSTRAINT library_featureprop_c1 UNIQUE (library_feature_id, type_id, rank);


--
-- Name: library_featureprop library_featureprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_featureprop
    ADD CONSTRAINT library_featureprop_pkey PRIMARY KEY (library_featureprop_id);


--
-- Name: library_grpmember library_grpmember_grpmember_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_grpmember
    ADD CONSTRAINT library_grpmember_grpmember_id_key UNIQUE (grpmember_id, library_id);


--
-- Name: library_grpmember library_grpmember_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_grpmember
    ADD CONSTRAINT library_grpmember_pkey PRIMARY KEY (library_grpmember_id);


--
-- Name: library_humanhealth library_humanhealth_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_humanhealth
    ADD CONSTRAINT library_humanhealth_c1 UNIQUE (humanhealth_id, library_id, pub_id);


--
-- Name: library_humanhealth library_humanhealth_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_humanhealth
    ADD CONSTRAINT library_humanhealth_pkey PRIMARY KEY (library_humanhealth_id);


--
-- Name: library_humanhealthprop library_humanhealthprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_humanhealthprop
    ADD CONSTRAINT library_humanhealthprop_c1 UNIQUE (library_humanhealth_id, type_id, rank);


--
-- Name: library_humanhealthprop library_humanhealthprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_humanhealthprop
    ADD CONSTRAINT library_humanhealthprop_pkey PRIMARY KEY (library_humanhealthprop_id);


--
-- Name: library_interaction library_interaction_interaction_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_interaction
    ADD CONSTRAINT library_interaction_interaction_id_key UNIQUE (interaction_id, library_id, pub_id);


--
-- Name: library_interaction library_interaction_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_interaction
    ADD CONSTRAINT library_interaction_pkey PRIMARY KEY (library_interaction_id);


--
-- Name: library library_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library
    ADD CONSTRAINT library_pkey PRIMARY KEY (library_id);


--
-- Name: library_pub library_pub_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_pub
    ADD CONSTRAINT library_pub_c1 UNIQUE (library_id, pub_id);


--
-- Name: library_pub library_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_pub
    ADD CONSTRAINT library_pub_pkey PRIMARY KEY (library_pub_id);


--
-- Name: library_relationship library_relationship_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_relationship
    ADD CONSTRAINT library_relationship_c1 UNIQUE (subject_id, object_id, type_id);


--
-- Name: library_relationship library_relationship_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_relationship
    ADD CONSTRAINT library_relationship_pkey PRIMARY KEY (library_relationship_id);


--
-- Name: library_relationship_pub library_relationship_pub_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_relationship_pub
    ADD CONSTRAINT library_relationship_pub_c1 UNIQUE (library_relationship_id, pub_id);


--
-- Name: library_relationship_pub library_relationship_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_relationship_pub
    ADD CONSTRAINT library_relationship_pub_pkey PRIMARY KEY (library_relationship_pub_id);


--
-- Name: library_strain library_strain_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_strain
    ADD CONSTRAINT library_strain_c1 UNIQUE (strain_id, library_id, pub_id);


--
-- Name: library_strain library_strain_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_strain
    ADD CONSTRAINT library_strain_pkey PRIMARY KEY (library_strain_id);


--
-- Name: library_strainprop library_strainprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_strainprop
    ADD CONSTRAINT library_strainprop_c1 UNIQUE (library_strain_id, type_id, rank);


--
-- Name: library_strainprop library_strainprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_strainprop
    ADD CONSTRAINT library_strainprop_pkey PRIMARY KEY (library_strainprop_id);


--
-- Name: library_synonym library_synonym_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_synonym
    ADD CONSTRAINT library_synonym_c1 UNIQUE (synonym_id, library_id, pub_id);


--
-- Name: library_synonym library_synonym_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_synonym
    ADD CONSTRAINT library_synonym_pkey PRIMARY KEY (library_synonym_id);


--
-- Name: libraryprop libraryprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.libraryprop
    ADD CONSTRAINT libraryprop_c1 UNIQUE (library_id, type_id, rank);


--
-- Name: libraryprop libraryprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.libraryprop
    ADD CONSTRAINT libraryprop_pkey PRIMARY KEY (libraryprop_id);


--
-- Name: libraryprop_pub libraryprop_pub_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.libraryprop_pub
    ADD CONSTRAINT libraryprop_pub_c1 UNIQUE (libraryprop_id, pub_id);


--
-- Name: libraryprop_pub libraryprop_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.libraryprop_pub
    ADD CONSTRAINT libraryprop_pub_pkey PRIMARY KEY (libraryprop_pub_id);


--
-- Name: lock lock_lockname_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lock
    ADD CONSTRAINT lock_lockname_key UNIQUE (lockname, lockrank, locktype);


--
-- Name: lock lock_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lock
    ADD CONSTRAINT lock_pkey PRIMARY KEY (lock_id);


--
-- Name: organism_cvterm organism_cvterm_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_cvterm
    ADD CONSTRAINT organism_cvterm_c1 UNIQUE (organism_id, cvterm_id, pub_id, rank);


--
-- Name: organism_cvterm organism_cvterm_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_cvterm
    ADD CONSTRAINT organism_cvterm_pkey PRIMARY KEY (organism_cvterm_id);


--
-- Name: organism_cvtermprop organism_cvtermprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_cvtermprop
    ADD CONSTRAINT organism_cvtermprop_c1 UNIQUE (organism_cvterm_id, type_id, rank);


--
-- Name: organism_cvtermprop organism_cvtermprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_cvtermprop
    ADD CONSTRAINT organism_cvtermprop_pkey PRIMARY KEY (organism_cvtermprop_id);


--
-- Name: organism_dbxref organism_dbxref_organism_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_dbxref
    ADD CONSTRAINT organism_dbxref_organism_id_key UNIQUE (organism_id, dbxref_id);


--
-- Name: organism_dbxref organism_dbxref_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_dbxref
    ADD CONSTRAINT organism_dbxref_pkey PRIMARY KEY (organism_dbxref_id);


--
-- Name: organism organism_genus_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism
    ADD CONSTRAINT organism_genus_key UNIQUE (genus, species);


--
-- Name: organism_grpmember organism_grpmember_grpmember_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_grpmember
    ADD CONSTRAINT organism_grpmember_grpmember_id_key UNIQUE (grpmember_id, organism_id);


--
-- Name: organism_grpmember organism_grpmember_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_grpmember
    ADD CONSTRAINT organism_grpmember_pkey PRIMARY KEY (organism_grpmember_id);


--
-- Name: organism_library organism_library_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_library
    ADD CONSTRAINT organism_library_c1 UNIQUE (organism_id, library_id);


--
-- Name: organism_library organism_library_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_library
    ADD CONSTRAINT organism_library_pkey PRIMARY KEY (organism_library_id);


--
-- Name: organism organism_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism
    ADD CONSTRAINT organism_pkey PRIMARY KEY (organism_id);


--
-- Name: organism_pub organism_pub_organism_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_pub
    ADD CONSTRAINT organism_pub_organism_id_key UNIQUE (organism_id, pub_id);


--
-- Name: organism_pub organism_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_pub
    ADD CONSTRAINT organism_pub_pkey PRIMARY KEY (organism_pub_id);


--
-- Name: organismprop organismprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organismprop
    ADD CONSTRAINT organismprop_c1 UNIQUE (organism_id, type_id, rank);


--
-- Name: organismprop organismprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organismprop
    ADD CONSTRAINT organismprop_pkey PRIMARY KEY (organismprop_id);


--
-- Name: organismprop_pub organismprop_pub_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organismprop_pub
    ADD CONSTRAINT organismprop_pub_c1 UNIQUE (organismprop_id, pub_id);


--
-- Name: organismprop_pub organismprop_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organismprop_pub
    ADD CONSTRAINT organismprop_pub_pkey PRIMARY KEY (organismprop_pub_id);


--
-- Name: phendesc phendesc_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phendesc
    ADD CONSTRAINT phendesc_c1 UNIQUE (genotype_id, environment_id, type_id, pub_id);


--
-- Name: phendesc phendesc_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phendesc
    ADD CONSTRAINT phendesc_pkey PRIMARY KEY (phendesc_id);


--
-- Name: phenotype phenotype_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype
    ADD CONSTRAINT phenotype_c1 UNIQUE (uniquename);


--
-- Name: phenotype_comparison phenotype_comparison_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype_comparison
    ADD CONSTRAINT phenotype_comparison_c1 UNIQUE (genotype1_id, environment1_id, genotype2_id, environment2_id, phenotype1_id, pub_id);


--
-- Name: phenotype_comparison_cvterm phenotype_comparison_cvterm_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype_comparison_cvterm
    ADD CONSTRAINT phenotype_comparison_cvterm_c1 UNIQUE (phenotype_comparison_id, cvterm_id);


--
-- Name: phenotype_comparison_cvterm phenotype_comparison_cvterm_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype_comparison_cvterm
    ADD CONSTRAINT phenotype_comparison_cvterm_pkey PRIMARY KEY (phenotype_comparison_cvterm_id);


--
-- Name: phenotype_comparison phenotype_comparison_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype_comparison
    ADD CONSTRAINT phenotype_comparison_pkey PRIMARY KEY (phenotype_comparison_id);


--
-- Name: phenotype_cvterm phenotype_cvterm_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype_cvterm
    ADD CONSTRAINT phenotype_cvterm_c1 UNIQUE (phenotype_id, cvterm_id, rank);


--
-- Name: phenotype_cvterm phenotype_cvterm_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype_cvterm
    ADD CONSTRAINT phenotype_cvterm_pkey PRIMARY KEY (phenotype_cvterm_id);


--
-- Name: phenotype phenotype_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype
    ADD CONSTRAINT phenotype_pkey PRIMARY KEY (phenotype_id);


--
-- Name: phenstatement phenstatement_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenstatement
    ADD CONSTRAINT phenstatement_c1 UNIQUE (genotype_id, phenotype_id, environment_id, type_id, pub_id);


--
-- Name: phenstatement phenstatement_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenstatement
    ADD CONSTRAINT phenstatement_pkey PRIMARY KEY (phenstatement_id);


--
-- Name: project project_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project
    ADD CONSTRAINT project_c1 UNIQUE (name);


--
-- Name: project project_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project
    ADD CONSTRAINT project_pkey PRIMARY KEY (project_id);


--
-- Name: pub_dbxref pub_dbxref_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pub_dbxref
    ADD CONSTRAINT pub_dbxref_pkey PRIMARY KEY (pub_dbxref_id);


--
-- Name: pub_dbxref pub_dbxref_pub_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pub_dbxref
    ADD CONSTRAINT pub_dbxref_pub_id_key UNIQUE (pub_id, dbxref_id);


--
-- Name: pub pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pub
    ADD CONSTRAINT pub_pkey PRIMARY KEY (pub_id);


--
-- Name: pub_relationship pub_relationship_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pub_relationship
    ADD CONSTRAINT pub_relationship_c1 UNIQUE (subject_id, object_id, type_id);


--
-- Name: pub_relationship pub_relationship_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pub_relationship
    ADD CONSTRAINT pub_relationship_pkey PRIMARY KEY (pub_relationship_id);


--
-- Name: pub pub_unique_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pub
    ADD CONSTRAINT pub_unique_key UNIQUE (uniquename);


--
-- Name: pubauthor pubauthor_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pubauthor
    ADD CONSTRAINT pubauthor_c1 UNIQUE (pub_id, rank);


--
-- Name: pubauthor pubauthor_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pubauthor
    ADD CONSTRAINT pubauthor_pkey PRIMARY KEY (pubauthor_id);


--
-- Name: pubprop pubprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pubprop
    ADD CONSTRAINT pubprop_pkey PRIMARY KEY (pubprop_id);


--
-- Name: pubprop pubprop_pub_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pubprop
    ADD CONSTRAINT pubprop_pub_id_key UNIQUE (pub_id, type_id, rank);


--
-- Name: strain strain_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain
    ADD CONSTRAINT strain_c1 UNIQUE (organism_id, uniquename);


--
-- Name: strain_cvterm strain_cvterm_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_cvterm
    ADD CONSTRAINT strain_cvterm_c1 UNIQUE (strain_id, cvterm_id, pub_id);


--
-- Name: strain_cvterm strain_cvterm_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_cvterm
    ADD CONSTRAINT strain_cvterm_pkey PRIMARY KEY (strain_cvterm_id);


--
-- Name: strain_cvtermprop strain_cvtermprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_cvtermprop
    ADD CONSTRAINT strain_cvtermprop_c1 UNIQUE (strain_cvterm_id, type_id, rank);


--
-- Name: strain_cvtermprop strain_cvtermprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_cvtermprop
    ADD CONSTRAINT strain_cvtermprop_pkey PRIMARY KEY (strain_cvtermprop_id);


--
-- Name: strain_dbxref strain_dbxref_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_dbxref
    ADD CONSTRAINT strain_dbxref_c1 UNIQUE (strain_id, dbxref_id);


--
-- Name: strain_dbxref strain_dbxref_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_dbxref
    ADD CONSTRAINT strain_dbxref_pkey PRIMARY KEY (strain_dbxref_id);


--
-- Name: strain_feature strain_feature_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_feature
    ADD CONSTRAINT strain_feature_c1 UNIQUE (strain_id, feature_id, pub_id);


--
-- Name: strain_feature strain_feature_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_feature
    ADD CONSTRAINT strain_feature_pkey PRIMARY KEY (strain_feature_id);


--
-- Name: strain_featureprop strain_featureprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_featureprop
    ADD CONSTRAINT strain_featureprop_c1 UNIQUE (strain_feature_id, type_id, rank);


--
-- Name: strain_featureprop strain_featureprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_featureprop
    ADD CONSTRAINT strain_featureprop_pkey PRIMARY KEY (strain_featureprop_id);


--
-- Name: strain_phenotype strain_phenotype_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_phenotype
    ADD CONSTRAINT strain_phenotype_c1 UNIQUE (strain_id, phenotype_id, pub_id);


--
-- Name: strain_phenotype strain_phenotype_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_phenotype
    ADD CONSTRAINT strain_phenotype_pkey PRIMARY KEY (strain_phenotype_id);


--
-- Name: strain_phenotypeprop strain_phenotypeprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_phenotypeprop
    ADD CONSTRAINT strain_phenotypeprop_c1 UNIQUE (strain_phenotype_id, type_id, rank);


--
-- Name: strain_phenotypeprop strain_phenotypeprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_phenotypeprop
    ADD CONSTRAINT strain_phenotypeprop_pkey PRIMARY KEY (strain_phenotypeprop_id);


--
-- Name: strain strain_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain
    ADD CONSTRAINT strain_pkey PRIMARY KEY (strain_id);


--
-- Name: strain_pub strain_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_pub
    ADD CONSTRAINT strain_pub_pkey PRIMARY KEY (strain_pub_id);


--
-- Name: strain_pub strain_pub_strain_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_pub
    ADD CONSTRAINT strain_pub_strain_id_key UNIQUE (strain_id, pub_id);


--
-- Name: strain_relationship strain_relationship_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_relationship
    ADD CONSTRAINT strain_relationship_c1 UNIQUE (subject_id, object_id, type_id, rank);


--
-- Name: strain_relationship strain_relationship_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_relationship
    ADD CONSTRAINT strain_relationship_pkey PRIMARY KEY (strain_relationship_id);


--
-- Name: strain_relationship_pub strain_relationship_pub_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_relationship_pub
    ADD CONSTRAINT strain_relationship_pub_c1 UNIQUE (strain_relationship_id, pub_id);


--
-- Name: strain_relationship_pub strain_relationship_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_relationship_pub
    ADD CONSTRAINT strain_relationship_pub_pkey PRIMARY KEY (strain_relationship_pub_id);


--
-- Name: strain_synonym strain_synonym_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_synonym
    ADD CONSTRAINT strain_synonym_c1 UNIQUE (synonym_id, strain_id, pub_id);


--
-- Name: strain_synonym strain_synonym_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_synonym
    ADD CONSTRAINT strain_synonym_pkey PRIMARY KEY (strain_synonym_id);


--
-- Name: strainprop strainprop_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strainprop
    ADD CONSTRAINT strainprop_c1 UNIQUE (strain_id, type_id, rank);


--
-- Name: strainprop strainprop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strainprop
    ADD CONSTRAINT strainprop_pkey PRIMARY KEY (strainprop_id);


--
-- Name: strainprop_pub strainprop_pub_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strainprop_pub
    ADD CONSTRAINT strainprop_pub_c1 UNIQUE (strainprop_id, pub_id);


--
-- Name: strainprop_pub strainprop_pub_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strainprop_pub
    ADD CONSTRAINT strainprop_pub_pkey PRIMARY KEY (strainprop_pub_id);


--
-- Name: synonym synonym_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.synonym
    ADD CONSTRAINT synonym_pkey PRIMARY KEY (synonym_id);


--
-- Name: synonym synonym_s1_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.synonym
    ADD CONSTRAINT synonym_s1_unique UNIQUE (name, type_id, synonym_sgml);


--
-- Name: tableinfo tableinfo_c1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tableinfo
    ADD CONSTRAINT tableinfo_c1 UNIQUE (name);


--
-- Name: tableinfo tableinfo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tableinfo
    ADD CONSTRAINT tableinfo_pkey PRIMARY KEY (tableinfo_id);


--
-- Name: update_track update_track_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.update_track
    ADD CONSTRAINT update_track_pkey PRIMARY KEY (update_track_id);


--
-- Name: analysis_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX analysis_idx1 ON public.analysis USING btree (sourcename);


--
-- Name: analysisfeature_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX analysisfeature_idx1 ON public.analysisfeature USING btree (feature_id);


--
-- Name: analysisfeature_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX analysisfeature_idx2 ON public.analysisfeature USING btree (analysis_id);


--
-- Name: analysisgrp_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX analysisgrp_idx1 ON public.analysisgrp USING btree (grp_id);


--
-- Name: analysisgrp_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX analysisgrp_idx2 ON public.analysisgrp USING btree (analysis_id);


--
-- Name: analysisgrpmember_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX analysisgrpmember_idx1 ON public.analysisgrpmember USING btree (grpmember_id);


--
-- Name: analysisgrpmember_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX analysisgrpmember_idx2 ON public.analysisgrpmember USING btree (analysis_id);


--
-- Name: analysisprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX analysisprop_idx1 ON public.analysisprop USING btree (analysis_id);


--
-- Name: analysisprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX analysisprop_idx2 ON public.analysisprop USING btree (type_id);


--
-- Name: binloc_boxrange; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX binloc_boxrange ON public.featureloc USING gist (public.boxrange(fmin, fmax));


--
-- Name: binloc_boxrange_src; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX binloc_boxrange_src ON public.featureloc USING gist (public.boxrange(srcfeature_id, fmin, fmax));


--
-- Name: cell_line_libraryprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX cell_line_libraryprop_idx1 ON public.cell_line_libraryprop USING btree (cell_line_library_id);


--
-- Name: cell_line_libraryprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX cell_line_libraryprop_idx2 ON public.cell_line_libraryprop USING btree (type_id);


--
-- Name: cell_line_strain_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX cell_line_strain_idx1 ON public.cell_line_strain USING btree (strain_id);


--
-- Name: cell_line_strain_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX cell_line_strain_idx2 ON public.cell_line_strain USING btree (cell_line_id);


--
-- Name: cell_line_strainprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX cell_line_strainprop_idx1 ON public.cell_line_strainprop USING btree (cell_line_strain_id);


--
-- Name: cell_line_strainprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX cell_line_strainprop_idx2 ON public.cell_line_strainprop USING btree (type_id);


--
-- Name: cvterm_dbxref_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX cvterm_dbxref_idx1 ON public.cvterm_dbxref USING btree (cvterm_id);


--
-- Name: cvterm_dbxref_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX cvterm_dbxref_idx2 ON public.cvterm_dbxref USING btree (dbxref_id);


--
-- Name: cvterm_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX cvterm_idx1 ON public.cvterm USING btree (cv_id);


--
-- Name: cvterm_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX cvterm_idx2 ON public.cvterm USING btree (name);


--
-- Name: cvterm_relationship_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX cvterm_relationship_idx1 ON public.cvterm_relationship USING btree (type_id);


--
-- Name: cvterm_relationship_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX cvterm_relationship_idx2 ON public.cvterm_relationship USING btree (subject_id);


--
-- Name: cvterm_relationship_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX cvterm_relationship_idx3 ON public.cvterm_relationship USING btree (object_id);


--
-- Name: cvtermpath_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX cvtermpath_idx1 ON public.cvtermpath USING btree (type_id);


--
-- Name: cvtermpath_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX cvtermpath_idx2 ON public.cvtermpath USING btree (subject_id);


--
-- Name: cvtermpath_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX cvtermpath_idx3 ON public.cvtermpath USING btree (object_id);


--
-- Name: cvtermpath_idx4; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX cvtermpath_idx4 ON public.cvtermpath USING btree (cv_id);


--
-- Name: cvtermprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX cvtermprop_idx1 ON public.cvtermprop USING btree (cvterm_id);


--
-- Name: cvtermprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX cvtermprop_idx2 ON public.cvtermprop USING btree (type_id);


--
-- Name: dbxref_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dbxref_idx1 ON public.dbxref USING btree (db_id);


--
-- Name: dbxref_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dbxref_idx2 ON public.dbxref USING btree (accession);


--
-- Name: dbxref_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dbxref_idx3 ON public.dbxref USING btree (version);


--
-- Name: dbxrefprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dbxrefprop_idx1 ON public.dbxrefprop USING btree (dbxref_id);


--
-- Name: dbxrefprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dbxrefprop_idx2 ON public.dbxrefprop USING btree (type_id);


--
-- Name: environment_cvterm_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX environment_cvterm_idx1 ON public.environment_cvterm USING btree (environment_id);


--
-- Name: environment_cvterm_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX environment_cvterm_idx2 ON public.environment_cvterm USING btree (cvterm_id);


--
-- Name: environment_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX environment_idx1 ON public.environment USING btree (uniquename);


--
-- Name: expression_cvterm_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX expression_cvterm_idx1 ON public.expression_cvterm USING btree (expression_id);


--
-- Name: expression_cvterm_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX expression_cvterm_idx2 ON public.expression_cvterm USING btree (cvterm_id);


--
-- Name: expression_cvterm_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX expression_cvterm_idx3 ON public.expression_cvterm USING btree (cvterm_type_id);


--
-- Name: expression_cvtermprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX expression_cvtermprop_idx1 ON public.expression_cvtermprop USING btree (expression_cvterm_id);


--
-- Name: expression_cvtermprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX expression_cvtermprop_idx2 ON public.expression_cvtermprop USING btree (type_id);


--
-- Name: expression_image_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX expression_image_idx1 ON public.expression_image USING btree (expression_id);


--
-- Name: expression_image_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX expression_image_idx2 ON public.expression_image USING btree (eimage_id);


--
-- Name: expression_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX expression_pub_idx1 ON public.expression_pub USING btree (expression_id);


--
-- Name: expression_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX expression_pub_idx2 ON public.expression_pub USING btree (pub_id);


--
-- Name: expressionprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX expressionprop_idx1 ON public.expressionprop USING btree (expression_id);


--
-- Name: expressionprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX expressionprop_idx2 ON public.expressionprop USING btree (type_id);


--
-- Name: feature_cvterm_dbxref_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_cvterm_dbxref_idx1 ON public.feature_cvterm_dbxref USING btree (feature_cvterm_id);


--
-- Name: feature_cvterm_dbxref_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_cvterm_dbxref_idx2 ON public.feature_cvterm_dbxref USING btree (dbxref_id);


--
-- Name: feature_cvterm_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_cvterm_idx1 ON public.feature_cvterm USING btree (feature_id);


--
-- Name: feature_cvterm_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_cvterm_idx2 ON public.feature_cvterm USING btree (cvterm_id);


--
-- Name: feature_cvterm_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_cvterm_idx3 ON public.feature_cvterm USING btree (pub_id);


--
-- Name: feature_cvtermprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_cvtermprop_idx1 ON public.feature_cvtermprop USING btree (feature_cvterm_id);


--
-- Name: feature_cvtermprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_cvtermprop_idx2 ON public.feature_cvtermprop USING btree (type_id);


--
-- Name: feature_dbxref_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_dbxref_idx1 ON public.feature_dbxref USING btree (feature_id);


--
-- Name: feature_dbxref_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_dbxref_idx2 ON public.feature_dbxref USING btree (dbxref_id);


--
-- Name: feature_expression_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_expression_idx1 ON public.feature_expression USING btree (expression_id);


--
-- Name: feature_expression_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_expression_idx2 ON public.feature_expression USING btree (feature_id);


--
-- Name: feature_expression_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_expression_idx3 ON public.feature_expression USING btree (pub_id);


--
-- Name: feature_expressionprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_expressionprop_idx1 ON public.feature_expressionprop USING btree (feature_expression_id);


--
-- Name: feature_expressionprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_expressionprop_idx2 ON public.feature_expressionprop USING btree (type_id);


--
-- Name: feature_genotype_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_genotype_idx1 ON public.feature_genotype USING btree (feature_id);


--
-- Name: feature_genotype_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_genotype_idx2 ON public.feature_genotype USING btree (genotype_id);


--
-- Name: feature_grpmember_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_grpmember_idx1 ON public.feature_grpmember USING btree (feature_id);


--
-- Name: feature_grpmember_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_grpmember_idx2 ON public.feature_grpmember USING btree (grpmember_id);


--
-- Name: feature_grpmember_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_grpmember_pub_idx1 ON public.feature_grpmember_pub USING btree (feature_grpmember_id);


--
-- Name: feature_grpmember_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_grpmember_pub_idx2 ON public.feature_grpmember_pub USING btree (pub_id);


--
-- Name: feature_humanhealth_dbxref_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_humanhealth_dbxref_idx1 ON public.feature_humanhealth_dbxref USING btree (humanhealth_dbxref_id);


--
-- Name: feature_humanhealth_dbxref_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_humanhealth_dbxref_idx2 ON public.feature_humanhealth_dbxref USING btree (feature_id);


--
-- Name: feature_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_idx1 ON public.feature USING btree (dbxref_id);


--
-- Name: feature_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_idx2 ON public.feature USING btree (organism_id);


--
-- Name: feature_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_idx3 ON public.feature USING btree (type_id);


--
-- Name: feature_idx4; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_idx4 ON public.feature USING btree (uniquename);


--
-- Name: feature_interaction_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_interaction_idx1 ON public.feature_interaction USING btree (feature_id);


--
-- Name: feature_interaction_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_interaction_idx2 ON public.feature_interaction USING btree (interaction_id);


--
-- Name: feature_interaction_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_interaction_idx3 ON public.feature_interaction USING btree (role_id);


--
-- Name: feature_interaction_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_interaction_pub_idx1 ON public.feature_interaction_pub USING btree (feature_interaction_id);


--
-- Name: feature_interaction_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_interaction_pub_idx2 ON public.feature_interaction_pub USING btree (pub_id);


--
-- Name: feature_interactionprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_interactionprop_idx1 ON public.feature_interactionprop USING btree (feature_interaction_id);


--
-- Name: feature_interactionprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_interactionprop_idx2 ON public.feature_interactionprop USING btree (type_id);


--
-- Name: feature_name_ind1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_name_ind1 ON public.feature USING btree (name);


--
-- Name: feature_phenotype_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_phenotype_idx1 ON public.feature_phenotype USING btree (feature_id);


--
-- Name: feature_phenotype_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_phenotype_idx2 ON public.feature_phenotype USING btree (phenotype_id);


--
-- Name: feature_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_pub_idx1 ON public.feature_pub USING btree (feature_id);


--
-- Name: feature_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_pub_idx2 ON public.feature_pub USING btree (pub_id);


--
-- Name: feature_pubprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_pubprop_idx1 ON public.feature_pubprop USING btree (feature_pub_id);


--
-- Name: feature_relationship_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_relationship_idx1 ON public.feature_relationship USING btree (subject_id);


--
-- Name: feature_relationship_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_relationship_idx2 ON public.feature_relationship USING btree (object_id);


--
-- Name: feature_relationship_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_relationship_idx3 ON public.feature_relationship USING btree (type_id);


--
-- Name: feature_relationship_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_relationship_pub_idx1 ON public.feature_relationship_pub USING btree (feature_relationship_id);


--
-- Name: feature_relationship_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_relationship_pub_idx2 ON public.feature_relationship_pub USING btree (pub_id);


--
-- Name: feature_relationshipprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_relationshipprop_idx1 ON public.feature_relationshipprop USING btree (feature_relationship_id);


--
-- Name: feature_relationshipprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_relationshipprop_idx2 ON public.feature_relationshipprop USING btree (type_id);


--
-- Name: feature_relationshipprop_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_relationshipprop_pub_idx1 ON public.feature_relationshipprop_pub USING btree (feature_relationshipprop_id);


--
-- Name: feature_relationshipprop_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_relationshipprop_pub_idx2 ON public.feature_relationshipprop_pub USING btree (pub_id);


--
-- Name: feature_synonym_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_synonym_idx1 ON public.feature_synonym USING btree (synonym_id);


--
-- Name: feature_synonym_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_synonym_idx2 ON public.feature_synonym USING btree (feature_id);


--
-- Name: feature_synonym_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX feature_synonym_idx3 ON public.feature_synonym USING btree (pub_id);


--
-- Name: featureloc_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX featureloc_idx1 ON public.featureloc USING btree (feature_id);


--
-- Name: featureloc_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX featureloc_idx2 ON public.featureloc USING btree (srcfeature_id);


--
-- Name: featureloc_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX featureloc_idx3 ON public.featureloc USING btree (srcfeature_id, fmin, fmax);


--
-- Name: featureloc_idx4; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX featureloc_idx4 ON public.featureloc USING btree (fmin);


--
-- Name: featureloc_idx5; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX featureloc_idx5 ON public.featureloc USING btree (fmax);


--
-- Name: featureloc_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX featureloc_pub_idx1 ON public.featureloc_pub USING btree (featureloc_id);


--
-- Name: featureloc_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX featureloc_pub_idx2 ON public.featureloc_pub USING btree (pub_id);


--
-- Name: featuremap_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX featuremap_pub_idx1 ON public.featuremap_pub USING btree (featuremap_id);


--
-- Name: featuremap_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX featuremap_pub_idx2 ON public.featuremap_pub USING btree (pub_id);


--
-- Name: featurepos_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX featurepos_idx1 ON public.featurepos USING btree (featuremap_id);


--
-- Name: featurepos_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX featurepos_idx2 ON public.featurepos USING btree (feature_id);


--
-- Name: featurepos_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX featurepos_idx3 ON public.featurepos USING btree (map_feature_id);


--
-- Name: featureprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX featureprop_idx1 ON public.featureprop USING btree (feature_id);


--
-- Name: featureprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX featureprop_idx2 ON public.featureprop USING btree (type_id);


--
-- Name: featureprop_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX featureprop_pub_idx1 ON public.featureprop_pub USING btree (featureprop_id);


--
-- Name: featureprop_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX featureprop_pub_idx2 ON public.featureprop_pub USING btree (pub_id);


--
-- Name: featurerange_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX featurerange_idx1 ON public.featurerange USING btree (featuremap_id);


--
-- Name: featurerange_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX featurerange_idx2 ON public.featurerange USING btree (feature_id);


--
-- Name: featurerange_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX featurerange_idx3 ON public.featurerange USING btree (leftstartf_id);


--
-- Name: featurerange_idx4; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX featurerange_idx4 ON public.featurerange USING btree (leftendf_id);


--
-- Name: featurerange_idx5; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX featurerange_idx5 ON public.featurerange USING btree (rightstartf_id);


--
-- Name: featurerange_idx6; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX featurerange_idx6 ON public.featurerange USING btree (rightendf_id);


--
-- Name: genotype_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX genotype_idx1 ON public.genotype USING btree (uniquename);


--
-- Name: genotype_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX genotype_idx2 ON public.genotype USING btree (name);


--
-- Name: grp_cvterm_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grp_cvterm_idx1 ON public.grp_cvterm USING btree (grp_id);


--
-- Name: grp_cvterm_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grp_cvterm_idx2 ON public.grp_cvterm USING btree (cvterm_id);


--
-- Name: grp_cvterm_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grp_cvterm_idx3 ON public.grp_cvterm USING btree (pub_id);


--
-- Name: grp_dbxref_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grp_dbxref_idx1 ON public.grp_dbxref USING btree (grp_id);


--
-- Name: grp_dbxref_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grp_dbxref_idx2 ON public.grp_dbxref USING btree (dbxref_id);


--
-- Name: grp_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grp_idx1 ON public.grp USING btree (type_id);


--
-- Name: grp_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grp_idx2 ON public.grp USING btree (uniquename);


--
-- Name: grp_name_ind1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grp_name_ind1 ON public.grp USING btree (name);


--
-- Name: grp_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grp_pub_idx1 ON public.grp_pub USING btree (grp_id);


--
-- Name: grp_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grp_pub_idx2 ON public.grp_pub USING btree (pub_id);


--
-- Name: grp_pubprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grp_pubprop_idx1 ON public.grp_pubprop USING btree (grp_pub_id);


--
-- Name: grp_relationship_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grp_relationship_idx1 ON public.grp_relationship USING btree (subject_id);


--
-- Name: grp_relationship_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grp_relationship_idx2 ON public.grp_relationship USING btree (object_id);


--
-- Name: grp_relationship_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grp_relationship_idx3 ON public.grp_relationship USING btree (type_id);


--
-- Name: grp_relationship_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grp_relationship_pub_idx1 ON public.grp_relationship_pub USING btree (grp_relationship_id);


--
-- Name: grp_relationship_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grp_relationship_pub_idx2 ON public.grp_relationship_pub USING btree (pub_id);


--
-- Name: grp_relationshipprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grp_relationshipprop_idx1 ON public.grp_relationshipprop USING btree (grp_relationship_id);


--
-- Name: grp_relationshipprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grp_relationshipprop_idx2 ON public.grp_relationshipprop USING btree (type_id);


--
-- Name: grp_synonym_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grp_synonym_idx1 ON public.grp_synonym USING btree (synonym_id);


--
-- Name: grp_synonym_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grp_synonym_idx2 ON public.grp_synonym USING btree (grp_id);


--
-- Name: grp_synonym_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grp_synonym_idx3 ON public.grp_synonym USING btree (pub_id);


--
-- Name: grpmember_cvterm_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grpmember_cvterm_idx1 ON public.grpmember_cvterm USING btree (grpmember_id);


--
-- Name: grpmember_cvterm_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grpmember_cvterm_idx2 ON public.grpmember_cvterm USING btree (cvterm_id);


--
-- Name: grpmember_cvterm_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grpmember_cvterm_idx3 ON public.grpmember_cvterm USING btree (pub_id);


--
-- Name: grpmember_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grpmember_idx1 ON public.grpmember USING btree (grp_id);


--
-- Name: grpmember_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grpmember_idx2 ON public.grpmember USING btree (type_id);


--
-- Name: grpmember_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grpmember_pub_idx1 ON public.grpmember_pub USING btree (grpmember_id);


--
-- Name: grpmember_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grpmember_pub_idx2 ON public.grpmember_pub USING btree (pub_id);


--
-- Name: grpmemberprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grpmemberprop_idx1 ON public.grpmemberprop USING btree (grpmember_id);


--
-- Name: grpmemberprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grpmemberprop_idx2 ON public.grpmemberprop USING btree (type_id);


--
-- Name: grpmemberprop_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grpmemberprop_pub_idx1 ON public.grpmemberprop_pub USING btree (grpmemberprop_id);


--
-- Name: grpmemberprop_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grpmemberprop_pub_idx2 ON public.grpmemberprop_pub USING btree (pub_id);


--
-- Name: grpprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grpprop_idx1 ON public.grpprop USING btree (grp_id);


--
-- Name: grpprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grpprop_idx2 ON public.grpprop USING btree (type_id);


--
-- Name: grpprop_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grpprop_pub_idx1 ON public.grpprop_pub USING btree (grpprop_id);


--
-- Name: grpprop_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX grpprop_pub_idx2 ON public.grpprop_pub USING btree (pub_id);


--
-- Name: humanhealth_cvterm_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_cvterm_idx1 ON public.humanhealth_cvterm USING btree (humanhealth_id);


--
-- Name: humanhealth_cvterm_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_cvterm_idx2 ON public.humanhealth_cvterm USING btree (cvterm_id);


--
-- Name: humanhealth_cvtermprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_cvtermprop_idx1 ON public.humanhealth_cvtermprop USING btree (humanhealth_cvterm_id);


--
-- Name: humanhealth_cvtermprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_cvtermprop_idx2 ON public.humanhealth_cvtermprop USING btree (type_id);


--
-- Name: humanhealth_dbxref_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_dbxref_idx1 ON public.humanhealth_dbxref USING btree (humanhealth_id);


--
-- Name: humanhealth_dbxref_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_dbxref_idx2 ON public.humanhealth_dbxref USING btree (dbxref_id);


--
-- Name: humanhealth_dbxrefprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_dbxrefprop_idx1 ON public.humanhealth_dbxrefprop USING btree (humanhealth_dbxref_id);


--
-- Name: humanhealth_dbxrefprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_dbxrefprop_idx2 ON public.humanhealth_dbxrefprop USING btree (type_id);


--
-- Name: humanhealth_dbxrefprop_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_dbxrefprop_pub_idx1 ON public.humanhealth_dbxrefprop_pub USING btree (humanhealth_dbxrefprop_id);


--
-- Name: humanhealth_dbxrefprop_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_dbxrefprop_pub_idx2 ON public.humanhealth_dbxrefprop_pub USING btree (pub_id);


--
-- Name: humanhealth_feature_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_feature_idx1 ON public.humanhealth_feature USING btree (humanhealth_id);


--
-- Name: humanhealth_feature_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_feature_idx2 ON public.humanhealth_feature USING btree (feature_id);


--
-- Name: humanhealth_featureprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_featureprop_idx1 ON public.humanhealth_featureprop USING btree (humanhealth_feature_id);


--
-- Name: humanhealth_featureprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_featureprop_idx2 ON public.humanhealth_featureprop USING btree (type_id);


--
-- Name: humanhealth_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_idx1 ON public.humanhealth USING btree (uniquename);


--
-- Name: humanhealth_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_idx2 ON public.humanhealth USING btree (name);


--
-- Name: humanhealth_phenotype_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_phenotype_idx1 ON public.humanhealth_phenotype USING btree (humanhealth_id);


--
-- Name: humanhealth_phenotype_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_phenotype_idx2 ON public.humanhealth_phenotype USING btree (phenotype_id);


--
-- Name: humanhealth_phenotypeprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_phenotypeprop_idx1 ON public.humanhealth_phenotypeprop USING btree (humanhealth_phenotype_id);


--
-- Name: humanhealth_phenotypeprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_phenotypeprop_idx2 ON public.humanhealth_phenotypeprop USING btree (type_id);


--
-- Name: humanhealth_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_pub_idx1 ON public.humanhealth_pub USING btree (humanhealth_id);


--
-- Name: humanhealth_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_pub_idx2 ON public.humanhealth_pub USING btree (pub_id);


--
-- Name: humanhealth_pubprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_pubprop_idx1 ON public.humanhealth_pubprop USING btree (humanhealth_pub_id);


--
-- Name: humanhealth_relationship_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_relationship_idx1 ON public.humanhealth_relationship USING btree (subject_id);


--
-- Name: humanhealth_relationship_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_relationship_idx2 ON public.humanhealth_relationship USING btree (object_id);


--
-- Name: humanhealth_relationship_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_relationship_pub_idx1 ON public.humanhealth_relationship_pub USING btree (humanhealth_relationship_id);


--
-- Name: humanhealth_relationship_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_relationship_pub_idx2 ON public.humanhealth_relationship_pub USING btree (pub_id);


--
-- Name: humanhealth_synonym_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_synonym_idx1 ON public.humanhealth_synonym USING btree (synonym_id);


--
-- Name: humanhealth_synonym_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_synonym_idx2 ON public.humanhealth_synonym USING btree (humanhealth_id);


--
-- Name: humanhealth_synonym_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealth_synonym_idx3 ON public.humanhealth_synonym USING btree (pub_id);


--
-- Name: humanhealthprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealthprop_idx1 ON public.humanhealthprop USING btree (humanhealth_id);


--
-- Name: humanhealthprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealthprop_idx2 ON public.humanhealthprop USING btree (type_id);


--
-- Name: humanhealthprop_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealthprop_pub_idx1 ON public.humanhealthprop_pub USING btree (humanhealthprop_id);


--
-- Name: humanhealthprop_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX humanhealthprop_pub_idx2 ON public.humanhealthprop_pub USING btree (pub_id);


--
-- Name: interaction_cell_line_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX interaction_cell_line_idx1 ON public.interaction_cell_line USING btree (cell_line_id);


--
-- Name: interaction_cell_line_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX interaction_cell_line_idx2 ON public.interaction_cell_line USING btree (interaction_id);


--
-- Name: interaction_cell_line_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX interaction_cell_line_idx3 ON public.interaction_cell_line USING btree (pub_id);


--
-- Name: interaction_cvterm_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX interaction_cvterm_idx1 ON public.interaction_cvterm USING btree (interaction_id);


--
-- Name: interaction_cvterm_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX interaction_cvterm_idx2 ON public.interaction_cvterm USING btree (cvterm_id);


--
-- Name: interaction_cvtermprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX interaction_cvtermprop_idx1 ON public.interaction_cvtermprop USING btree (interaction_cvterm_id);


--
-- Name: interaction_cvtermprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX interaction_cvtermprop_idx2 ON public.interaction_cvtermprop USING btree (type_id);


--
-- Name: interaction_expression_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX interaction_expression_idx1 ON public.interaction_expression USING btree (expression_id);


--
-- Name: interaction_expression_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX interaction_expression_idx2 ON public.interaction_expression USING btree (interaction_id);


--
-- Name: interaction_expression_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX interaction_expression_idx3 ON public.interaction_expression USING btree (pub_id);


--
-- Name: interaction_expressionprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX interaction_expressionprop_idx1 ON public.interaction_expressionprop USING btree (interaction_expression_id);


--
-- Name: interaction_expressionprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX interaction_expressionprop_idx2 ON public.interaction_expressionprop USING btree (type_id);


--
-- Name: interaction_group_feature_interaction_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX interaction_group_feature_interaction_idx1 ON public.interaction_group_feature_interaction USING btree (interaction_group_id);


--
-- Name: interaction_group_feature_interaction_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX interaction_group_feature_interaction_idx2 ON public.interaction_group_feature_interaction USING btree (feature_interaction_id);


--
-- Name: interaction_group_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX interaction_group_idx1 ON public.interaction_group USING btree (uniquename);


--
-- Name: interaction_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX interaction_idx1 ON public.interaction USING btree (uniquename);


--
-- Name: interaction_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX interaction_idx2 ON public.interaction USING btree (type_id);


--
-- Name: interaction_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX interaction_pub_idx1 ON public.interaction_pub USING btree (interaction_id);


--
-- Name: interaction_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX interaction_pub_idx2 ON public.interaction_pub USING btree (pub_id);


--
-- Name: interactionprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX interactionprop_idx1 ON public.interactionprop USING btree (interaction_id);


--
-- Name: interactionprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX interactionprop_idx2 ON public.interactionprop USING btree (type_id);


--
-- Name: interactionprop_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX interactionprop_pub_idx1 ON public.interactionprop_pub USING btree (interactionprop_id);


--
-- Name: interactionprop_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX interactionprop_pub_idx2 ON public.interactionprop_pub USING btree (pub_id);


--
-- Name: library_cvterm_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_cvterm_idx1 ON public.library_cvterm USING btree (library_id);


--
-- Name: library_cvterm_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_cvterm_idx2 ON public.library_cvterm USING btree (cvterm_id);


--
-- Name: library_cvterm_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_cvterm_idx3 ON public.library_cvterm USING btree (pub_id);


--
-- Name: library_cvtermprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_cvtermprop_idx1 ON public.library_cvtermprop USING btree (library_cvterm_id);


--
-- Name: library_cvtermprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_cvtermprop_idx2 ON public.library_cvtermprop USING btree (type_id);


--
-- Name: library_dbxref_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_dbxref_idx1 ON public.library_dbxref USING btree (library_id);


--
-- Name: library_dbxref_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_dbxref_idx2 ON public.library_dbxref USING btree (dbxref_id);


--
-- Name: library_dbxrefprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_dbxrefprop_idx1 ON public.library_dbxrefprop USING btree (library_dbxref_id);


--
-- Name: library_dbxrefprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_dbxrefprop_idx2 ON public.library_dbxrefprop USING btree (type_id);


--
-- Name: library_expression_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_expression_idx1 ON public.library_expression USING btree (expression_id);


--
-- Name: library_expression_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_expression_idx2 ON public.library_expression USING btree (library_id);


--
-- Name: library_expression_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_expression_idx3 ON public.library_expression USING btree (pub_id);


--
-- Name: library_expressionprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_expressionprop_idx1 ON public.library_expressionprop USING btree (library_expression_id);


--
-- Name: library_expressionprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_expressionprop_idx2 ON public.library_expressionprop USING btree (type_id);


--
-- Name: library_feature_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_feature_idx1 ON public.library_feature USING btree (library_id);


--
-- Name: library_feature_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_feature_idx2 ON public.library_feature USING btree (feature_id);


--
-- Name: library_featureprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_featureprop_idx1 ON public.library_featureprop USING btree (library_feature_id);


--
-- Name: library_featureprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_featureprop_idx2 ON public.library_featureprop USING btree (type_id);


--
-- Name: library_grpmember_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_grpmember_idx1 ON public.library_grpmember USING btree (library_id);


--
-- Name: library_grpmember_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_grpmember_idx2 ON public.library_grpmember USING btree (grpmember_id);


--
-- Name: library_humanhealth_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_humanhealth_idx1 ON public.library_humanhealth USING btree (humanhealth_id);


--
-- Name: library_humanhealth_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_humanhealth_idx2 ON public.library_humanhealth USING btree (library_id);


--
-- Name: library_humanhealthprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_humanhealthprop_idx1 ON public.library_humanhealthprop USING btree (library_humanhealth_id);


--
-- Name: library_humanhealthprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_humanhealthprop_idx2 ON public.library_humanhealthprop USING btree (type_id);


--
-- Name: library_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_idx1 ON public.library USING btree (organism_id);


--
-- Name: library_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_idx2 ON public.library USING btree (type_id);


--
-- Name: library_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_idx3 ON public.library USING btree (uniquename);


--
-- Name: library_interaction_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_interaction_idx1 ON public.library_interaction USING btree (interaction_id);


--
-- Name: library_interaction_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_interaction_idx2 ON public.library_interaction USING btree (library_id);


--
-- Name: library_interaction_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_interaction_idx3 ON public.library_interaction USING btree (pub_id);


--
-- Name: library_name_ind1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_name_ind1 ON public.library USING btree (name);


--
-- Name: library_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_pub_idx1 ON public.library_pub USING btree (library_id);


--
-- Name: library_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_pub_idx2 ON public.library_pub USING btree (pub_id);


--
-- Name: library_relationship_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_relationship_idx1 ON public.library_relationship USING btree (subject_id);


--
-- Name: library_relationship_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_relationship_idx2 ON public.library_relationship USING btree (object_id);


--
-- Name: library_relationship_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_relationship_idx3 ON public.library_relationship USING btree (type_id);


--
-- Name: library_relationship_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_relationship_pub_idx1 ON public.library_relationship_pub USING btree (library_relationship_id);


--
-- Name: library_relationship_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_relationship_pub_idx2 ON public.library_relationship_pub USING btree (pub_id);


--
-- Name: library_strain_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_strain_idx1 ON public.library_strain USING btree (strain_id);


--
-- Name: library_strain_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_strain_idx2 ON public.library_strain USING btree (library_id);


--
-- Name: library_strainprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_strainprop_idx1 ON public.library_strainprop USING btree (library_strain_id);


--
-- Name: library_strainprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_strainprop_idx2 ON public.library_strainprop USING btree (type_id);


--
-- Name: library_synonym_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_synonym_idx1 ON public.library_synonym USING btree (synonym_id);


--
-- Name: library_synonym_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_synonym_idx2 ON public.library_synonym USING btree (library_id);


--
-- Name: library_synonym_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX library_synonym_idx3 ON public.library_synonym USING btree (pub_id);


--
-- Name: libraryprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX libraryprop_idx1 ON public.libraryprop USING btree (library_id);


--
-- Name: libraryprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX libraryprop_idx2 ON public.libraryprop USING btree (type_id);


--
-- Name: libraryprop_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX libraryprop_pub_idx1 ON public.libraryprop_pub USING btree (libraryprop_id);


--
-- Name: libraryprop_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX libraryprop_pub_idx2 ON public.libraryprop_pub USING btree (pub_id);


--
-- Name: organism_cvterm_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX organism_cvterm_idx1 ON public.organism_cvterm USING btree (organism_id);


--
-- Name: organism_cvterm_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX organism_cvterm_idx2 ON public.organism_cvterm USING btree (cvterm_id);


--
-- Name: organism_cvtermprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX organism_cvtermprop_idx1 ON public.organism_cvtermprop USING btree (organism_cvterm_id);


--
-- Name: organism_cvtermprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX organism_cvtermprop_idx2 ON public.organism_cvtermprop USING btree (type_id);


--
-- Name: organism_dbxref_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX organism_dbxref_idx1 ON public.organism_dbxref USING btree (organism_id);


--
-- Name: organism_dbxref_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX organism_dbxref_idx2 ON public.organism_dbxref USING btree (dbxref_id);


--
-- Name: organism_grpmember_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX organism_grpmember_idx1 ON public.organism_grpmember USING btree (organism_id);


--
-- Name: organism_grpmember_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX organism_grpmember_idx2 ON public.organism_grpmember USING btree (grpmember_id);


--
-- Name: organism_library_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX organism_library_idx1 ON public.organism_library USING btree (organism_id);


--
-- Name: organism_library_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX organism_library_idx2 ON public.organism_library USING btree (library_id);


--
-- Name: organism_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX organism_pub_idx1 ON public.organism_pub USING btree (organism_id);


--
-- Name: organism_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX organism_pub_idx2 ON public.organism_pub USING btree (pub_id);


--
-- Name: organismprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX organismprop_idx1 ON public.organismprop USING btree (organism_id);


--
-- Name: organismprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX organismprop_idx2 ON public.organismprop USING btree (type_id);


--
-- Name: organismprop_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX organismprop_pub_idx1 ON public.organismprop_pub USING btree (organismprop_id);


--
-- Name: organismprop_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX organismprop_pub_idx2 ON public.organismprop_pub USING btree (pub_id);


--
-- Name: phendesc_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX phendesc_idx1 ON public.phendesc USING btree (genotype_id);


--
-- Name: phendesc_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX phendesc_idx2 ON public.phendesc USING btree (environment_id);


--
-- Name: phendesc_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX phendesc_idx3 ON public.phendesc USING btree (pub_id);


--
-- Name: phenotype_comparison_cvterm_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX phenotype_comparison_cvterm_idx1 ON public.phenotype_comparison_cvterm USING btree (phenotype_comparison_id);


--
-- Name: phenotype_comparison_cvterm_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX phenotype_comparison_cvterm_idx2 ON public.phenotype_comparison_cvterm USING btree (cvterm_id);


--
-- Name: phenotype_comparison_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX phenotype_comparison_idx1 ON public.phenotype_comparison USING btree (genotype1_id);


--
-- Name: phenotype_comparison_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX phenotype_comparison_idx2 ON public.phenotype_comparison USING btree (genotype2_id);


--
-- Name: phenotype_comparison_idx4; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX phenotype_comparison_idx4 ON public.phenotype_comparison USING btree (pub_id);


--
-- Name: phenotype_cvterm_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX phenotype_cvterm_idx1 ON public.phenotype_cvterm USING btree (phenotype_id);


--
-- Name: phenotype_cvterm_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX phenotype_cvterm_idx2 ON public.phenotype_cvterm USING btree (cvterm_id);


--
-- Name: phenotype_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX phenotype_idx1 ON public.phenotype USING btree (cvalue_id);


--
-- Name: phenotype_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX phenotype_idx2 ON public.phenotype USING btree (observable_id);


--
-- Name: phenotype_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX phenotype_idx3 ON public.phenotype USING btree (attr_id);


--
-- Name: phenstatement_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX phenstatement_idx1 ON public.phenstatement USING btree (genotype_id);


--
-- Name: phenstatement_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX phenstatement_idx2 ON public.phenstatement USING btree (phenotype_id);


--
-- Name: pub_dbxref_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pub_dbxref_idx1 ON public.pub_dbxref USING btree (pub_id);


--
-- Name: pub_dbxref_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pub_dbxref_idx2 ON public.pub_dbxref USING btree (dbxref_id);


--
-- Name: pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pub_idx1 ON public.pub USING btree (type_id);


--
-- Name: pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pub_idx2 ON public.pub USING btree (uniquename);


--
-- Name: pub_relationship_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pub_relationship_idx3 ON public.pub_relationship USING btree (type_id);


--
-- Name: pubauthor_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pubauthor_idx2 ON public.pubauthor USING btree (pub_id);


--
-- Name: pubprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pubprop_idx1 ON public.pubprop USING btree (pub_id);


--
-- Name: pubprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX pubprop_idx2 ON public.pubprop USING btree (type_id);


--
-- Name: strain_cvterm_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strain_cvterm_idx1 ON public.strain_cvterm USING btree (strain_id);


--
-- Name: strain_cvterm_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strain_cvterm_idx2 ON public.strain_cvterm USING btree (cvterm_id);


--
-- Name: strain_cvtermprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strain_cvtermprop_idx1 ON public.strain_cvtermprop USING btree (strain_cvterm_id);


--
-- Name: strain_cvtermprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strain_cvtermprop_idx2 ON public.strain_cvtermprop USING btree (type_id);


--
-- Name: strain_dbxref_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strain_dbxref_idx1 ON public.strain_dbxref USING btree (strain_id);


--
-- Name: strain_dbxref_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strain_dbxref_idx2 ON public.strain_dbxref USING btree (dbxref_id);


--
-- Name: strain_feature_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strain_feature_idx1 ON public.strain_feature USING btree (strain_id);


--
-- Name: strain_feature_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strain_feature_idx2 ON public.strain_feature USING btree (feature_id);


--
-- Name: strain_featureprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strain_featureprop_idx1 ON public.strain_featureprop USING btree (strain_feature_id);


--
-- Name: strain_featureprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strain_featureprop_idx2 ON public.strain_featureprop USING btree (type_id);


--
-- Name: strain_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strain_idx1 ON public.strain USING btree (uniquename);


--
-- Name: strain_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strain_idx2 ON public.strain USING btree (name);


--
-- Name: strain_phenotype_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strain_phenotype_idx1 ON public.strain_phenotype USING btree (strain_id);


--
-- Name: strain_phenotype_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strain_phenotype_idx2 ON public.strain_phenotype USING btree (phenotype_id);


--
-- Name: strain_phenotypeprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strain_phenotypeprop_idx1 ON public.strain_phenotypeprop USING btree (strain_phenotype_id);


--
-- Name: strain_phenotypeprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strain_phenotypeprop_idx2 ON public.strain_phenotypeprop USING btree (type_id);


--
-- Name: strain_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strain_pub_idx1 ON public.strain_pub USING btree (strain_id);


--
-- Name: strain_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strain_pub_idx2 ON public.strain_pub USING btree (pub_id);


--
-- Name: strain_relationship_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strain_relationship_idx1 ON public.strain_relationship USING btree (subject_id);


--
-- Name: strain_relationship_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strain_relationship_idx2 ON public.strain_relationship USING btree (object_id);


--
-- Name: strain_relationship_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strain_relationship_pub_idx1 ON public.strain_relationship_pub USING btree (strain_relationship_id);


--
-- Name: strain_relationship_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strain_relationship_pub_idx2 ON public.strain_relationship_pub USING btree (pub_id);


--
-- Name: strain_synonym_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strain_synonym_idx1 ON public.strain_synonym USING btree (synonym_id);


--
-- Name: strain_synonym_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strain_synonym_idx2 ON public.strain_synonym USING btree (strain_id);


--
-- Name: strain_synonym_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strain_synonym_idx3 ON public.strain_synonym USING btree (pub_id);


--
-- Name: strainprop_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strainprop_idx1 ON public.strainprop USING btree (strain_id);


--
-- Name: strainprop_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strainprop_idx2 ON public.strainprop USING btree (type_id);


--
-- Name: strainprop_pub_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strainprop_pub_idx1 ON public.strainprop_pub USING btree (strainprop_id);


--
-- Name: strainprop_pub_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX strainprop_pub_idx2 ON public.strainprop_pub USING btree (pub_id);


--
-- Name: synonym_idx1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX synonym_idx1 ON public.synonym USING btree (type_id);


--
-- Name: synonym_idx2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX synonym_idx2 ON public.synonym USING btree (name);


--
-- Name: synonym_idx3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX synonym_idx3 ON public.synonym USING btree (synonym_sgml);


--
-- Name: expression expression_assignname_tr_i; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER expression_assignname_tr_i AFTER INSERT ON public.expression FOR EACH ROW EXECUTE PROCEDURE public.expression_assignname_fn_i();


--
-- Name: feature feature_assignname_tr_i; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER feature_assignname_tr_i AFTER INSERT ON public.feature FOR EACH ROW EXECUTE PROCEDURE public.feature_assignname_fn_i();


--
-- Name: feature feature_propagatename_tr_u; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER feature_propagatename_tr_u AFTER UPDATE ON public.feature FOR EACH ROW EXECUTE PROCEDURE public.feature_propagatename_fn_u();


--
-- Name: feature_relationship feature_relationship_propagatename_tr_i; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER feature_relationship_propagatename_tr_i AFTER INSERT ON public.feature_relationship FOR EACH ROW EXECUTE PROCEDURE public.feature_relationship_propagatename_fn_i();


--
-- Name: feature_relationship feature_relationship_tr_d; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER feature_relationship_tr_d BEFORE DELETE ON public.feature_relationship FOR EACH ROW EXECUTE PROCEDURE public.feature_relationship_fn_d();


--
-- Name: grp grp_assignname_tr_i; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER grp_assignname_tr_i AFTER INSERT ON public.grp FOR EACH ROW EXECUTE PROCEDURE public.grp_assignname_fn_i();


--
-- Name: humanhealth humanhealth_assignname_tr_i; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER humanhealth_assignname_tr_i AFTER INSERT ON public.humanhealth FOR EACH ROW EXECUTE PROCEDURE public.humanhealth_assignname_fn_i();


--
-- Name: humanhealth_dbxrefprop_pub humanhealth_dbxrefprop_pub_audit; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER humanhealth_dbxrefprop_pub_audit AFTER INSERT OR DELETE OR UPDATE ON public.humanhealth_dbxrefprop_pub FOR EACH ROW EXECUTE PROCEDURE public.humanhealth_dbxrefprop_pub_audit();


--
-- Name: library library_assignname_tr_i; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER library_assignname_tr_i AFTER INSERT ON public.library FOR EACH ROW EXECUTE PROCEDURE public.library_assignname_fn_i();


--
-- Name: pub pub_assignname_tr_i; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER pub_assignname_tr_i AFTER INSERT ON public.pub FOR EACH ROW EXECUTE PROCEDURE public.pub_assignname_fn_i();


--
-- Name: strain strain_assignname_tr_i; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER strain_assignname_tr_i AFTER INSERT ON public.strain FOR EACH ROW EXECUTE PROCEDURE public.strain_assignname_fn_i();


--
-- Name: feature tr_feature_del; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_feature_del BEFORE DELETE ON public.feature FOR EACH ROW EXECUTE PROCEDURE public.fn_feature_del();


--
-- Name: feature tr_feature_evi_del; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_feature_evi_del BEFORE UPDATE ON public.feature FOR EACH ROW EXECUTE PROCEDURE public.fn_feature_evi_del();


--
-- Name: analysisfeature analysisfeature_analysis_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisfeature
    ADD CONSTRAINT analysisfeature_analysis_id_fkey FOREIGN KEY (analysis_id) REFERENCES public.analysis(analysis_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: analysisfeature analysisfeature_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisfeature
    ADD CONSTRAINT analysisfeature_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.feature(feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: analysisgrp analysisgrp_analysis_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisgrp
    ADD CONSTRAINT analysisgrp_analysis_id_fkey FOREIGN KEY (analysis_id) REFERENCES public.analysis(analysis_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: analysisgrp analysisgrp_grp_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisgrp
    ADD CONSTRAINT analysisgrp_grp_id_fkey FOREIGN KEY (grp_id) REFERENCES public.grp(grp_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: analysisgrpmember analysisgrpmember_analysis_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisgrpmember
    ADD CONSTRAINT analysisgrpmember_analysis_id_fkey FOREIGN KEY (analysis_id) REFERENCES public.analysis(analysis_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: analysisgrpmember analysisgrpmember_grpmember_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisgrpmember
    ADD CONSTRAINT analysisgrpmember_grpmember_id_fkey FOREIGN KEY (grpmember_id) REFERENCES public.grpmember(grpmember_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: analysisprop analysisprop_analysis_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisprop
    ADD CONSTRAINT analysisprop_analysis_id_fkey FOREIGN KEY (analysis_id) REFERENCES public.analysis(analysis_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: analysisprop analysisprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analysisprop
    ADD CONSTRAINT analysisprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_cvterm cell_line_cvterm_cell_line_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_cvterm
    ADD CONSTRAINT cell_line_cvterm_cell_line_id_fkey FOREIGN KEY (cell_line_id) REFERENCES public.cell_line(cell_line_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_cvterm cell_line_cvterm_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_cvterm
    ADD CONSTRAINT cell_line_cvterm_cvterm_id_fkey FOREIGN KEY (cvterm_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_cvterm cell_line_cvterm_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_cvterm
    ADD CONSTRAINT cell_line_cvterm_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_cvtermprop cell_line_cvtermprop_cell_line_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_cvtermprop
    ADD CONSTRAINT cell_line_cvtermprop_cell_line_cvterm_id_fkey FOREIGN KEY (cell_line_cvterm_id) REFERENCES public.cell_line_cvterm(cell_line_cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_cvtermprop cell_line_cvtermprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_cvtermprop
    ADD CONSTRAINT cell_line_cvtermprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_dbxref cell_line_dbxref_cell_line_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_dbxref
    ADD CONSTRAINT cell_line_dbxref_cell_line_id_fkey FOREIGN KEY (cell_line_id) REFERENCES public.cell_line(cell_line_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_dbxref cell_line_dbxref_dbxref_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_dbxref
    ADD CONSTRAINT cell_line_dbxref_dbxref_id_fkey FOREIGN KEY (dbxref_id) REFERENCES public.dbxref(dbxref_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_feature cell_line_feature_cell_line_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_feature
    ADD CONSTRAINT cell_line_feature_cell_line_id_fkey FOREIGN KEY (cell_line_id) REFERENCES public.cell_line(cell_line_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_feature cell_line_feature_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_feature
    ADD CONSTRAINT cell_line_feature_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.feature(feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_feature cell_line_feature_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_feature
    ADD CONSTRAINT cell_line_feature_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_library cell_line_library_cell_line_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_library
    ADD CONSTRAINT cell_line_library_cell_line_id_fkey FOREIGN KEY (cell_line_id) REFERENCES public.cell_line(cell_line_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_library cell_line_library_library_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_library
    ADD CONSTRAINT cell_line_library_library_id_fkey FOREIGN KEY (library_id) REFERENCES public.library(library_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_library cell_line_library_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_library
    ADD CONSTRAINT cell_line_library_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_libraryprop cell_line_libraryprop_cell_line_library_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_libraryprop
    ADD CONSTRAINT cell_line_libraryprop_cell_line_library_id_fkey FOREIGN KEY (cell_line_library_id) REFERENCES public.cell_line_library(cell_line_library_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_libraryprop cell_line_libraryprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_libraryprop
    ADD CONSTRAINT cell_line_libraryprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line cell_line_organism_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line
    ADD CONSTRAINT cell_line_organism_id_fkey FOREIGN KEY (organism_id) REFERENCES public.organism(organism_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_pub cell_line_pub_cell_line_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_pub
    ADD CONSTRAINT cell_line_pub_cell_line_id_fkey FOREIGN KEY (cell_line_id) REFERENCES public.cell_line(cell_line_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_pub cell_line_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_pub
    ADD CONSTRAINT cell_line_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_relationship cell_line_relationship_object_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_relationship
    ADD CONSTRAINT cell_line_relationship_object_id_fkey FOREIGN KEY (object_id) REFERENCES public.cell_line(cell_line_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_relationship cell_line_relationship_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_relationship
    ADD CONSTRAINT cell_line_relationship_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.cell_line(cell_line_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_relationship cell_line_relationship_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_relationship
    ADD CONSTRAINT cell_line_relationship_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_strain cell_line_strain_cell_line_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_strain
    ADD CONSTRAINT cell_line_strain_cell_line_id_fkey FOREIGN KEY (cell_line_id) REFERENCES public.cell_line(cell_line_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_strain cell_line_strain_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_strain
    ADD CONSTRAINT cell_line_strain_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_strain cell_line_strain_strain_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_strain
    ADD CONSTRAINT cell_line_strain_strain_id_fkey FOREIGN KEY (strain_id) REFERENCES public.strain(strain_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_strainprop cell_line_strainprop_cell_line_strain_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_strainprop
    ADD CONSTRAINT cell_line_strainprop_cell_line_strain_id_fkey FOREIGN KEY (cell_line_strain_id) REFERENCES public.cell_line_strain(cell_line_strain_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_strainprop cell_line_strainprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_strainprop
    ADD CONSTRAINT cell_line_strainprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_synonym cell_line_synonym_cell_line_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_synonym
    ADD CONSTRAINT cell_line_synonym_cell_line_id_fkey FOREIGN KEY (cell_line_id) REFERENCES public.cell_line(cell_line_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_synonym cell_line_synonym_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_synonym
    ADD CONSTRAINT cell_line_synonym_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_line_synonym cell_line_synonym_synonym_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_line_synonym
    ADD CONSTRAINT cell_line_synonym_synonym_id_fkey FOREIGN KEY (synonym_id) REFERENCES public.synonym(synonym_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_lineprop cell_lineprop_cell_line_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_lineprop
    ADD CONSTRAINT cell_lineprop_cell_line_id_fkey FOREIGN KEY (cell_line_id) REFERENCES public.cell_line(cell_line_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_lineprop_pub cell_lineprop_pub_cell_lineprop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_lineprop_pub
    ADD CONSTRAINT cell_lineprop_pub_cell_lineprop_id_fkey FOREIGN KEY (cell_lineprop_id) REFERENCES public.cell_lineprop(cell_lineprop_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_lineprop_pub cell_lineprop_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_lineprop_pub
    ADD CONSTRAINT cell_lineprop_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cell_lineprop cell_lineprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cell_lineprop
    ADD CONSTRAINT cell_lineprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cvterm cvterm_cv_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvterm
    ADD CONSTRAINT cvterm_cv_id_fkey FOREIGN KEY (cv_id) REFERENCES public.cv(cv_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cvterm_dbxref cvterm_dbxref_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvterm_dbxref
    ADD CONSTRAINT cvterm_dbxref_cvterm_id_fkey FOREIGN KEY (cvterm_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cvterm_dbxref cvterm_dbxref_dbxref_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvterm_dbxref
    ADD CONSTRAINT cvterm_dbxref_dbxref_id_fkey FOREIGN KEY (dbxref_id) REFERENCES public.dbxref(dbxref_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cvterm cvterm_dbxref_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvterm
    ADD CONSTRAINT cvterm_dbxref_id_fkey FOREIGN KEY (dbxref_id) REFERENCES public.dbxref(dbxref_id) ON DELETE SET NULL;


--
-- Name: cvterm_relationship cvterm_relationship_object_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvterm_relationship
    ADD CONSTRAINT cvterm_relationship_object_id_fkey FOREIGN KEY (object_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cvterm_relationship cvterm_relationship_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvterm_relationship
    ADD CONSTRAINT cvterm_relationship_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cvterm_relationship cvterm_relationship_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvterm_relationship
    ADD CONSTRAINT cvterm_relationship_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cvtermpath cvtermpath_object_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvtermpath
    ADD CONSTRAINT cvtermpath_object_id_fkey FOREIGN KEY (object_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cvtermpath cvtermpath_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvtermpath
    ADD CONSTRAINT cvtermpath_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cvtermpath cvtermpath_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvtermpath
    ADD CONSTRAINT cvtermpath_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE SET NULL;


--
-- Name: cvtermprop cvtermprop_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvtermprop
    ADD CONSTRAINT cvtermprop_cvterm_id_fkey FOREIGN KEY (cvterm_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cvtermprop cvtermprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvtermprop
    ADD CONSTRAINT cvtermprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cvtermsynonym cvtermsynonym_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvtermsynonym
    ADD CONSTRAINT cvtermsynonym_cvterm_id_fkey FOREIGN KEY (cvterm_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cvtermsynonym cvtermsynonym_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cvtermsynonym
    ADD CONSTRAINT cvtermsynonym_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: db db_contact_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.db
    ADD CONSTRAINT db_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES public.contact(contact_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dbxref dbxref_db_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dbxref
    ADD CONSTRAINT dbxref_db_id_fkey FOREIGN KEY (db_id) REFERENCES public.db(db_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dbxrefprop dbxrefprop_dbxref_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dbxrefprop
    ADD CONSTRAINT dbxrefprop_dbxref_id_fkey FOREIGN KEY (dbxref_id) REFERENCES public.dbxref(dbxref_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dbxrefprop dbxrefprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dbxrefprop
    ADD CONSTRAINT dbxrefprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: environment_cvterm environment_cvterm_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.environment_cvterm
    ADD CONSTRAINT environment_cvterm_cvterm_id_fkey FOREIGN KEY (cvterm_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: environment_cvterm environment_cvterm_environment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.environment_cvterm
    ADD CONSTRAINT environment_cvterm_environment_id_fkey FOREIGN KEY (environment_id) REFERENCES public.environment(environment_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: expression_cvterm expression_cvterm_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expression_cvterm
    ADD CONSTRAINT expression_cvterm_cvterm_id_fkey FOREIGN KEY (cvterm_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: expression_cvterm expression_cvterm_cvterm_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expression_cvterm
    ADD CONSTRAINT expression_cvterm_cvterm_type_id_fkey FOREIGN KEY (cvterm_type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: expression_cvterm expression_cvterm_expression_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expression_cvterm
    ADD CONSTRAINT expression_cvterm_expression_id_fkey FOREIGN KEY (expression_id) REFERENCES public.expression(expression_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: expression_cvtermprop expression_cvtermprop_expression_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expression_cvtermprop
    ADD CONSTRAINT expression_cvtermprop_expression_cvterm_id_fkey FOREIGN KEY (expression_cvterm_id) REFERENCES public.expression_cvterm(expression_cvterm_id) ON DELETE CASCADE;


--
-- Name: expression_cvtermprop expression_cvtermprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expression_cvtermprop
    ADD CONSTRAINT expression_cvtermprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: expression_image expression_image_eimage_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expression_image
    ADD CONSTRAINT expression_image_eimage_id_fkey FOREIGN KEY (eimage_id) REFERENCES public.eimage(eimage_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: expression_image expression_image_expression_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expression_image
    ADD CONSTRAINT expression_image_expression_id_fkey FOREIGN KEY (expression_id) REFERENCES public.expression(expression_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: expression_pub expression_pub_expression_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expression_pub
    ADD CONSTRAINT expression_pub_expression_id_fkey FOREIGN KEY (expression_id) REFERENCES public.expression(expression_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: expression_pub expression_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expression_pub
    ADD CONSTRAINT expression_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: expressionprop expressionprop_expression_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expressionprop
    ADD CONSTRAINT expressionprop_expression_id_fkey FOREIGN KEY (expression_id) REFERENCES public.expression(expression_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: expressionprop expressionprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expressionprop
    ADD CONSTRAINT expressionprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_cvterm feature_cvterm_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_cvterm
    ADD CONSTRAINT feature_cvterm_cvterm_id_fkey FOREIGN KEY (cvterm_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_cvterm_dbxref feature_cvterm_dbxref_dbxref_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_cvterm_dbxref
    ADD CONSTRAINT feature_cvterm_dbxref_dbxref_id_fkey FOREIGN KEY (dbxref_id) REFERENCES public.dbxref(dbxref_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_cvterm_dbxref feature_cvterm_dbxref_feature_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_cvterm_dbxref
    ADD CONSTRAINT feature_cvterm_dbxref_feature_cvterm_id_fkey FOREIGN KEY (feature_cvterm_id) REFERENCES public.feature_cvterm(feature_cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_cvterm feature_cvterm_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_cvterm
    ADD CONSTRAINT feature_cvterm_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.feature(feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_cvterm feature_cvterm_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_cvterm
    ADD CONSTRAINT feature_cvterm_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_cvtermprop feature_cvtermprop_feature_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_cvtermprop
    ADD CONSTRAINT feature_cvtermprop_feature_cvterm_id_fkey FOREIGN KEY (feature_cvterm_id) REFERENCES public.feature_cvterm(feature_cvterm_id) ON DELETE CASCADE;


--
-- Name: feature_cvtermprop feature_cvtermprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_cvtermprop
    ADD CONSTRAINT feature_cvtermprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_dbxref feature_dbxref_dbxref_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_dbxref
    ADD CONSTRAINT feature_dbxref_dbxref_id_fkey FOREIGN KEY (dbxref_id) REFERENCES public.dbxref(dbxref_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_dbxref feature_dbxref_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_dbxref
    ADD CONSTRAINT feature_dbxref_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.feature(feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature feature_dbxref_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature
    ADD CONSTRAINT feature_dbxref_id_fkey FOREIGN KEY (dbxref_id) REFERENCES public.dbxref(dbxref_id) ON DELETE SET NULL;


--
-- Name: feature_expression feature_expression_expression_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_expression
    ADD CONSTRAINT feature_expression_expression_id_fkey FOREIGN KEY (expression_id) REFERENCES public.expression(expression_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_expression feature_expression_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_expression
    ADD CONSTRAINT feature_expression_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.feature(feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_expression feature_expression_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_expression
    ADD CONSTRAINT feature_expression_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_expressionprop feature_expressionprop_feature_expression_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_expressionprop
    ADD CONSTRAINT feature_expressionprop_feature_expression_id_fkey FOREIGN KEY (feature_expression_id) REFERENCES public.feature_expression(feature_expression_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_expressionprop feature_expressionprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_expressionprop
    ADD CONSTRAINT feature_expressionprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_genotype feature_genotype_chromosome_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_genotype
    ADD CONSTRAINT feature_genotype_chromosome_id_fkey FOREIGN KEY (chromosome_id) REFERENCES public.feature(feature_id) ON DELETE SET NULL;


--
-- Name: feature_genotype feature_genotype_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_genotype
    ADD CONSTRAINT feature_genotype_cvterm_id_fkey FOREIGN KEY (cvterm_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_genotype feature_genotype_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_genotype
    ADD CONSTRAINT feature_genotype_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.feature(feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_genotype feature_genotype_genotype_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_genotype
    ADD CONSTRAINT feature_genotype_genotype_id_fkey FOREIGN KEY (genotype_id) REFERENCES public.genotype(genotype_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_grpmember feature_grpmember_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_grpmember
    ADD CONSTRAINT feature_grpmember_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.feature(feature_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_grpmember feature_grpmember_grpmember_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_grpmember
    ADD CONSTRAINT feature_grpmember_grpmember_id_fkey FOREIGN KEY (grpmember_id) REFERENCES public.grpmember(grpmember_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_grpmember_pub feature_grpmember_pub_feature_grpmember_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_grpmember_pub
    ADD CONSTRAINT feature_grpmember_pub_feature_grpmember_id_fkey FOREIGN KEY (feature_grpmember_id) REFERENCES public.feature_grpmember(feature_grpmember_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_grpmember_pub feature_grpmember_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_grpmember_pub
    ADD CONSTRAINT feature_grpmember_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_humanhealth_dbxref feature_humanhealth_dbxref_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_humanhealth_dbxref
    ADD CONSTRAINT feature_humanhealth_dbxref_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.feature(feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_humanhealth_dbxref feature_humanhealth_dbxref_humanhealth_dbxref_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_humanhealth_dbxref
    ADD CONSTRAINT feature_humanhealth_dbxref_humanhealth_dbxref_id_fkey FOREIGN KEY (humanhealth_dbxref_id) REFERENCES public.humanhealth_dbxref(humanhealth_dbxref_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_humanhealth_dbxref feature_humanhealth_dbxref_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_humanhealth_dbxref
    ADD CONSTRAINT feature_humanhealth_dbxref_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_interaction feature_interaction_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_interaction
    ADD CONSTRAINT feature_interaction_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.feature(feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_interaction feature_interaction_interaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_interaction
    ADD CONSTRAINT feature_interaction_interaction_id_fkey FOREIGN KEY (interaction_id) REFERENCES public.interaction(interaction_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_interaction_pub feature_interaction_pub_feature_interaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_interaction_pub
    ADD CONSTRAINT feature_interaction_pub_feature_interaction_id_fkey FOREIGN KEY (feature_interaction_id) REFERENCES public.feature_interaction(feature_interaction_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_interaction_pub feature_interaction_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_interaction_pub
    ADD CONSTRAINT feature_interaction_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_interaction feature_interaction_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_interaction
    ADD CONSTRAINT feature_interaction_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_interactionprop feature_interactionprop_feature_interaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_interactionprop
    ADD CONSTRAINT feature_interactionprop_feature_interaction_id_fkey FOREIGN KEY (feature_interaction_id) REFERENCES public.feature_interaction(feature_interaction_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_interactionprop feature_interactionprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_interactionprop
    ADD CONSTRAINT feature_interactionprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature feature_organism_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature
    ADD CONSTRAINT feature_organism_id_fkey FOREIGN KEY (organism_id) REFERENCES public.organism(organism_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_phenotype feature_phenotype_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_phenotype
    ADD CONSTRAINT feature_phenotype_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.feature(feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_phenotype feature_phenotype_phenotype_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_phenotype
    ADD CONSTRAINT feature_phenotype_phenotype_id_fkey FOREIGN KEY (phenotype_id) REFERENCES public.phenotype(phenotype_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_pub feature_pub_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_pub
    ADD CONSTRAINT feature_pub_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.feature(feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_pub feature_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_pub
    ADD CONSTRAINT feature_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_pubprop feature_pubprop_feature_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_pubprop
    ADD CONSTRAINT feature_pubprop_feature_pub_id_fkey FOREIGN KEY (feature_pub_id) REFERENCES public.feature_pub(feature_pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_pubprop feature_pubprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_pubprop
    ADD CONSTRAINT feature_pubprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_relationship feature_relationship_object_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_relationship
    ADD CONSTRAINT feature_relationship_object_id_fkey FOREIGN KEY (object_id) REFERENCES public.feature(feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_relationship_pub feature_relationship_pub_feature_relationship_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_relationship_pub
    ADD CONSTRAINT feature_relationship_pub_feature_relationship_id_fkey FOREIGN KEY (feature_relationship_id) REFERENCES public.feature_relationship(feature_relationship_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_relationship_pub feature_relationship_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_relationship_pub
    ADD CONSTRAINT feature_relationship_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_relationship feature_relationship_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_relationship
    ADD CONSTRAINT feature_relationship_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.feature(feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_relationship feature_relationship_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_relationship
    ADD CONSTRAINT feature_relationship_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_relationshipprop feature_relationshipprop_feature_relationship_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_relationshipprop
    ADD CONSTRAINT feature_relationshipprop_feature_relationship_id_fkey FOREIGN KEY (feature_relationship_id) REFERENCES public.feature_relationship(feature_relationship_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_relationshipprop_pub feature_relationshipprop_pub_feature_relationshipprop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_relationshipprop_pub
    ADD CONSTRAINT feature_relationshipprop_pub_feature_relationshipprop_id_fkey FOREIGN KEY (feature_relationshipprop_id) REFERENCES public.feature_relationshipprop(feature_relationshipprop_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_relationshipprop_pub feature_relationshipprop_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_relationshipprop_pub
    ADD CONSTRAINT feature_relationshipprop_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_relationshipprop feature_relationshipprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_relationshipprop
    ADD CONSTRAINT feature_relationshipprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_synonym feature_synonym_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_synonym
    ADD CONSTRAINT feature_synonym_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.feature(feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_synonym feature_synonym_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_synonym
    ADD CONSTRAINT feature_synonym_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature_synonym feature_synonym_synonym_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_synonym
    ADD CONSTRAINT feature_synonym_synonym_id_fkey FOREIGN KEY (synonym_id) REFERENCES public.synonym(synonym_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: feature feature_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature
    ADD CONSTRAINT feature_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: featureloc featureloc_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featureloc
    ADD CONSTRAINT featureloc_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.feature(feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: featureloc_pub featureloc_pub_featureloc_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featureloc_pub
    ADD CONSTRAINT featureloc_pub_featureloc_id_fkey FOREIGN KEY (featureloc_id) REFERENCES public.featureloc(featureloc_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: featureloc_pub featureloc_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featureloc_pub
    ADD CONSTRAINT featureloc_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: featureloc featureloc_srcfeature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featureloc
    ADD CONSTRAINT featureloc_srcfeature_id_fkey FOREIGN KEY (srcfeature_id) REFERENCES public.feature(feature_id) ON DELETE SET NULL;


--
-- Name: featuremap_pub featuremap_pub_featuremap_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featuremap_pub
    ADD CONSTRAINT featuremap_pub_featuremap_id_fkey FOREIGN KEY (featuremap_id) REFERENCES public.featuremap(featuremap_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: featuremap_pub featuremap_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featuremap_pub
    ADD CONSTRAINT featuremap_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: featuremap featuremap_unittype_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featuremap
    ADD CONSTRAINT featuremap_unittype_id_fkey FOREIGN KEY (unittype_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: featurepos featurepos_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featurepos
    ADD CONSTRAINT featurepos_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.feature(feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: featurepos featurepos_featuremap_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featurepos
    ADD CONSTRAINT featurepos_featuremap_id_fkey FOREIGN KEY (featuremap_id) REFERENCES public.featuremap(featuremap_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: featurepos featurepos_map_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featurepos
    ADD CONSTRAINT featurepos_map_feature_id_fkey FOREIGN KEY (map_feature_id) REFERENCES public.feature(feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: featureprop featureprop_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featureprop
    ADD CONSTRAINT featureprop_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.feature(feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: featureprop_pub featureprop_pub_featureprop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featureprop_pub
    ADD CONSTRAINT featureprop_pub_featureprop_id_fkey FOREIGN KEY (featureprop_id) REFERENCES public.featureprop(featureprop_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: featureprop_pub featureprop_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featureprop_pub
    ADD CONSTRAINT featureprop_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: featureprop featureprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featureprop
    ADD CONSTRAINT featureprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: featurerange featurerange_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featurerange
    ADD CONSTRAINT featurerange_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.feature(feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: featurerange featurerange_featuremap_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featurerange
    ADD CONSTRAINT featurerange_featuremap_id_fkey FOREIGN KEY (featuremap_id) REFERENCES public.featuremap(featuremap_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: featurerange featurerange_leftendf_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featurerange
    ADD CONSTRAINT featurerange_leftendf_id_fkey FOREIGN KEY (leftendf_id) REFERENCES public.feature(feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: featurerange featurerange_leftstartf_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featurerange
    ADD CONSTRAINT featurerange_leftstartf_id_fkey FOREIGN KEY (leftstartf_id) REFERENCES public.feature(feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: featurerange featurerange_rightendf_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featurerange
    ADD CONSTRAINT featurerange_rightendf_id_fkey FOREIGN KEY (rightendf_id) REFERENCES public.feature(feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: featurerange featurerange_rightstartf_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featurerange
    ADD CONSTRAINT featurerange_rightstartf_id_fkey FOREIGN KEY (rightstartf_id) REFERENCES public.feature(feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grp_cvterm grp_cvterm_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_cvterm
    ADD CONSTRAINT grp_cvterm_cvterm_id_fkey FOREIGN KEY (cvterm_id) REFERENCES public.cvterm(cvterm_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grp_cvterm grp_cvterm_grp_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_cvterm
    ADD CONSTRAINT grp_cvterm_grp_id_fkey FOREIGN KEY (grp_id) REFERENCES public.grp(grp_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grp_cvterm grp_cvterm_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_cvterm
    ADD CONSTRAINT grp_cvterm_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grp_dbxref grp_dbxref_dbxref_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_dbxref
    ADD CONSTRAINT grp_dbxref_dbxref_id_fkey FOREIGN KEY (dbxref_id) REFERENCES public.dbxref(dbxref_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grp_dbxref grp_dbxref_grp_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_dbxref
    ADD CONSTRAINT grp_dbxref_grp_id_fkey FOREIGN KEY (grp_id) REFERENCES public.grp(grp_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grp_pub grp_pub_grp_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_pub
    ADD CONSTRAINT grp_pub_grp_id_fkey FOREIGN KEY (grp_id) REFERENCES public.grp(grp_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grp_pub grp_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_pub
    ADD CONSTRAINT grp_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grp_pubprop grp_pubprop_grp_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_pubprop
    ADD CONSTRAINT grp_pubprop_grp_pub_id_fkey FOREIGN KEY (grp_pub_id) REFERENCES public.grp_pub(grp_pub_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grp_pubprop grp_pubprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_pubprop
    ADD CONSTRAINT grp_pubprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grp_relationship grp_relationship_object_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_relationship
    ADD CONSTRAINT grp_relationship_object_id_fkey FOREIGN KEY (object_id) REFERENCES public.grp(grp_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grp_relationship_pub grp_relationship_pub_grp_relationship_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_relationship_pub
    ADD CONSTRAINT grp_relationship_pub_grp_relationship_id_fkey FOREIGN KEY (grp_relationship_id) REFERENCES public.grp_relationship(grp_relationship_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grp_relationship_pub grp_relationship_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_relationship_pub
    ADD CONSTRAINT grp_relationship_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grp_relationship grp_relationship_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_relationship
    ADD CONSTRAINT grp_relationship_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.grp(grp_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grp_relationship grp_relationship_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_relationship
    ADD CONSTRAINT grp_relationship_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grp_relationshipprop grp_relationshipprop_grp_relationship_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_relationshipprop
    ADD CONSTRAINT grp_relationshipprop_grp_relationship_id_fkey FOREIGN KEY (grp_relationship_id) REFERENCES public.grp_relationship(grp_relationship_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grp_relationshipprop grp_relationshipprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_relationshipprop
    ADD CONSTRAINT grp_relationshipprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grp_synonym grp_synonym_grp_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_synonym
    ADD CONSTRAINT grp_synonym_grp_id_fkey FOREIGN KEY (grp_id) REFERENCES public.grp(grp_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grp_synonym grp_synonym_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_synonym
    ADD CONSTRAINT grp_synonym_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grp_synonym grp_synonym_synonym_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_synonym
    ADD CONSTRAINT grp_synonym_synonym_id_fkey FOREIGN KEY (synonym_id) REFERENCES public.synonym(synonym_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grp grp_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp
    ADD CONSTRAINT grp_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grpmember_cvterm grpmember_cvterm_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmember_cvterm
    ADD CONSTRAINT grpmember_cvterm_cvterm_id_fkey FOREIGN KEY (cvterm_id) REFERENCES public.cvterm(cvterm_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grpmember_cvterm grpmember_cvterm_grpmember_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmember_cvterm
    ADD CONSTRAINT grpmember_cvterm_grpmember_id_fkey FOREIGN KEY (grpmember_id) REFERENCES public.grpmember(grpmember_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grpmember_cvterm grpmember_cvterm_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmember_cvterm
    ADD CONSTRAINT grpmember_cvterm_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grpmember grpmember_grp_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmember
    ADD CONSTRAINT grpmember_grp_id_fkey FOREIGN KEY (grp_id) REFERENCES public.grp(grp_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grpmember_pub grpmember_pub_grpmember_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmember_pub
    ADD CONSTRAINT grpmember_pub_grpmember_id_fkey FOREIGN KEY (grpmember_id) REFERENCES public.grpmember(grpmember_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grpmember_pub grpmember_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmember_pub
    ADD CONSTRAINT grpmember_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grpmember grpmember_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmember
    ADD CONSTRAINT grpmember_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grpmemberprop grpmemberprop_grpmember_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmemberprop
    ADD CONSTRAINT grpmemberprop_grpmember_id_fkey FOREIGN KEY (grpmember_id) REFERENCES public.grpmember(grpmember_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grpmemberprop_pub grpmemberprop_pub_grpmemberprop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmemberprop_pub
    ADD CONSTRAINT grpmemberprop_pub_grpmemberprop_id_fkey FOREIGN KEY (grpmemberprop_id) REFERENCES public.grpmemberprop(grpmemberprop_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grpmemberprop_pub grpmemberprop_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmemberprop_pub
    ADD CONSTRAINT grpmemberprop_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grpmemberprop grpmemberprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpmemberprop
    ADD CONSTRAINT grpmemberprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grpprop grpprop_grp_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpprop
    ADD CONSTRAINT grpprop_grp_id_fkey FOREIGN KEY (grp_id) REFERENCES public.grp(grp_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grpprop_pub grpprop_pub_grpprop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpprop_pub
    ADD CONSTRAINT grpprop_pub_grpprop_id_fkey FOREIGN KEY (grpprop_id) REFERENCES public.grpprop(grpprop_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grpprop_pub grpprop_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpprop_pub
    ADD CONSTRAINT grpprop_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: grpprop grpprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grpprop
    ADD CONSTRAINT grpprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_cvterm humanhealth_cvterm_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_cvterm
    ADD CONSTRAINT humanhealth_cvterm_cvterm_id_fkey FOREIGN KEY (cvterm_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_cvterm humanhealth_cvterm_humanhealth_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_cvterm
    ADD CONSTRAINT humanhealth_cvterm_humanhealth_id_fkey FOREIGN KEY (humanhealth_id) REFERENCES public.humanhealth(humanhealth_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_cvterm humanhealth_cvterm_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_cvterm
    ADD CONSTRAINT humanhealth_cvterm_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_cvtermprop humanhealth_cvtermprop_humanhealth_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_cvtermprop
    ADD CONSTRAINT humanhealth_cvtermprop_humanhealth_cvterm_id_fkey FOREIGN KEY (humanhealth_cvterm_id) REFERENCES public.humanhealth_cvterm(humanhealth_cvterm_id) ON DELETE CASCADE;


--
-- Name: humanhealth_cvtermprop humanhealth_cvtermprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_cvtermprop
    ADD CONSTRAINT humanhealth_cvtermprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_dbxref humanhealth_dbxref_dbxref_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_dbxref
    ADD CONSTRAINT humanhealth_dbxref_dbxref_id_fkey FOREIGN KEY (dbxref_id) REFERENCES public.dbxref(dbxref_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_dbxref humanhealth_dbxref_humanhealth_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_dbxref
    ADD CONSTRAINT humanhealth_dbxref_humanhealth_id_fkey FOREIGN KEY (humanhealth_id) REFERENCES public.humanhealth(humanhealth_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth humanhealth_dbxref_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth
    ADD CONSTRAINT humanhealth_dbxref_id_fkey FOREIGN KEY (dbxref_id) REFERENCES public.dbxref(dbxref_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_dbxrefprop humanhealth_dbxrefprop_humanhealth_dbxref_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_dbxrefprop
    ADD CONSTRAINT humanhealth_dbxrefprop_humanhealth_dbxref_id_fkey FOREIGN KEY (humanhealth_dbxref_id) REFERENCES public.humanhealth_dbxref(humanhealth_dbxref_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_dbxrefprop_pub humanhealth_dbxrefprop_pub_humanhealth_dbxrefprop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_dbxrefprop_pub
    ADD CONSTRAINT humanhealth_dbxrefprop_pub_humanhealth_dbxrefprop_id_fkey FOREIGN KEY (humanhealth_dbxrefprop_id) REFERENCES public.humanhealth_dbxrefprop(humanhealth_dbxrefprop_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_dbxrefprop_pub humanhealth_dbxrefprop_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_dbxrefprop_pub
    ADD CONSTRAINT humanhealth_dbxrefprop_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_dbxrefprop humanhealth_dbxrefprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_dbxrefprop
    ADD CONSTRAINT humanhealth_dbxrefprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_feature humanhealth_feature_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_feature
    ADD CONSTRAINT humanhealth_feature_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.feature(feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_feature humanhealth_feature_humanhealth_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_feature
    ADD CONSTRAINT humanhealth_feature_humanhealth_id_fkey FOREIGN KEY (humanhealth_id) REFERENCES public.humanhealth(humanhealth_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_feature humanhealth_feature_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_feature
    ADD CONSTRAINT humanhealth_feature_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_featureprop humanhealth_featureprop_humanhealth_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_featureprop
    ADD CONSTRAINT humanhealth_featureprop_humanhealth_feature_id_fkey FOREIGN KEY (humanhealth_feature_id) REFERENCES public.humanhealth_feature(humanhealth_feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_featureprop humanhealth_featureprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_featureprop
    ADD CONSTRAINT humanhealth_featureprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth humanhealth_organism_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth
    ADD CONSTRAINT humanhealth_organism_id_fkey FOREIGN KEY (organism_id) REFERENCES public.organism(organism_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_phenotype humanhealth_phenotype_humanhealth_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_phenotype
    ADD CONSTRAINT humanhealth_phenotype_humanhealth_id_fkey FOREIGN KEY (humanhealth_id) REFERENCES public.humanhealth(humanhealth_id) ON DELETE CASCADE;


--
-- Name: humanhealth_phenotype humanhealth_phenotype_phenotype_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_phenotype
    ADD CONSTRAINT humanhealth_phenotype_phenotype_id_fkey FOREIGN KEY (phenotype_id) REFERENCES public.phenotype(phenotype_id) ON DELETE CASCADE;


--
-- Name: humanhealth_phenotype humanhealth_phenotype_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_phenotype
    ADD CONSTRAINT humanhealth_phenotype_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_phenotypeprop humanhealth_phenotypeprop_humanhealth_phenotype_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_phenotypeprop
    ADD CONSTRAINT humanhealth_phenotypeprop_humanhealth_phenotype_id_fkey FOREIGN KEY (humanhealth_phenotype_id) REFERENCES public.humanhealth_phenotype(humanhealth_phenotype_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_phenotypeprop humanhealth_phenotypeprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_phenotypeprop
    ADD CONSTRAINT humanhealth_phenotypeprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_pub humanhealth_pub_humanhealth_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_pub
    ADD CONSTRAINT humanhealth_pub_humanhealth_id_fkey FOREIGN KEY (humanhealth_id) REFERENCES public.humanhealth(humanhealth_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_pub humanhealth_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_pub
    ADD CONSTRAINT humanhealth_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_pubprop humanhealth_pubprop_humanhealth_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_pubprop
    ADD CONSTRAINT humanhealth_pubprop_humanhealth_pub_id_fkey FOREIGN KEY (humanhealth_pub_id) REFERENCES public.humanhealth_pub(humanhealth_pub_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_pubprop humanhealth_pubprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_pubprop
    ADD CONSTRAINT humanhealth_pubprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_relationship humanhealth_relationship_object_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_relationship
    ADD CONSTRAINT humanhealth_relationship_object_id_fkey FOREIGN KEY (object_id) REFERENCES public.humanhealth(humanhealth_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_relationship_pub humanhealth_relationship_pub_humanhealth_relationship_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_relationship_pub
    ADD CONSTRAINT humanhealth_relationship_pub_humanhealth_relationship_id_fkey FOREIGN KEY (humanhealth_relationship_id) REFERENCES public.humanhealth_relationship(humanhealth_relationship_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_relationship_pub humanhealth_relationship_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_relationship_pub
    ADD CONSTRAINT humanhealth_relationship_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_relationship humanhealth_relationship_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_relationship
    ADD CONSTRAINT humanhealth_relationship_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.humanhealth(humanhealth_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_relationship humanhealth_relationship_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_relationship
    ADD CONSTRAINT humanhealth_relationship_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_synonym humanhealth_synonym_humanhealth_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_synonym
    ADD CONSTRAINT humanhealth_synonym_humanhealth_id_fkey FOREIGN KEY (humanhealth_id) REFERENCES public.humanhealth(humanhealth_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_synonym humanhealth_synonym_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_synonym
    ADD CONSTRAINT humanhealth_synonym_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealth_synonym humanhealth_synonym_synonym_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealth_synonym
    ADD CONSTRAINT humanhealth_synonym_synonym_id_fkey FOREIGN KEY (synonym_id) REFERENCES public.synonym(synonym_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealthprop humanhealthprop_humanhealth_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealthprop
    ADD CONSTRAINT humanhealthprop_humanhealth_id_fkey FOREIGN KEY (humanhealth_id) REFERENCES public.humanhealth(humanhealth_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealthprop_pub humanhealthprop_pub_humanhealthprop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealthprop_pub
    ADD CONSTRAINT humanhealthprop_pub_humanhealthprop_id_fkey FOREIGN KEY (humanhealthprop_id) REFERENCES public.humanhealthprop(humanhealthprop_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealthprop_pub humanhealthprop_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealthprop_pub
    ADD CONSTRAINT humanhealthprop_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: humanhealthprop humanhealthprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.humanhealthprop
    ADD CONSTRAINT humanhealthprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: interaction_cell_line interaction_cell_line_cell_line_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_cell_line
    ADD CONSTRAINT interaction_cell_line_cell_line_id_fkey FOREIGN KEY (cell_line_id) REFERENCES public.cell_line(cell_line_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: interaction_cell_line interaction_cell_line_interaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_cell_line
    ADD CONSTRAINT interaction_cell_line_interaction_id_fkey FOREIGN KEY (interaction_id) REFERENCES public.interaction(interaction_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: interaction_cell_line interaction_cell_line_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_cell_line
    ADD CONSTRAINT interaction_cell_line_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: interaction_cvterm interaction_cvterm_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_cvterm
    ADD CONSTRAINT interaction_cvterm_cvterm_id_fkey FOREIGN KEY (cvterm_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: interaction_cvterm interaction_cvterm_interaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_cvterm
    ADD CONSTRAINT interaction_cvterm_interaction_id_fkey FOREIGN KEY (interaction_id) REFERENCES public.interaction(interaction_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: interaction_cvtermprop interaction_cvtermprop_interaction_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_cvtermprop
    ADD CONSTRAINT interaction_cvtermprop_interaction_cvterm_id_fkey FOREIGN KEY (interaction_cvterm_id) REFERENCES public.interaction_cvterm(interaction_cvterm_id) ON DELETE CASCADE;


--
-- Name: interaction_cvtermprop interaction_cvtermprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_cvtermprop
    ADD CONSTRAINT interaction_cvtermprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: interaction_expression interaction_expression_expression_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_expression
    ADD CONSTRAINT interaction_expression_expression_id_fkey FOREIGN KEY (expression_id) REFERENCES public.expression(expression_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: interaction_expression interaction_expression_interaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_expression
    ADD CONSTRAINT interaction_expression_interaction_id_fkey FOREIGN KEY (interaction_id) REFERENCES public.interaction(interaction_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: interaction_expression interaction_expression_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_expression
    ADD CONSTRAINT interaction_expression_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: interaction_expressionprop interaction_expressionprop_interaction_expression_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_expressionprop
    ADD CONSTRAINT interaction_expressionprop_interaction_expression_id_fkey FOREIGN KEY (interaction_expression_id) REFERENCES public.interaction_expression(interaction_expression_id) ON DELETE CASCADE;


--
-- Name: interaction_expressionprop interaction_expressionprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_expressionprop
    ADD CONSTRAINT interaction_expressionprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: interaction_group_feature_interaction interaction_group_feature_interacti_feature_interaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_group_feature_interaction
    ADD CONSTRAINT interaction_group_feature_interacti_feature_interaction_id_fkey FOREIGN KEY (feature_interaction_id) REFERENCES public.feature_interaction(feature_interaction_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: interaction_group_feature_interaction interaction_group_feature_interaction_interaction_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_group_feature_interaction
    ADD CONSTRAINT interaction_group_feature_interaction_interaction_group_id_fkey FOREIGN KEY (interaction_group_id) REFERENCES public.interaction_group(interaction_group_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: interaction_pub interaction_pub_interaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_pub
    ADD CONSTRAINT interaction_pub_interaction_id_fkey FOREIGN KEY (interaction_id) REFERENCES public.interaction(interaction_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: interaction_pub interaction_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_pub
    ADD CONSTRAINT interaction_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: interaction interaction_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction
    ADD CONSTRAINT interaction_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: interactionprop interactionprop_interaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interactionprop
    ADD CONSTRAINT interactionprop_interaction_id_fkey FOREIGN KEY (interaction_id) REFERENCES public.interaction(interaction_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: interactionprop_pub interactionprop_pub_interactionprop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interactionprop_pub
    ADD CONSTRAINT interactionprop_pub_interactionprop_id_fkey FOREIGN KEY (interactionprop_id) REFERENCES public.interactionprop(interactionprop_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: interactionprop_pub interactionprop_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interactionprop_pub
    ADD CONSTRAINT interactionprop_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: interactionprop interactionprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interactionprop
    ADD CONSTRAINT interactionprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_cvterm library_cvterm_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_cvterm
    ADD CONSTRAINT library_cvterm_cvterm_id_fkey FOREIGN KEY (cvterm_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_cvterm library_cvterm_library_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_cvterm
    ADD CONSTRAINT library_cvterm_library_id_fkey FOREIGN KEY (library_id) REFERENCES public.library(library_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_cvterm library_cvterm_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_cvterm
    ADD CONSTRAINT library_cvterm_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_cvtermprop library_cvtermprop_library_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_cvtermprop
    ADD CONSTRAINT library_cvtermprop_library_cvterm_id_fkey FOREIGN KEY (library_cvterm_id) REFERENCES public.library_cvterm(library_cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_cvtermprop library_cvtermprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_cvtermprop
    ADD CONSTRAINT library_cvtermprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id);


--
-- Name: library_dbxref library_dbxref_dbxref_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_dbxref
    ADD CONSTRAINT library_dbxref_dbxref_id_fkey FOREIGN KEY (dbxref_id) REFERENCES public.dbxref(dbxref_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_dbxref library_dbxref_library_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_dbxref
    ADD CONSTRAINT library_dbxref_library_id_fkey FOREIGN KEY (library_id) REFERENCES public.library(library_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_dbxrefprop library_dbxrefprop_library_dbxref_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_dbxrefprop
    ADD CONSTRAINT library_dbxrefprop_library_dbxref_id_fkey FOREIGN KEY (library_dbxref_id) REFERENCES public.library_dbxref(library_dbxref_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_dbxrefprop library_dbxrefprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_dbxrefprop
    ADD CONSTRAINT library_dbxrefprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_expression library_expression_expression_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_expression
    ADD CONSTRAINT library_expression_expression_id_fkey FOREIGN KEY (expression_id) REFERENCES public.expression(expression_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_expression library_expression_library_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_expression
    ADD CONSTRAINT library_expression_library_id_fkey FOREIGN KEY (library_id) REFERENCES public.library(library_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_expression library_expression_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_expression
    ADD CONSTRAINT library_expression_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_expressionprop library_expressionprop_library_expression_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_expressionprop
    ADD CONSTRAINT library_expressionprop_library_expression_id_fkey FOREIGN KEY (library_expression_id) REFERENCES public.library_expression(library_expression_id) ON DELETE CASCADE;


--
-- Name: library_expressionprop library_expressionprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_expressionprop
    ADD CONSTRAINT library_expressionprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_feature library_feature_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_feature
    ADD CONSTRAINT library_feature_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.feature(feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_feature library_feature_library_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_feature
    ADD CONSTRAINT library_feature_library_id_fkey FOREIGN KEY (library_id) REFERENCES public.library(library_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_featureprop library_featureprop_library_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_featureprop
    ADD CONSTRAINT library_featureprop_library_feature_id_fkey FOREIGN KEY (library_feature_id) REFERENCES public.library_feature(library_feature_id) ON DELETE CASCADE;


--
-- Name: library_featureprop library_featureprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_featureprop
    ADD CONSTRAINT library_featureprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_grpmember library_grpmember_grpmember_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_grpmember
    ADD CONSTRAINT library_grpmember_grpmember_id_fkey FOREIGN KEY (grpmember_id) REFERENCES public.grpmember(grpmember_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_grpmember library_grpmember_library_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_grpmember
    ADD CONSTRAINT library_grpmember_library_id_fkey FOREIGN KEY (library_id) REFERENCES public.library(library_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_humanhealth library_humanhealth_humanhealth_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_humanhealth
    ADD CONSTRAINT library_humanhealth_humanhealth_id_fkey FOREIGN KEY (humanhealth_id) REFERENCES public.humanhealth(humanhealth_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_humanhealth library_humanhealth_library_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_humanhealth
    ADD CONSTRAINT library_humanhealth_library_id_fkey FOREIGN KEY (library_id) REFERENCES public.library(library_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_humanhealth library_humanhealth_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_humanhealth
    ADD CONSTRAINT library_humanhealth_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_humanhealthprop library_humanhealthprop_library_humanhealth_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_humanhealthprop
    ADD CONSTRAINT library_humanhealthprop_library_humanhealth_id_fkey FOREIGN KEY (library_humanhealth_id) REFERENCES public.library_humanhealth(library_humanhealth_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_humanhealthprop library_humanhealthprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_humanhealthprop
    ADD CONSTRAINT library_humanhealthprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_interaction library_interaction_interaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_interaction
    ADD CONSTRAINT library_interaction_interaction_id_fkey FOREIGN KEY (interaction_id) REFERENCES public.interaction(interaction_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_interaction library_interaction_library_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_interaction
    ADD CONSTRAINT library_interaction_library_id_fkey FOREIGN KEY (library_id) REFERENCES public.library(library_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_interaction library_interaction_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_interaction
    ADD CONSTRAINT library_interaction_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library library_organism_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library
    ADD CONSTRAINT library_organism_id_fkey FOREIGN KEY (organism_id) REFERENCES public.organism(organism_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_pub library_pub_library_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_pub
    ADD CONSTRAINT library_pub_library_id_fkey FOREIGN KEY (library_id) REFERENCES public.library(library_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_pub library_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_pub
    ADD CONSTRAINT library_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_relationship library_relationship_object_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_relationship
    ADD CONSTRAINT library_relationship_object_id_fkey FOREIGN KEY (object_id) REFERENCES public.library(library_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_relationship_pub library_relationship_pub_library_relationship_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_relationship_pub
    ADD CONSTRAINT library_relationship_pub_library_relationship_id_fkey FOREIGN KEY (library_relationship_id) REFERENCES public.library_relationship(library_relationship_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_relationship_pub library_relationship_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_relationship_pub
    ADD CONSTRAINT library_relationship_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_relationship library_relationship_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_relationship
    ADD CONSTRAINT library_relationship_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.library(library_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_relationship library_relationship_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_relationship
    ADD CONSTRAINT library_relationship_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_strain library_strain_library_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_strain
    ADD CONSTRAINT library_strain_library_id_fkey FOREIGN KEY (library_id) REFERENCES public.library(library_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_strain library_strain_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_strain
    ADD CONSTRAINT library_strain_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_strain library_strain_strain_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_strain
    ADD CONSTRAINT library_strain_strain_id_fkey FOREIGN KEY (strain_id) REFERENCES public.strain(strain_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_strainprop library_strainprop_library_strain_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_strainprop
    ADD CONSTRAINT library_strainprop_library_strain_id_fkey FOREIGN KEY (library_strain_id) REFERENCES public.library_strain(library_strain_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_strainprop library_strainprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_strainprop
    ADD CONSTRAINT library_strainprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_synonym library_synonym_library_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_synonym
    ADD CONSTRAINT library_synonym_library_id_fkey FOREIGN KEY (library_id) REFERENCES public.library(library_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_synonym library_synonym_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_synonym
    ADD CONSTRAINT library_synonym_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library_synonym library_synonym_synonym_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library_synonym
    ADD CONSTRAINT library_synonym_synonym_id_fkey FOREIGN KEY (synonym_id) REFERENCES public.synonym(synonym_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: library library_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.library
    ADD CONSTRAINT library_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: libraryprop libraryprop_library_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.libraryprop
    ADD CONSTRAINT libraryprop_library_id_fkey FOREIGN KEY (library_id) REFERENCES public.library(library_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: libraryprop_pub libraryprop_pub_libraryprop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.libraryprop_pub
    ADD CONSTRAINT libraryprop_pub_libraryprop_id_fkey FOREIGN KEY (libraryprop_id) REFERENCES public.libraryprop(libraryprop_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: libraryprop_pub libraryprop_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.libraryprop_pub
    ADD CONSTRAINT libraryprop_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: libraryprop libraryprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.libraryprop
    ADD CONSTRAINT libraryprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: organism_cvterm organism_cvterm_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_cvterm
    ADD CONSTRAINT organism_cvterm_cvterm_id_fkey FOREIGN KEY (cvterm_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: organism_cvterm organism_cvterm_organism_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_cvterm
    ADD CONSTRAINT organism_cvterm_organism_id_fkey FOREIGN KEY (organism_id) REFERENCES public.organism(organism_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: organism_cvterm organism_cvterm_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_cvterm
    ADD CONSTRAINT organism_cvterm_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: organism_cvtermprop organism_cvtermprop_organism_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_cvtermprop
    ADD CONSTRAINT organism_cvtermprop_organism_cvterm_id_fkey FOREIGN KEY (organism_cvterm_id) REFERENCES public.organism_cvterm(organism_cvterm_id) ON DELETE CASCADE;


--
-- Name: organism_cvtermprop organism_cvtermprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_cvtermprop
    ADD CONSTRAINT organism_cvtermprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: organism_dbxref organism_dbxref_dbxref_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_dbxref
    ADD CONSTRAINT organism_dbxref_dbxref_id_fkey FOREIGN KEY (dbxref_id) REFERENCES public.dbxref(dbxref_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: organism_dbxref organism_dbxref_organism_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_dbxref
    ADD CONSTRAINT organism_dbxref_organism_id_fkey FOREIGN KEY (organism_id) REFERENCES public.organism(organism_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: organism_grpmember organism_grpmember_grpmember_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_grpmember
    ADD CONSTRAINT organism_grpmember_grpmember_id_fkey FOREIGN KEY (grpmember_id) REFERENCES public.grpmember(grpmember_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: organism_grpmember organism_grpmember_organism_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_grpmember
    ADD CONSTRAINT organism_grpmember_organism_id_fkey FOREIGN KEY (organism_id) REFERENCES public.organism(organism_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: organism_library organism_library_library_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_library
    ADD CONSTRAINT organism_library_library_id_fkey FOREIGN KEY (library_id) REFERENCES public.library(library_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: organism_library organism_library_organism_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_library
    ADD CONSTRAINT organism_library_organism_id_fkey FOREIGN KEY (organism_id) REFERENCES public.organism(organism_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: organism_pub organism_pub_organism_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_pub
    ADD CONSTRAINT organism_pub_organism_id_fkey FOREIGN KEY (organism_id) REFERENCES public.organism(organism_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: organism_pub organism_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organism_pub
    ADD CONSTRAINT organism_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: organismprop organismprop_organism_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organismprop
    ADD CONSTRAINT organismprop_organism_id_fkey FOREIGN KEY (organism_id) REFERENCES public.organism(organism_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: organismprop_pub organismprop_pub_organismprop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organismprop_pub
    ADD CONSTRAINT organismprop_pub_organismprop_id_fkey FOREIGN KEY (organismprop_id) REFERENCES public.organismprop(organismprop_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: organismprop_pub organismprop_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organismprop_pub
    ADD CONSTRAINT organismprop_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: organismprop organismprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organismprop
    ADD CONSTRAINT organismprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: phendesc phendesc_environment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phendesc
    ADD CONSTRAINT phendesc_environment_id_fkey FOREIGN KEY (environment_id) REFERENCES public.environment(environment_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: phendesc phendesc_genotype_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phendesc
    ADD CONSTRAINT phendesc_genotype_id_fkey FOREIGN KEY (genotype_id) REFERENCES public.genotype(genotype_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: phendesc phendesc_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phendesc
    ADD CONSTRAINT phendesc_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: phendesc phendesc_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phendesc
    ADD CONSTRAINT phendesc_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: phenotype phenotype_assay_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype
    ADD CONSTRAINT phenotype_assay_id_fkey FOREIGN KEY (assay_id) REFERENCES public.cvterm(cvterm_id) ON DELETE SET NULL;


--
-- Name: phenotype phenotype_attr_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype
    ADD CONSTRAINT phenotype_attr_id_fkey FOREIGN KEY (attr_id) REFERENCES public.cvterm(cvterm_id) ON DELETE SET NULL;


--
-- Name: phenotype_comparison_cvterm phenotype_comparison_cvterm_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype_comparison_cvterm
    ADD CONSTRAINT phenotype_comparison_cvterm_cvterm_id_fkey FOREIGN KEY (cvterm_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE;


--
-- Name: phenotype_comparison_cvterm phenotype_comparison_cvterm_phenotype_comparison_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype_comparison_cvterm
    ADD CONSTRAINT phenotype_comparison_cvterm_phenotype_comparison_id_fkey FOREIGN KEY (phenotype_comparison_id) REFERENCES public.phenotype_comparison(phenotype_comparison_id) ON DELETE CASCADE;


--
-- Name: phenotype_comparison phenotype_comparison_environment1_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype_comparison
    ADD CONSTRAINT phenotype_comparison_environment1_id_fkey FOREIGN KEY (environment1_id) REFERENCES public.environment(environment_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: phenotype_comparison phenotype_comparison_environment2_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype_comparison
    ADD CONSTRAINT phenotype_comparison_environment2_id_fkey FOREIGN KEY (environment2_id) REFERENCES public.environment(environment_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: phenotype_comparison phenotype_comparison_genotype1_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype_comparison
    ADD CONSTRAINT phenotype_comparison_genotype1_id_fkey FOREIGN KEY (genotype1_id) REFERENCES public.genotype(genotype_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: phenotype_comparison phenotype_comparison_genotype2_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype_comparison
    ADD CONSTRAINT phenotype_comparison_genotype2_id_fkey FOREIGN KEY (genotype2_id) REFERENCES public.genotype(genotype_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: phenotype_comparison phenotype_comparison_organism_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype_comparison
    ADD CONSTRAINT phenotype_comparison_organism_id_fkey FOREIGN KEY (organism_id) REFERENCES public.organism(organism_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: phenotype_comparison phenotype_comparison_phenotype1_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype_comparison
    ADD CONSTRAINT phenotype_comparison_phenotype1_id_fkey FOREIGN KEY (phenotype1_id) REFERENCES public.phenotype(phenotype_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: phenotype_comparison phenotype_comparison_phenotype2_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype_comparison
    ADD CONSTRAINT phenotype_comparison_phenotype2_id_fkey FOREIGN KEY (phenotype2_id) REFERENCES public.phenotype(phenotype_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: phenotype_comparison phenotype_comparison_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype_comparison
    ADD CONSTRAINT phenotype_comparison_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: phenotype phenotype_cvalue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype
    ADD CONSTRAINT phenotype_cvalue_id_fkey FOREIGN KEY (cvalue_id) REFERENCES public.cvterm(cvterm_id) ON DELETE SET NULL;


--
-- Name: phenotype_cvterm phenotype_cvterm_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype_cvterm
    ADD CONSTRAINT phenotype_cvterm_cvterm_id_fkey FOREIGN KEY (cvterm_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: phenotype_cvterm phenotype_cvterm_phenotype_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype_cvterm
    ADD CONSTRAINT phenotype_cvterm_phenotype_id_fkey FOREIGN KEY (phenotype_id) REFERENCES public.phenotype(phenotype_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: phenotype phenotype_observable_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenotype
    ADD CONSTRAINT phenotype_observable_id_fkey FOREIGN KEY (observable_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: phenstatement phenstatement_environment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenstatement
    ADD CONSTRAINT phenstatement_environment_id_fkey FOREIGN KEY (environment_id) REFERENCES public.environment(environment_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: phenstatement phenstatement_genotype_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenstatement
    ADD CONSTRAINT phenstatement_genotype_id_fkey FOREIGN KEY (genotype_id) REFERENCES public.genotype(genotype_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: phenstatement phenstatement_phenotype_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenstatement
    ADD CONSTRAINT phenstatement_phenotype_id_fkey FOREIGN KEY (phenotype_id) REFERENCES public.phenotype(phenotype_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: phenstatement phenstatement_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenstatement
    ADD CONSTRAINT phenstatement_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: phenstatement phenstatement_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.phenstatement
    ADD CONSTRAINT phenstatement_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pub_dbxref pub_dbxref_dbxref_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pub_dbxref
    ADD CONSTRAINT pub_dbxref_dbxref_id_fkey FOREIGN KEY (dbxref_id) REFERENCES public.dbxref(dbxref_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pub_dbxref pub_dbxref_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pub_dbxref
    ADD CONSTRAINT pub_dbxref_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pub_relationship pub_relationship_object_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pub_relationship
    ADD CONSTRAINT pub_relationship_object_id_fkey FOREIGN KEY (object_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pub_relationship pub_relationship_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pub_relationship
    ADD CONSTRAINT pub_relationship_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pub_relationship pub_relationship_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pub_relationship
    ADD CONSTRAINT pub_relationship_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pub pub_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pub
    ADD CONSTRAINT pub_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pubauthor pubauthor_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pubauthor
    ADD CONSTRAINT pubauthor_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pubprop pubprop_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pubprop
    ADD CONSTRAINT pubprop_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pubprop pubprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pubprop
    ADD CONSTRAINT pubprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain_cvterm strain_cvterm_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_cvterm
    ADD CONSTRAINT strain_cvterm_cvterm_id_fkey FOREIGN KEY (cvterm_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain_cvterm strain_cvterm_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_cvterm
    ADD CONSTRAINT strain_cvterm_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain_cvterm strain_cvterm_strain_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_cvterm
    ADD CONSTRAINT strain_cvterm_strain_id_fkey FOREIGN KEY (strain_id) REFERENCES public.strain(strain_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain_cvtermprop strain_cvtermprop_strain_cvterm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_cvtermprop
    ADD CONSTRAINT strain_cvtermprop_strain_cvterm_id_fkey FOREIGN KEY (strain_cvterm_id) REFERENCES public.strain_cvterm(strain_cvterm_id) ON DELETE CASCADE;


--
-- Name: strain_cvtermprop strain_cvtermprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_cvtermprop
    ADD CONSTRAINT strain_cvtermprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain_dbxref strain_dbxref_dbxref_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_dbxref
    ADD CONSTRAINT strain_dbxref_dbxref_id_fkey FOREIGN KEY (dbxref_id) REFERENCES public.dbxref(dbxref_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain strain_dbxref_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain
    ADD CONSTRAINT strain_dbxref_id_fkey FOREIGN KEY (dbxref_id) REFERENCES public.dbxref(dbxref_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain_dbxref strain_dbxref_strain_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_dbxref
    ADD CONSTRAINT strain_dbxref_strain_id_fkey FOREIGN KEY (strain_id) REFERENCES public.strain(strain_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain_feature strain_feature_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_feature
    ADD CONSTRAINT strain_feature_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.feature(feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain_feature strain_feature_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_feature
    ADD CONSTRAINT strain_feature_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain_feature strain_feature_strain_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_feature
    ADD CONSTRAINT strain_feature_strain_id_fkey FOREIGN KEY (strain_id) REFERENCES public.strain(strain_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain_featureprop strain_featureprop_strain_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_featureprop
    ADD CONSTRAINT strain_featureprop_strain_feature_id_fkey FOREIGN KEY (strain_feature_id) REFERENCES public.strain_feature(strain_feature_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain_featureprop strain_featureprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_featureprop
    ADD CONSTRAINT strain_featureprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain strain_organism_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain
    ADD CONSTRAINT strain_organism_id_fkey FOREIGN KEY (organism_id) REFERENCES public.organism(organism_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain_phenotype strain_phenotype_phenotype_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_phenotype
    ADD CONSTRAINT strain_phenotype_phenotype_id_fkey FOREIGN KEY (phenotype_id) REFERENCES public.phenotype(phenotype_id) ON DELETE CASCADE;


--
-- Name: strain_phenotype strain_phenotype_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_phenotype
    ADD CONSTRAINT strain_phenotype_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain_phenotype strain_phenotype_strain_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_phenotype
    ADD CONSTRAINT strain_phenotype_strain_id_fkey FOREIGN KEY (strain_id) REFERENCES public.strain(strain_id) ON DELETE CASCADE;


--
-- Name: strain_phenotypeprop strain_phenotypeprop_strain_phenotype_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_phenotypeprop
    ADD CONSTRAINT strain_phenotypeprop_strain_phenotype_id_fkey FOREIGN KEY (strain_phenotype_id) REFERENCES public.strain_phenotype(strain_phenotype_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain_phenotypeprop strain_phenotypeprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_phenotypeprop
    ADD CONSTRAINT strain_phenotypeprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain_pub strain_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_pub
    ADD CONSTRAINT strain_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain_pub strain_pub_strain_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_pub
    ADD CONSTRAINT strain_pub_strain_id_fkey FOREIGN KEY (strain_id) REFERENCES public.strain(strain_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain_relationship strain_relationship_object_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_relationship
    ADD CONSTRAINT strain_relationship_object_id_fkey FOREIGN KEY (object_id) REFERENCES public.strain(strain_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain_relationship_pub strain_relationship_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_relationship_pub
    ADD CONSTRAINT strain_relationship_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain_relationship_pub strain_relationship_pub_strain_relationship_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_relationship_pub
    ADD CONSTRAINT strain_relationship_pub_strain_relationship_id_fkey FOREIGN KEY (strain_relationship_id) REFERENCES public.strain_relationship(strain_relationship_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain_relationship strain_relationship_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_relationship
    ADD CONSTRAINT strain_relationship_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.strain(strain_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain_relationship strain_relationship_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_relationship
    ADD CONSTRAINT strain_relationship_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain_synonym strain_synonym_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_synonym
    ADD CONSTRAINT strain_synonym_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain_synonym strain_synonym_strain_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_synonym
    ADD CONSTRAINT strain_synonym_strain_id_fkey FOREIGN KEY (strain_id) REFERENCES public.strain(strain_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strain_synonym strain_synonym_synonym_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strain_synonym
    ADD CONSTRAINT strain_synonym_synonym_id_fkey FOREIGN KEY (synonym_id) REFERENCES public.synonym(synonym_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strainprop_pub strainprop_pub_pub_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strainprop_pub
    ADD CONSTRAINT strainprop_pub_pub_id_fkey FOREIGN KEY (pub_id) REFERENCES public.pub(pub_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strainprop_pub strainprop_pub_strainprop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strainprop_pub
    ADD CONSTRAINT strainprop_pub_strainprop_id_fkey FOREIGN KEY (strainprop_id) REFERENCES public.strainprop(strainprop_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strainprop strainprop_strain_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strainprop
    ADD CONSTRAINT strainprop_strain_id_fkey FOREIGN KEY (strain_id) REFERENCES public.strain(strain_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: strainprop strainprop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.strainprop
    ADD CONSTRAINT strainprop_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- Name: synonym synonym_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.synonym
    ADD CONSTRAINT synonym_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.cvterm(cvterm_id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

