"""
:synopsis: The Gene checks that cerberus is unable to do.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>, Ian Longden <ilongden@morgan.harvard.edu>
"""
import re
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from harvdev_utils.chado_functions import (
    feature_symbol_lookup, get_organism
    # , get_or_create
)
# from harvdev_utils.production import Dbxref
from chado_object.utils.dbxref import get_dbxref_by_params
from chado_object.chado_base import FIELD_VALUE

import logging
log = logging.getLogger(__name__)

###########################################
# Checks, put together to help find easier.
###########################################

##############################################################
# Gxx checks.
# Try to keep these is field order to make it easier to find.
##############################################################


def g26_format_error(self, key):
    """Report format error."""
    message = "Does not match format Foreign sequence; species == <Genus species>; gene == <gene symbol>; <optional accession number>."
    self.critical_error(self.process_data[key]['data'], message)


def g26_species_check(self, key, species_bit):
    """Check the species data."""
    organism = None
    species = species_bit.strip().split()
    if len(species) < 4:
        self.g26_format_error(key)
        return organism

    if species[0] != 'species' or species[1] != '==':
        # look up species
        organism = get_organism(self.session, species[2], species[3])
        if organism.organism_id != self.feature.organism_id:  # Should be the same organism.
            message = "Organisms differ {}={} != {}={}".\
                format(organism.genus, organism.species,
                       self.feature.organism.genus, self.feature.organism.species)
            self.critical_error(self.process_data[key]['data'], message)
    return organism


def g26_gene_symbol_check(self, key, gene_bit):
    """Check the gene data."""
    pattern = r"""
        gene        # key word
        \s*         # possible spaces
        ==          # separator
        \s*         # possible spaces
        [']*        # possible '
        (\w+)       # gene symbol
        [']*        # possible '
        (.*)        # possible other stuff, if so
        $           # end of line
    """
    fields = re.search(pattern, gene_bit, re.VERBOSE)
    if not fields:
        self.g26_format_error(key)
        return
    gene_symbol = "{}\\{}".format(self.feature.organism.abbreviation, fields.group(1).strip())

    if fields.group(2).strip():  # not just symbol, so case like gene == 'DefA-la, Defensin-A-large'.
        message = "Not checking gene symbol as its has the wrong format"
        self.warning_error(self.process_data[key]['data'], message)
        return
    try:
        feature_symbol_lookup(self.session, 'gene', gene_symbol)
    except MultipleResultsFound:
        message = "Multiple Genes with symbol {}.".format(gene_symbol)
        self.critical_error(self.process_data[key]['data'], message)
    except NoResultFound:
        message = "Unable to find Gene with symbol {}.".format(gene_symbol)
        self.critical_error(self.process_data[key]['data'], message)


def g26_dbxref_check(self, key, db_bit, organism):
    """Dbxref get/create (optional).

    Set self.g26_dbxref.
    """
    org_to_db = {'Hsap': 'HGNC', 'Scer': 'SGD', 'Mmus': 'MGI'}
    db_pattern = r"""
        ^       # start of string
        \s*     # possible space
        (\w+)   # dbname
        :+      # separator
        \s*     # possible space
        (\w+)   # accession
        [.]*    # possible . at end
    """

    db_data = re.search(db_pattern, db_bit, re.VERBOSE)
    if not db_data:
        message = "Incorrect format for db:acc"
        self.critical_error(self.process_data[key]['data'], message)

    params = {'dbname': db_data[1].strip(), 'accession': db_data[2].strip()}

    self.g26_dbxref, _ = get_dbxref_by_params(self.session, params=params)

    #################################################
    # if G35 is set then check that wrt dbxref above.
    #################################################
    if self.has_data('G35'):
        db_data_check = re.search(db_pattern, self.process_data['G35']['data'][FIELD_VALUE].strip(), re.VERBOSE)
        if not db_data_check:
            message = "Wrong format should be dbname:accession"
            self.critical_error(self.process_data['G35']['data'], message)
        else:
            if (db_data_check[1].strip() != db_data[1].strip() or db_data_check[2].strip() != db_data[2].strip()):
                message = "G26 and G35 DB:Accession do not match. {}:{} != {}:{}".\
                    format(db_data[1].strip(), db_data[1].strip(),
                           db_data_check[2].strip(), db_data_check[2].strip())
                self.critical_error(self.process_data['G35']['data'], message)

    if organism and organism.abbreviation in org_to_db:
        if org_to_db[organism.abbreviation] != params['dbname']:
            message = "Organism {} can only have dnxref to {} NOT {} as stated".\
                format(organism.abbreviation, org_to_db[organism.abbreviation], params['dbname'])
    elif organism:
        if db_data[0].strip() not in self.process_data[key]['allowed_dbs']:
            message = "Only one of {} can be used for species not in {}".\
                format(self.process_data[key]['allowed_dbs'], org_to_db.keys())


def g26_check(self, key):
    """G26 checks.

    # check for correct format
    Foreign sequence; species == <Genus species>; gene == <gene symbol>; <accession number>.
    Examples:
    Foreign sequence; species == Homo sapiens; gene == ABL1; HGNC:76.
    Foreign sequence; species == Mus musculus; gene == Cry1; MGI:MGI:1270841.
    Foreign sequence; species == Bombyx mori; gene == 'Cyp306a1'; UniProt/TrEMBL:Q6I6X0.
    Foreign sequence; species == Aedes aegypti; gene == 'DefA-la, Defensin-A-large'.


    If you fill in G26, you need to fill in G30 (see new_foreign_gene.notes).

    If you fill in G26, for a foreign gene you need to fill in G35. The value in the G26 <accession number> must match the contents of G35.

    will generate critical errors for checks that fail.

    Set self.g26_dbxref if appropriate.
    """
    parts = self.process_data[key]['data'][FIELD_VALUE].split(';')
    # i.e.  ['Foreign sequence', ' species == Bombyx mori', " gene == 'Cyp306a1'", ' UniProt/TrEMBL:Q6I6X0.']

    if parts[0].strip() != 'Foreign sequence':
        self.g26_format_error(key)
        return

    if len(parts) < 3:
        self.g26_format_error(key)
        return

    organism = self.g26_species_check(key, parts[1])

    self.g26_gene_symbol_check(key, parts[2])

    if len(parts) == 4:
        self.g26_dbxref_check(key, parts[3], organism)
    else:
        if self.has_data('G35'):
            message = "Cannot set G35 without {} db:acc at end for now".format(key)
            self.critical_error(self.process_data[key]['data'], message)


