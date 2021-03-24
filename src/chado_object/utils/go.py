"""GO and DO general routines.

.. module:: GO
   :synopsis: Lookup and general dbxref functions.

.. moduleauthor:: Ian Longden <ilongden@morgan.harvard.edu>
"""
import re
from harvdev_utils.chado_functions import (
    CodingError, feature_name_lookup, get_cvterm, get_feature_by_uniquename, feature_symbol_lookup
)
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from harvdev_utils.production import Db
from harvdev_utils.chado_functions import get_or_create

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
        do_dict['error'].append('Could not find cv {} cvterm {}'.format(cv_name, cvterm_name))
        return
    # check the cvterm dbxref to make sure the gocode matches the accession
    docode = str(fields.group(fpi['do_code'])).strip()
    if docode != do_dict['docvterm'].dbxref.accession:
        do_dict['error'].append("{} matches {} but lookup gives {} instead?".format(cvterm_name, docode, do_dict['docvterm'].dbxref.accession))


def process_evidence(session, do_dict, evidence, allowed_codes):
    """Process the evidence bit."""
    bits = evidence.split()
    do_dict['evidence_code'] = bits.pop(0)  # first element should be the code
    if do_dict['evidence_code'] not in allowed_codes:
        message = "{} Not an allowed evidence code must be one of {}".format(do_dict['evidence_code'], allowed_codes)
        do_dict['error'].append(message)
        return
    if not bits:
        return
    code_quali = bits.pop(0)  # first element after evidence code
    if not (code_quali == 'with' or code_quali == 'by'):
        do_dict['error'].append("Only with/by allowed after evidence code, {} is listed here".format(code_quali))

    symbols = []
    pattern = '@([^@]+)@'
    for item in bits:
        fields = re.search(pattern, item)
        if not fields:
            do_dict['error'].append("Only @symbol@ allowed but here we have {}".format(item))
            continue
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

    do_dict['evidence_code'] = "{} {} {}".format(do_dict['evidence_code'], code_quali, ', '.join(symbols))


