"""GO, general routines.

.. module:: GO
   :synopsis: Lookup and general dbxref functions.

.. moduleauthor:: Ian Longden <ilongden@morgan.harvard.edu>
"""
import re
from harvdev_utils.chado_functions import (
    feature_name_lookup, get_cvterm, get_feature_by_uniquename
)
from sqlalchemy.orm.exc import NoResultFound

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


def process_GO_line(session, line, cv_name):
    """From string generate and validate GO.

    Examples:-
    1) nucleolus ; GO:0002001 | IDA
    2) something ; GO:0002002 | IGI with FLYBASE:symbol-35; FB:FBgn0000035 any bull here
    3) mRNA binding ; GO:0001001 | IDA

    should return dict with the following in it.
        {
         'gocvterm': <cvterm object>,
         'error': [], # can be many errors so check for empty array for no error)
         'value': expanded abbr + 'string'  # None if code lookup fails
        }

    Lots of stuff to check here
    1) name matches go identifier.
    2) valid code abbreviation.
    3) if FLYBASE:xxxxxx, xxxxxx must be a valid feature symbol.
    4) if FB:xxxxxx, xxxxxx must be a valid feature uniquename.
    5) ? (with|?) ......... must be there for some codes.
    """
    go_dict = {'gocvterm': None,
               'error': [],
               'value': None}

    full_pattern = r"""
                ^           # start of line
                \s*         # possible leading spaces
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
    fields = re.search(full_pattern, line, re.VERBOSE)
    if not fields:
        go_dict['error'].append("Failed to match format xxxxxx ; GO:ddddddd | XX[X]")
        return go_dict

    # get cvterm using the cvterm name
    cvterm_name = fields.group(1).strip()
    go_dict['gocvterm'] = cvterm = get_cvterm(session, cv_name, cvterm_name)

    # check the cvterm dbxref to make sure the gocode matches the accession
    gocode = str(fields.group(2)).strip()
    if gocode != cvterm.dbxref.accession:
        go_dict['error'].append("{} matches {} but lookup gives {} instead?".format(cvterm_name, gocode, cvterm.dbxref.accession))

    abbr = fields.group(3).strip()
    try:
        start_comment = code_to_string[abbr]
    except KeyError:
        go_dict['error'].append("{} Not one of the list valid codes".format(abbr))

    end_comment = fields.group(4).strip()
    go_dict['value'] = start_comment
    if end_comment:
        go_dict['value'] += ' ' + end_comment
    if not end_comment:  # can be an empty string some times no additional comments are given
        return go_dict

    problem = check_for_valid_fbs(session, end_comment)
    if problem:
        go_dict['error'].append(problem)
    return go_dict


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
