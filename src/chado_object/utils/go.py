"""GO and DO general routines.

.. module:: GO
   :synopsis: Lookup and general dbxref functions.

.. moduleauthor:: Ian Longden <ilongden@morgan.harvard.edu>
"""
import re
from harvdev_utils.chado_functions import (
    CodingError, feature_name_lookup, get_cvterm, get_feature_by_uniquename, feature_symbol_lookup
)
# from harvdev_utils.production import (Dbxref, Db)
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

import logging
log = logging.getLogger(__name__)

code_to_string = {
    'IMP': 'inferred from mutant phenotype',
    'IGI': 'inferred from genetic interaction',
    'IPI': 'inferred from physical interaction',
    'ISS': 'inferred from sequence or structural similarity',
    'IDA': 'inferred from direct assay',
    'IEA': 'inferred from electronic annotation',
    'IEP': 'inferred from expression pattern',
    'RCA': 'inferred from reviewed computational analysis',
    'TAS': 'traceable author statement',
    'NAS': 'non-traceable author statement',
    'IC': 'inferred by curator',
    'IGC': 'inferred from genomic context',
    'ND': 'no biological data available',
    'ISM': 'inferred from sequence model',
    'ISO': 'inferred from sequence orthology',
    'ISA': 'inferred from sequence alignment',
    'EXP': 'inferred from experiment',
    'IBA': 'inferred from biological aspect of ancestor',
    'IBD': 'inferred from biological aspect of descendant',
    'IKR': 'inferred from key residues',
    'IRD': 'inferred from rapid divergence'
    }
# get from yml now.
# quali = ['colocalizes_with', 'contributes_to', 'NOT']
# if($1 eq 'UniProtKB' or $1 eq 'FlyBase' or $1 eq 'BHF-UCL' or $1 eq 'GOC' or $1 eq 'HGNC' or $1 eq 'IntAct' or $1
# eq 'InterPro' or $1 eq 'MGI' or $1 eq 'PINC' or $1 eq 'Reactome' or $1 eq 'RefGenome' ){


def process_doid(session, doid, do_dict, allowed_qualifiers, cv_name):
    """Process doid line.

    doid: string, doid bit of value i.e.
                  'DOES NOT model doid desc 1 ; DOID:00001'
                  'model of doid desc 2 ; DOID:00002'
    do_dict: dictionary to store results in should return something liek:
        {
         'docvterm': <cvterm object>, # for the doid term
         'error': [], # can be many errors so check for empty array for no error)
         'qualifier': one of the allowed qualifiers.
         'provenance': 'FLYBASE'
        }
    allowed_qualifiers: [], list of allowed qualifier name
                            obtained from the yml file (See GA34a as an example)
    cv_name: string, cv name to be used.
    """
    for qualifier in allowed_qualifiers:
        if doid.startswith(qualifier):
            do_dict['qualifier'] = qualifier
            doid = doid.replace(qualifier, '', 1)

    if 'qualifier' not in do_dict:
        do_dict['error'].append("No qualifier defined")

    # split doid into code and description
    fpi = {
        'do_name': 1,
        'do_code': 2,
    }
    full_pattern = r"""
        ^           # start of line
        \s*         # possible leading spaces
        (.*)        # description can have spaces
        \s*         # possible spaces
        ;           # semi colon
        \s*         # possible spaces
        DOID:       # DOID: prefix
        (\d+)       # accession 7 digit number i.e. 0000011
        \s*         # possible spaces
    """
    fields = re.search(full_pattern, doid, re.VERBOSE)
    if not fields:
        do_dict['error'].append("Failed to match DO format 'xxxxxx xxx ; DOID:d+'")
        return

    for key in fpi.keys():
        log.debug('DOTERM: {}: {} {}'.format(key, fpi[key], fields.group(fpi[key])))

    # get cvterm using the cvterm name
    cvterm_name = fields.group(fpi['do_name']).strip()
    try:
        do_dict['docvterm'] = get_cvterm(session, cv_name, cvterm_name)
    except CodingError:
        do_dict['error'].append("Could not find cv '{}' cvterm '{}'.".format(cv_name, cvterm_name))
        return
    # check the cvterm dbxref to make sure the gocode matches the accession
    docode = str(fields.group(fpi['do_code'])).strip()
    if docode != do_dict['docvterm'].dbxref.accession:
        do_dict['error'].append("{} matches {} but lookup gives {} instead?".format(cvterm_name, docode, do_dict['docvterm'].dbxref.accession))