def process_DO_line(session, line, cv_name, allowed_qualifiers, allowed_symbols, allowed_codes):
    """From string generate and validate DO.

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
    process_evidence(session, do_dict, evidence, allowed_codes)
    return do_dict


def process_GO_line(session, line, cv_name, allowed_qualifiers, quali_cvs):
    """From string generate and validate GO.

    Params:
      session: <session object>
      line: <string> Go line to be processed.
      cv_name: <string> cv name for lookup with GO cvterm
      allowed_qualifiers: <dict> dictionary of cvterms allowed for qualifiers
      quali_cvs: <dict> dictionary of cv names for different to cv_name in qualifiers.

    Returns: <dict>
        {
         'gocvterm': <cvterm object>,
         'error': [], # can be many errors so check for empty array for no error)
         'value': expanded abbr + 'string',  # None if code lookup fails
         'provenance': string,
         'prov_term': <cvterm obj>,
         'is_not': True/False
        }

    Examples of lines:-
    1) nucleolus ; GO:0002001 | IDA
    2) something ; GO:0002002 | IGI with FLYBASE:symbol-35; FB:FBgn0000035 any bull here
    3) mRNA binding ; GO:0001001 | IDA
    4) UniProtKB:colocalizes_with mRNA binding ; GO:0001001 | IDA
    5) NOT involved_in triglyceride homeostasis ; GO:0070328 | IMP
    6) colocalizes_with nucleolus ; GO:0002001 | IDA


    Lots of stuff to check here
    1) qualifier without  ':' in it (i.e. located_in)
    2) qualifier with ':' in it  (i.e. HGNC:contributes_to)
    3) name matches go identifier.
    4) valid code abbreviation.
    5) if FLYBASE:xxxxxx, xxxxxx must be a valid feature symbol.
    6) if FB:xxxxxx, xxxxxx must be a valid feature uniquename.
    7) ? (with|?) ......... must be there for some codes.
    8) check for NOT
    """
    go_dict = {'gocvterm': None,
               'error': [],
               'value': None,
               'provenance': 'FlyBase',
               'prov_term': None,
               'is_not': False}

    # 1) qualifier without  ':' in it (i.e. located_in)
    # it is hard to have a regex to maybe get quali without a ':' so do this first.
    line = quali_checks(session, line, go_dict, allowed_qualifiers, quali_cvs)

    full_pattern = r"""
                ^           # start of line
                \s*         # possible leading spaces
                (NOT)*      # possible NOT
                \s*         # possible spaces
                (\S*:\S*)*  # possible UniProtKB:quali
                \s*         # possible spaces
                (.+)        # anything including spaces
                \s*         # possible spaces
                ;           # semi colon
                \s*         # possible spaces
                GO:         # GO: prefix
                (\d{7})     # accession 7 digit number i.e. 0000011
                \s*         # possible spaces
                \|          # separator
                \s*         # possible spaces
                (\S{2,3})   # 2 or 3 letter abbreviation code
                \s*         # possible spaces
                (.*)        # evidence comment possibly with checks
            """
    # USE dict as full_pattern could change often
    # so try to make code easier with indexs that can be changed easily and not missed
    fpi = {
        'is_not': 1,
        'quali': 2,
        'go_name': 3,
        'go_code': 4,
        'evi_code': 5,
        'comment':  6}

    fields = re.search(full_pattern, line, re.VERBOSE)
    if not fields:
        go_dict['error'].append("Failed to match format xxxxxx ; GO:ddddddd | XX[X]")
        return go_dict

    if fields.group(fpi['is_not']):
        go_dict['is_not'] = True

    # 2) if quali check that it is DB:quali
    if fields.group(fpi['quali']):
        update_quali(session, go_dict, fields, fpi, allowed_qualifiers, quali_cvs)

    # get cvterm using the cvterm name
    cvterm_name = fields.group(fpi['go_name']).strip()
    go_dict['gocvterm'] = cvterm = get_cvterm(session, cv_name, cvterm_name)
    # check the cvterm dbxref to make sure the gocode matches the accession
    gocode = str(fields.group(fpi['go_code'])).strip()
    if gocode != cvterm.dbxref.accession:
        go_dict['error'].append("{} matches {} but lookup gives {} instead?".format(cvterm_name, gocode, cvterm.dbxref.accession))

    abbr = fields.group(fpi['evi_code']).strip()
    try:
        start_comment = code_to_string[abbr]
    except KeyError:
        go_dict['error'].append("{} Not one of the list valid codes {}.".format(abbr, code_to_string.keys()))
        start_comment = 'Not valid code'

    end_comment = fields.group(fpi['comment'])
    go_dict['value'] = start_comment
    if end_comment:
        go_dict['value'] += ' ' + end_comment.strip()
    if not end_comment:  # can be an empty string some times no additional comments are given
        return go_dict

    problem = check_for_valid_fbs(session, end_comment)
    if problem:
        go_dict['error'].append(problem)
    return go_dict


def quali_checks(session, line, go_dict, allowed_qualifiers, quali_cvs):
    """Process qualifiers at the start."""
    # NOTE: We do not know the order in which the qualifiers are coming in so as we
    #       are testing for the cvterm at the start of the string we may have to
    #       repeat this step.
    # NOTE: Cannot use it in any part as we may have things like HGNCL:contributes_to in
    #       there so we need to make sure the cvterm is at the start of the string.
    found = []
    one_found = True
    while (one_found):
        one_found = False
        for quali in allowed_qualifiers:
            if line.startswith(quali):
                q_cv_name = 'FlyBase miscellaneous CV'
                if quali in quali_cvs:
                    q_cv_name = quali_cvs[quali]
                found.append(quali)
                one_found = True
                go_dict['prov_term'] = get_cvterm(session, q_cv_name, quali)
                line = line.replace(quali, '')
                line = line.lstrip()
    if len(found) > 1:
        go_dict['error'].append("Only 1 qualifier allowed. you specified many ({})".format(found))
    return line


def check_for_valid_fbs(session, end_comment):
    """Check for valid features if they are in the string."""
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


def update_quali(session, go_dict, fields, fpi, allowed_qualifiers, alt_cvs=None):
    """Update the go_dict with any qualifiers found."""
    dbname, term = fields.group(fpi['quali']).strip().split(':')
    log.debug("GOTERM: '{}' '{}'".format(dbname, term))
    # check term is allowed
    if term not in allowed_qualifiers:
        go_dict['error'].append("{} Not one of the allowed values {}". format(term, allowed_qualifiers))
    else:
        cv_name = 'FlyBase miscellaneous CV'
        if alt_cvs and term in alt_cvs:
            cv_name = alt_cvs[term]
        if go_dict['prov_term']:
            go_dict['error'].append("Already have a qualifier {} so cannot add another {}".format(go_dict['prov_term'], term))
        go_dict['prov_term'] = get_cvterm(session, cv_name, term)
    # check DB is valid
    db, new = get_or_create(session, Db, name=dbname)
    if new:
        go_dict['error'].append("{} Not a valid database".format(db))
    go_dict['provenance'] = dbname
    return go_dict
