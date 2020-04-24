"""
:synopsis: The Gene ChadoObject.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>, Ian Longden <ilongden@morgan.harvard.edu>
"""
import os
import re
from chado_object.chado_base import (
    FIELD_VALUE, FIELD_NAME, LINE_NUMBER
)
from chado_object.feature.chado_feature import ChadoFeatureObject
from harvdev_utils.production import (
    Feature, FeaturePub
)
from harvdev_utils.chado_functions import (
    get_or_create, get_cvterm, DataError,
    feature_symbol_lookup, get_dbxref,
    get_feature_and_check_uname_symbol,
    synonym_name_details
)
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from datetime import datetime

import logging
log = logging.getLogger(__name__)


class ChadoGene(ChadoFeatureObject):
    """ChadoGene object."""

    from chado_object.gene.gene_merge import (
        merge, get_merge_genes, transfer_dbxrefs, transfer_synonyms, transfer_grpmembers,
        transfer_hh_dbxrefs, transfer_cvterms
    )

    def __init__(self, params):
        """Initialise the ChadoGene Object."""
        log.debug('Initializing ChadoGene object.')

        # Initiate the parent.
        super(ChadoGene, self).__init__(params)
        ##########################################
        # Set up how to process each type of input
        ##########################################
        self.type_dict = {'synonym': self.load_synonym,
                          'ignore': self.ignore,
                          'cvtermprop': self.load_cvtermprop,
                          'merge': self.merge,
                          'dis_pub': self.ignore,
                          'make_obsolete': self.make_obsolete,
                          'featureprop': self.load_featureprop}

        self.delete_dict = {'synonym': self.delete_synonym,
                            'cvterm': self.delete_cvterm}

        self.proforma_start_line_number = params.get('proforma_start_line_number')

        ###########################################################
        # Values queried later, placed here for reference purposes.
        ############################################################
        self.pub = None
        self.type_name = 'gene'

        ############################################################
        # Get processing info and data to be processed.
        # Please see the yml/publication.yml file for more details
        ############################################################
        yml_file = os.path.join(os.path.dirname(__file__), '../yml/gene.yml')
        # Populated self.process_data with all possible keys.
        self.process_data = self.load_reference_yaml(yml_file, params)

    def load_content(self, references):
        """Process the data."""
        try:
            self.pub = references['ChadoPub']
        except KeyError:
            message = "Unable to find publication."
            self.critical_error(self.process_data['G1a']['data'], message)
            return None

        self.get_gene()
        if not self.feature:  # problem getting gene, lets finish
            return None
        self.extra_checks()
        # feature pub
        get_or_create(self.session, FeaturePub, feature_id=self.feature.feature_id, pub_id=self.pub.pub_id)
        # bang c first as this supersedes all things
        if self.bang_c:
            self.bang_c_it()
        if self.bang_d:
            self.bang_d_it()

        for key in self.process_data:
            log.debug("Processing {}".format(self.process_data[key]['data']))
            self.type_dict[self.process_data[key]['type']](key)

        timestamp = datetime.now().strftime('%c')
        curated_by_string = 'Curator: %s;Proforma: %s;timelastmodified: %s' % (self.curator_fullname, self.filename_short, timestamp)
        log.debug('Curator string assembled as:')
        log.debug('%s' % (curated_by_string))
        return self.feature

    def check_only_certain_fields_allowed(self, key, allowed):
        """Check only allowed fields exist."""
        bad_fields = []
        for valid_key in self.process_data:
            if valid_key not in allowed:
                bad_fields.append(valid_key)
            log.info("BOB: {} {}".format(valid_key, self.process_data[valid_key]))
        if bad_fields:
            message = "{} prohibits use of {}".format(key, bad_fields)
            self.critical_error(self.process_data[key]['data'], message)

    def extra_checks(self):
        """Extra checks.

        Ones that ar not easy to do via the validator.
        """
        if self.has_data('G31a'):
            # If G31a contains the value y,
            # G1g must also be y and G1a must contain a symbol
            # which is the valid symbol of a gene which is already in FlyBase.
            # All other fields in this proforma, including the non-renaming fields,
            # must be blank.
            self.check_only_certain_fields_allowed('G31a', ['G1a', 'G1g', 'G31a'])
        if self.has_data('G31b'):
            # If G31b contains the value y, G1g must also be y and 
            # G1a must contain a symbol which is the valid symbol 
            # of a gene which is already in FlyBase.
            # All other fields in this proforma, including the non-renaming fields,
            # must be blank.
            self.check_only_certain_fields_allowed('G31b', ['G1a', 'G1g', 'G31b'])

    def ignore(self, key):
        """Ignore, done by initial setup."""
        pass

    def make_obsolete(self, key):
        """Make gene obsolete."""
        self.feature.is_obsolete = True

    def load_cvtermprop(self, key):
        """Ignore, done by initial setup."""
        if key == 'G30':
            # check x ; y first got GA
            # y :- SO:{7d}
            # NOTE still needs to be done
            g30_pattern = r"""
                ^           # start of line
                \s*         # possible leading spaces
                (\S+)       # anything excluding spaces
                \s*         # possible spaces
                ;           # separator
                \s*         # possible spaces
                SO:         # dbxref DB must start be SO:
                (\d{7})  # accession 7 digit number i.e. 0000011
            """
            fields = re.search(g30_pattern, self.process_data[key]['data'][FIELD_VALUE], re.VERBOSE)
            if not fields:
                message = 'Wrong format should be "none_spaces_name ; SO:[0-9]*7"'
                self.critical_error(self.process_data[key]['data'], message)
                return

            cvterm_name = fields.group(1).strip()
            db_name = 'SO'
            db_acc = fields.group(2)
            cv_name = self.process_data[key]['cv']

            cvterm = get_cvterm(self.session, cv_name, cvterm_name)
            try:
                db_xref = get_dbxref(self.session, db_name, db_acc)
            except DataError:
                message = "Could not find dbxref for db '{}' and accession '{}'".format(db_name, db_acc)
                self.critical_error(self.process_data[key]['data'], message)
                return None

            if cvterm.dbxref.dbxref_id != db_xref.dbxref_id:
                message = "'{}' Does not match '{}', lookup gave '{}'".\
                    format(cvterm_name, cvterm.dbxref.accession, db_xref.accession)
                self.critical_error(self.process_data[key]['data'], message)
                return None

            new_tuple = (self.process_data[key]['data'][FIELD_NAME],
                         cvterm_name,
                         self.process_data[key]['data'][LINE_NUMBER])
            self.process_data[key]['data'] = new_tuple

        # then process
        self.load_feature_cvtermprop(key)

    def get_gene(self):
        """Get initial gene and check."""
        if self.has_data('G1f'):  # if gene merge we want to create a new gene even if one exist already
            cvterm = get_cvterm(self.session, 'SO', 'gene')
            if not cvterm:
                message = "Unable to find cvterm 'gene' for Cv 'SO'."
                self.critical_error(self.process_data['G1a']['data'], message)
                return None
            organism, plain_name, sgml = synonym_name_details(self.session, self.process_data['G1a']['data'][FIELD_VALUE])
            self.feature, _ = get_or_create(self.session, Feature, name=plain_name,
                                            type_id=cvterm.cvterm_id, uniquename='FBgn:temp_0', organism_id=organism.organism_id)
            return

        if self.has_data('G1h'):
            self.feature = None
            try:
                self.feature = get_feature_and_check_uname_symbol(self.session,
                                                                  self.process_data['G1h']['data'][FIELD_VALUE],
                                                                  self.process_data['G1a']['data'][FIELD_VALUE],
                                                                  type_name='gene')
            except DataError as e:
                self.critical_error(self.process_data['G1h']['data'], e.error)

            return self.feature
        if self.process_data['G1g']['data'][FIELD_VALUE] == 'y':  # Should exist already
            #  organism, plain_name, sgml = synonym_name_details(self.session, self.process_data['G1a']['data'][FIELD_VALUE])
            try:
                self.feature = feature_symbol_lookup(self.session, 'gene', self.process_data['G1a']['data'][FIELD_VALUE])
            except MultipleResultsFound:
                message = "Multiple Genes with symbol {}.".format(self.process_data['G1a']['data'][FIELD_VALUE])
                log.info(message)
                self.critical_error(self.process_data['G1a']['data'], message)
                return
            except NoResultFound:
                message = "Unable to find Gene with symbol {}.".format(self.process_data['G1a']['data'][FIELD_VALUE])
                self.critical_error(self.process_data['G1a']['data'], message)
                return
        else:
            cvterm = get_cvterm(self.session, 'SO', 'gene')
            if not cvterm:
                message = "Unable to find cvterm 'gene' for Cv 'SO'."
                self.critical_error(self.process_data['G1a']['data'], message)
                return None
            organism, plain_name, sgml = synonym_name_details(self.session, self.process_data['G1a']['data'][FIELD_VALUE])
            self.feature, _ = get_or_create(self.session, Feature, name=plain_name,
                                            type_id=cvterm.cvterm_id, uniquename='FBgn:temp_0',
                                            organism_id=organism.organism_id)
            # add default symbol
            self.load_synonym('G1a')

    def delete_synonym(self, key):
        """Ignore, done by initial setup."""
        pass

    def delete_cvterm(self, key):
        """Ignore, done by initial setup."""
        pass