def check_dbxref(session, do_dict, dbname, accession, allowed_dbs=None):
    """Check DBXref exists.

    Params:
      session: <session object> sql session
      do_dict: <dict> add ['error'] here if there is a problem.
      dbname: <string> db name
      accession: <string> ac cesion to check for the above db.
      allowed_dbs: <list> db names allowed to be used in evidence.
    Returns:
        symbol or None if problem with DB name.

    Check dbname exists first and in the allowed list.
    Check accession exists. Warning Error?
    """
    if allowed_dbs and dbname not in allowed_dbs:
        do_dict['error'].append("Database '{}' not found in list of allowed dbs '{}'".format(dbname, allowed_dbs))
        return None
    # Leave below in we may want to check this in the python version.
    # try:
    #     db = session.query(Db).filter(Db.name == dbname).one()
    # except NoResultFound:
    #     do_dict['error'].append("Database '{}' not found in chado".format(dbname))
    #     return None
    # try:
    #     dbxref = session.query(Dbxref).filter(Dbxref.name == dbname,
    #                                           Db.db_id == db.db_id).one()
    # except NoResultFound:
    #     do_dict['error'].append("Could not find accession '{}' for db '{}'".format(accession, dbname))
    #     return None
    return "{}:{}".format(dbname, accession)


def get_symbols(session, do_dict, bits, allowed_dbs=[]):
    """Get symbols.

    Params:
      session: <session object> sql session
      do_dict: <dict> add ['error'] here if there is a problem.
      bits: <list> symbols/db:accs to process
      allowed_dbs: <list> database names that are allowed.

    Returns:
       list of symbols.
    """
    symbols = []
    at_pattern = '@([^@]+)@'
    db_pattern = r'(\S+):(\S+)'
    for item in bits:
        fields = re.search(at_pattern, item)
        if not fields:
            fields = re.search(db_pattern, item)
            if not fields:
                do_dict['error'].append("Only @symbol@ and DB:Acc allowed but here we have {}".format(item))
                continue
            symbol = check_dbxref(session, do_dict, fields.group(1), fields.group(2), allowed_dbs=allowed_dbs)
            if symbol:
                symbols.append(symbol)
        else:
            symbol_name = fields.group(1)
            try:
                feature = feature_symbol_lookup(session, 'gene', symbol_name)
            except NoResultFound:
                do_dict['error'].append("Unable to lookup symbol {}".format(symbol_name))
                continue
            except MultipleResultsFound:
                do_dict['error'].append("Non unique lookup for symbol {}".format(symbol_name))
                continue
            symbol_string = "FLYBASE:{}; FB:{}".format(symbol_name, feature.uniquename)
            symbols.append(symbol_string)
    return symbols