def g28a_check(self, key):
    """G28a checks.

    1) check that entries flanked by @@ are valid symbols of any FBid type
       (either existing already in chado or instantiated in the curation record).

    2)  sub 'check_stamped_free_text' also checks that the line does not
        *start with* either of the following (to catch cases where SoftCV field
        data has been put into a neighbouring free text field by mistake):

       'Source for identity of: '
       'Source for merge of: '
    """
    if not self.has_data(key):
        return
    # 1)
    self.check_at_symbols_exist(key)
    # 2)
    self.check_bad_starts(key, ['Source for identity of: ', 'Source for merge of: '])


def g28b_check(self, key):
    """G28b checks.

    1) If you are using G1e to rename a gene symbol, you must fill in G28b.
        using the 'Source for identity of:' SoftCV.
    2) If you are using G1f to merge two (or more) gene reports,
        then you must fill in G28b. using the 'Source for merge of:' SoftCV.
    """
    if self.has_data('G1e'):
        line_segment = 'Source for identity of:'
        sup_key = 'G1e'
    elif self.has_data('G1f'):
        line_segment = 'Source for merge of:'
        sup_key = 'G1f'
    else:
        return
    if line_segment not in self.process_data[key]['data'][FIELD_VALUE]:
        message = "{} not found (required from {}) in {}".\
            format(line_segment, sup_key, self.process_data[key]['data'][FIELD_VALUE])
        self.critical_error(self.process_data[key]['data'], message)


def g31a_check(self, key):
    """G31a checks.

    If G31a contains the value y,
    G1g must also be y and G1a must contain a symbol
    which is the valid symbol of a gene which is already in FlyBase.
    All other fields in this proforma, including the non-renaming fields,
    must be blank.
    """
    self.check_only_certain_fields_allowed('G31a', ['G1a', 'G1g', 'G31a'])


def g31b_check(self, key):
    """G31b checks.

    If G31b contains the value y, G1g must also be y and
    G1a must contain a symbol which is the valid symbol
    of a gene which is already in FlyBase.
    All other fields in this proforma, including the non-renaming fields,
    must be blank.
    """
    self.check_only_certain_fields_allowed('G31b', ['G1a', 'G1g', 'G31b'])


def g35_check(self, key):
    """G35 checks.

    Fill in using the <database>:<accession number> format, i.e., exactly the same as the last component of the
    G26 field (without a full-stop).

    This field requires the value in to be the name of a valid database in the 'db' table in chado, which is not
    necessarily the same as what is in the GO.xrf_abbs file.
    This all needs reconciling, and the db table itself needs tidying, and we need to get a report in
    curation_data that gives us a list of these values, but in the meantime, the following are allowed
    as a database prefix in this field:

    'HGNC' for Hsap genes
    'SGD' for Scer genes
    'MGI' for Mmus genes
    NOTE, the id for an MGI gene starts with the string 'MGI:', so even though it looks odd, the correct format
    for Mus musculus genes is 'MGI:MGI:1270841' NOT 'MGI:1270841'. Any other model organism database abbreivations
    will currently cause Peeves to complain, even if they are in the GO.xrf_abbs file, so if you are making a
    foreign gene that has a model organism database id, but it is not one of the species in the above list,
    fill in G26 as normal using the model organism database id and leave G35 blank (do not be tempted to use a
    sequence accession number such as 'GB' instead).
    Peeves will complain (sorry!), but this avoids the risk of trying to add an id for a database that is
    not yet in chado.

    (NOTE Once we have this reconciled, the accession number can be retrofitted into the G35 slot using the
    information in G26, so no information is lost by leaving G35 blank in this case).

    Only use an accession for a sequence database for those species where there is no model organism id number
    to use. The allowed values are as follows (NOTE, Peeves will currently complain about this, giving a
    'Missing or unrecognized database abbreviation' error message - but for the databases below you can ignore it)

    'GB' for a GenBank nucleotide sequence
    'GB_protein' for a GenBank protein sequence (NB: try to use a UniProt sequence instead of using this)
    'UniProt/Swiss-Prot' for a UniProt Swiss-Prot sequence
    'UniProt/TrEMBL' for a UniProt TrEMBL sequence
    """
    message = "G35 checking not done yet"
    self.critical_error(self.process_data[key]['data'], message)


def g39a_check(self, key):
    """G39a checks.

    1) check that entries flanked by @@ are valid symbols of any FBid type
       (either existing already in chado or instantiated in the curation record).

    2) If G39a is filled in, G39b must be 'y', and G39c and G39d should be filled in.
    """
    # 1)
    self.check_at_symbols_exist(key)
    # 2) G39c and G39d checks done by validation
    if self.has_data('G39b') and self.process_data['G39b']['data'][FIELD_VALUE] != 'y':
        message = "G39a is set so 'G39b' should be set to 'y' and not {}".format(self.process_data['G39b']['data'][FIELD_VALUE])
        self.critical_error(self.process_data['G39b']['data'], message)
