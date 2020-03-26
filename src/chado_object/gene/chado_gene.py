"""
:synopsis: The Gene ChadoObject.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>, Ian Longden <ilongden@morgan.harvard.edu>
"""
import os
from chado_object.feature.chado_feature import ChadoFeatureObject, FIELD_VALUE
from harvdev_utils.production import (
    Feature, FeaturePub
)
from harvdev_utils.chado_functions import get_or_create, get_cvterm, DataError
from chado_object.utils.feature import (
    feature_symbol_lookup,
    get_feature_and_check_uname_symbol
)
from chado_object.utils.synonym import synonym_name_details
from sqlalchemy.orm.exc import NoResultFound
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
                          'cvterm': self.load_cvterm,
                          'merge': self.merge,
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
        # self.reference = params.get('reference')
        # self.genus = "Drosophila"
        # self.species = "melanogaster"

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

    def ignore(self, key):
        """Ignore, done by initial setup."""
        pass

    def load_cvterm(self, key):
        """Ignore, done by initial setup."""
        pass

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
            # feature pub
            get_or_create(self.session, FeaturePub, feature_id=self.feature.feature_id, pub_id=self.pub.pub_id)
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
            organism, plain_name, sgml = synonym_name_details(self.session, self.process_data['G1a']['data'][FIELD_VALUE])
            try:
                self.feature = feature_symbol_lookup(self.session, 'gene', self.process_data['G1a']['data'][FIELD_VALUE], organism_id=organism.organism_id)
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
            # feature pub
            get_or_create(self.session, FeaturePub, feature_id=self.feature.feature_id, pub_id=self.pub.pub_id)
            # add default symbol
            self.load_synonym('G1a')

    def delete_synonym(self, key):
        """Ignore, done by initial setup."""
        pass

    def delete_cvterm(self, key):
        """Ignore, done by initial setup."""
        pass