def process_evidence(session, do_dict, evidence, allowed_codes=[], with_required=[], go_format=False,
                     allowed_dbs=[]):
    """Process the evidence bit.

    Params:
        session: <session object> sql session
        do_dict: <dict> store for dta extracted and errors
        evidence: <string> evidence line i.e. 'IMP with @bob@' or 'IDA'
        allowed_codes: <list>  evidence codes that are allowed.
        with_required: <list> evidence codes that require a with/by in the statement.
        go_format: <bool> output in go format (Default if False).
        allowed_dbs: <list> db names allowed to be used in evidence.
    Returns:
       dictionary of evidence data with errors if found.
    """
    bits = evidence.split()
    do_dict['evidence_code'] = bits.pop(0)  # first element should be the code
    if allowed_codes and do_dict['evidence_code'] not in allowed_codes:
        message = "{} Not an allowed evidence code must be one of {}".format(do_dict['evidence_code'], allowed_codes)
        do_dict['error'].append(message)
        return
    if not bits:
        if with_required and do_dict['evidence_code'] in with_required:
            do_dict['error'].append("{} requires a 'with' or 'by'".format(do_dict['evidence_code']))
        if not go_format:
            do_dict['evidence_code'] = do_dict['evidence_code']
        else:
            do_dict['evidence_code'] = code_to_string[do_dict['evidence_code']]
        return
    code_quali = bits.pop(0)  # first element after evidence code
    if not (code_quali == 'with' or code_quali == 'by'):
        do_dict['error'].append("Only with/by allowed after evidence code, {} is listed here".format(code_quali))

    if with_required and do_dict['evidence_code'] not in with_required:
        do_dict['error'].append("{} does not allow 'with' or 'by'".format(do_dict['evidence_code']))

    # If we reach here we have with or by. Check that.
    symbols = get_symbols(session, do_dict, bits, allowed_dbs)

    if not go_format and symbols:
        do_dict['evidence_code'] = "{} {} {}".format(do_dict['evidence_code'], code_quali, ', '.join(symbols))
    elif symbols:
        do_dict['evidence_code'] = "{} {} {}".format(code_to_string[do_dict['evidence_code']], code_quali, ', '.join(symbols))
    else:
        do_dict['evidence_code'] = do_dict['evidence_code']


def process_DO_line(session, line, cv_name, allowed_qualifiers, allowed_symbols, allowed_codes):
    """From string generate and validate DO.

    Params:
        session: <session object> sql session
        line: <string> DO line (see Examples)
        allowed_qualifiers: <list> qualifiers that are allowed.
        allowed_symbols: <list> feature types the symbols are allowd to be.
        allowed_codes: <list> codes allowed to be used in evidence.

    Examples:-
    1) Parkinson's disease ; DOID:14330 | CEA with @symbol-15@
    2) model of hereditary spastic paraplegia 31 ; DOID:0110782 | CEA
    3) ameliorates neuronal ceroid lipofuscinosis 4B ; DOID:0110720 | modeled by @symbol-16@

    GA34a: examples
    allowed_qualifiers: ['model of', 'ameliorates', 'exacerbates', 'DOES NOT model', 'DOES NOT ameliorate', 'DOES NOT exacerbate']
    allowed_symbols: ['allele']
    allowed:_codes: ['CEC, 'CEA' ,'modeled']

    return dict of:-
        {
         'docvterm': <cvterm object>,
         'error': [], # can be many errors so check for empty array for no error)
         'qualifier': one of the allowed qualifiers.
         'provenance': 'FLYBASE'
         'evidence_code':   # with symbols expanded to i.e. for 1
                             # CEA with FLYBASE:symbol-15; FB:FBgn0001500
        }

    cv_name: cv name
    """
    do_dict = {'error': [],
               'provenance': 'FlyBase',
               'docvterm': None}
    # split into DOID and evidence
    doid, evidence = line.split('|')
    if not evidence:
        message = "Could not split line by | into doid and evidence"
        do_dict['error'].append(message)
        return do_dict
    process_doid(session, doid, do_dict, allowed_qualifiers, cv_name)
    process_evidence(session, do_dict, evidence, allowed_codes=allowed_codes)
    return do_dict


def process_provenance(go_dict, provenance, allowed_provenance):
    """Check the provenance is legal.

    Params:
        go_dict: <dict> Add provence and errors here.
        provenance: <string> provenance db name to be checked.
        allowed_provenance: <list> db names alloawed for provenance
    """
    if not provenance:
        return
    provenance = provenance[:-1]  # remove the ':' at the end
    if provenance not in allowed_provenance:
        message = "{} Not a valid provenance must be one of  {}".format(provenance, allowed_provenance)
        go_dict['error'].append(message)
        return
    go_dict['provenance'] = provenance


def process_go(session, go_dict, go_name, go_code, go_cv_name):
    """Check the GO name and code match.

    Params:
      session: <session object> sql session
      go_dict: <dict> store gocvterm and possible errors here.
      go_name: <string> name of GO.
      go_code: <string> code for GO.
      go_cv_name: <string> cv name to look up GO cvterm with.
    """
    # get cvterm using the cvterm name
    cvterm_name = go_name.strip()
    go_dict['gocvterm'] = cvterm = get_cvterm(session, go_cv_name, cvterm_name)
    # check the cvterm dbxref to make sure the gocode matches the accession
    gocode = str(go_code).strip()
    if gocode != cvterm.dbxref.accession:
        go_dict['error'].append("{} matches {} but lookup gives {} instead?".format(cvterm_name, gocode, cvterm.dbxref.accession))


def process_qualifier(session, go_dict, qualifier, quali_cvs, allowed_qualifiers):
    """Check qualifier.

    Params:
      session: <session object> sql session
      go_dict: <dict> store gocvterm and possible errors here
      qualifier: <string> qualifier to be processed.
      quali_cvs: <dict> qualifer name -> cv name to be used if not defualt.
      allowed_qualifiers: <list> qualifiers that are allowed.

    """
    if qualifier not in allowed_qualifiers:
        go_dict['error'].append("{} Not one of the allowed values {}". format(qualifier, allowed_qualifiers))
        return

    q_cv_name = 'FlyBase miscellaneous CV'
    if qualifier in quali_cvs:
        q_cv_name = quali_cvs[qualifier]
    go_dict['qualifier'] = get_cvterm(session, q_cv_name, qualifier)


def check_for_valid_fbs(session, end_comment):
    """Check for valid features if they are in the string.

    Params:
      session: <session object> sql session
      end_comment: <string> flybae symbols.
     """
    # i.e. FLYBASE:symbol-35; FB:FBgn0000035
    problem = ""
    fields = re.search(r'FLYBASE:(.+)\s+;', end_comment)
    if fields:
        try:
            feature_name_lookup(session, fields.group(1))
        except NoResultFound:
            problem = 'Could not find FlyBase symbol {}.'.format(fields.group(1))
    fields = re.search(r'FB:(\S+)', end_comment)
    if fields:
        try:
            get_feature_by_uniquename(session, fields.group(1))
        except (NoResultFound, AttributeError):
            problem += 'Could not find FlyBase uniquename "{}"'.format(fields.group(1))
    return problem


def process_GO_line(session, line=None, cv_name=None, allowed_qualifiers=None,
                    qualifier_cv_list=[], allowed_provenances=[], with_evidence_code=None,
                    allowed_dbs=[]):
    """From string generate and validate GO.

    Params:
      session: <session object>
      line: <string> Go line to be processed.
      cv_name: <string> cv name for lookup with GO cvterm
      allowed_qualifiers: <dict> dictionary of cvterms allowed for qualifiers
      qualifier_cv_list: <dict> dictionary of cv names for different to cv_name in qualifiers.
      allowed_provenance: <list> List of provenances that are allowed.
      with_evidence_code: <list> List of evidence codes that require 'with' in comment

    Returns: <dict>
        {
         'gocvterm': <cvterm object>,
         'error': [], # can be many errors so check for empty array for no error)
         'value': expanded abbr + 'string',  # None if code lookup fails
         'provenance': string,
         'qualifer': <cvterm obj>,
         'is_not': True/False
        }

    Tests actually exist and are 0034_[x]_Gene_G24_GOCvterms_good.txt in the test suite
    NOTE: In test files go term may be different as we have only a subset and the GO number are different.
    Examples of GOOD lines:-
    a) located_in extracellular space ; GO:0002003 | IDA
       0034_a_Gene_G24_GOCvterms_good.txt
    b) part_of something ; GO:0032991 | IDA
       0034_b_Gene_G24_GOCvterms_good.txt
    c) NOT involved_in triglyceride homeostasis ; GO:0070328 | IMP
       0034_c_Gene_G24_GOCvterms_good.txt
    d) UniProtKB:involved_in extracellular space ; GO:0016458 | IMP
       0034_d_Gene_G24_GOCvterms_good.txt
    e) UniProtKB:involved_in extracellular space ; GO:0016458 | IGI with @symbol-31@
       0034_e_Gene_G24_GOCvterms_good.txt
    f) involved_in gene silencing ; GO:0016458 | IGI with UniProtKB:Q9NDJ2
       0034_f_Gene_G24_GOCvterms_good.txt
    h) involved_in extracellular space ; GO:0016458 | IGI with MGI:MGI:1100526
       check MGI:MGI: (possible problem with double ::)
    i) NOT UniProtKB:involved_in extracellular space ; GO:0016458 | IMP
    j) UniProtKB:involved_in extracellular space ; GO:0016458 | IGI with @symbol-31@ @symbol-32@
        multiple @'s

    Bad lines:-
    a) nucleolus ; GO:0002001 | IDA
       No qualifier
       0055_a_Gene_G24_GOCvterms_bad.txt
    b) NOT nucleolus ; GO:0002001 | IDA
       No qualifier
       0055_b_Gene_G24_GOCvterms_bad.txt
    c) UniProtKB:protein stabilization ; GO:0050821 | IMP
       No qualifier
       0055_c_Gene_G24_GOCvterms_bad.txt
    d) located_in extracellular space ; GO:0005615 | IDA with UniProtKB:Q9NDJ2
       'with' not allowed with IDA
       0055_d_Gene_G24_GOCvterms_bad.txt
    e) involved_in gene silencing ; GO:0016458 | IGI
       [IGI, ISS, ISO, IPI, ISA, HGI] REQUIRED with 'with'.
       0055_e_Gene_G24_GOCvterms_bad.txt
    f) part_of madeup ; GO:0009999 | IDA
       madeup cvterm does not exist.
       0055_f_Gene_G24_GOCvterms_bad.txt
    g) UniProtKB:NOT involved_in extracellular space ; GO:0016458 | IMP
       'NOT' in wrong place. ?? May need review NOTE:Gillian
    h) madeup_qualifier nucleolus ; GO:0002001 | IDA
       'madeup_qulaifer' not allowed.
    i) involved_in gene silencing ; GO:0016458 | IGI FLYBASE:madeup
       madeup non existant gene.
    j) involved_in extracellular space ; GO:0016458 | IGI with FLYBASE:symbol-31 ; FB:FBgn0005001
       FLYBASE not allowed use the @@ format.
    """
    go_dict = {'gocvterm': None,
               'error': [],
               'value': None,
               'provenance': 'FlyBase',
               'qualifier': None,
               'is_not': False}

    full_pattern = r"""
                ^           # start of line
                \s*         # possible leading spaces
                (NOT)*      # possible NOT
                \s*         # possible spaces
                (\S*:)*     # possible provenance: i.e. UniProtKB:
                \s*         # possible spaces
                (\S+)       # qualifier
                \s+         # spaces
                (\S+.*)     # anything including spaces, but be something
                \s*         # possible spaces
                ;           # semi colon
                \s*         # possible spaces
                GO:         # GO: prefix
                (\d{7})     # accession 7 digit number i.e. 0000011
                \s*         # possible spaces
                \|          # separator
                \s*         # possible spaces
                (.*$)       # evidence code and comment possibly with checks.
            """
    # USE dict as full_pattern could change often
    # so try to make code easier with indexs that can be changed easily and not missed
    fpi = {
        'is_not': 1,
        'provenance': 2,
        'qualifier': 3,
        'go_name': 4,
        'go_code': 5,
        'evi_comment': 6}

    fields = re.search(full_pattern, line, re.VERBOSE)
    if not fields:
        go_dict['error'].append("Failed to match format '(NOT) (provenance:)qualifier xxxxxx ; GO:ddddddd | XX[X]'")
        return go_dict
    elif not fields.group(fpi['qualifier']) or fields.group(fpi['qualifier']) == 'NOT':
        go_dict['error'].append('qualifier not found. This is required.')
        return go_dict
    if fields.group(fpi['is_not']):
        go_dict['is_not'] = True

    process_provenance(go_dict, fields.group(fpi['provenance']), allowed_provenances)
    process_qualifier(session, go_dict, fields.group(fpi['qualifier']), qualifier_cv_list, allowed_qualifiers)
    process_go(session, go_dict, fields.group(fpi['go_name']), fields.group(fpi['go_code']), cv_name)
    process_evidence(session, go_dict, fields.group(fpi['evi_comment']),
                     allowed_codes=[], with_required=with_evidence_code, go_format=True,
                     allowed_dbs=allowed_dbs)

    return go_dict

