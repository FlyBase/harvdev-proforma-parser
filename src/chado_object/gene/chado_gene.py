"""
:synopsis: The Gene ChadoObject.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>, Ian Longden <ilongden@morgan.harvard.edu>
"""
import os
from chado_object.chado_base import ChadoObject, FIELD_VALUE
from harvdev_utils.production import (
    Feature, Featureprop, Pub, FeaturePub
)
from harvdev_utils.chado_functions import get_or_create, get_cvterm, DataError
from chado_object.utils.feature_synonym import fs_add_by_synonym_name_and_type
from chado_object.utils.feature import (
    feature_symbol_lookup,
    get_feature_and_check_uname_symbol
)
from chado_object.utils.synonym import synonym_name_details
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime

import logging
log = logging.getLogger(__name__)


class ChadoGene(ChadoObject):
    """ChadoGene object."""

    from chado_object.gene.gene_merge import (
        merge, get_merge_genes, transfer_dbxrefs, transfer_synonyms
    )

    def __init__(self, params):
        """Initialise the ChadoGene Object."""
        log.info('Initializing ChadoGene object.')

        # Initiate the parent.
        super(ChadoGene, self).__init__(params)
        ##########################################
        # Set up how to process each type of input
        ##########################################
        self.type_dict = {'synonym': self.load_synonym,
                          'ignore': self.ignore,
                          'cvterm': self.load_cvterm,
                          'merge': self.merge,
                          'prop': self.load_prop}

        self.delete_dict = {'synonym': self.delete_synonym,
                            'cvterm': self.delete_cvterm}

        self.proforma_start_line_number = params.get('proforma_start_line_number')

        ###########################################################
        # Values queried later, placed here for reference purposes.
        ############################################################
        self.pub = None
        self.gene = None

        ############################################################
        # Get processing info and data to be processed.
        # Please see the yml/publication.yml file for more details
        ############################################################
        yml_file = os.path.join(os.path.dirname(__file__), '../yml/gene.yml')
        # Populated self.process_data with all possible keys.
        self.process_data = self.load_reference_yaml(yml_file, params)
        self.reference = params.get('reference')
        self.genus = "Drosophila"
        self.species = "melanogaster"

    def load_content(self):
        """Process the data."""
        self.pub = super(ChadoGene, self).pub_from_fbrf(self.reference)

        self.get_gene()
        if not self.gene:  # problem getting gene, lets finish
            return
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
        log.info('Curator string assembled as:')
        log.info('%s' % (curated_by_string))

    def load_prop(self, key):
        """Load featureprop."""
        if not self.has_data(key):
            return
        cv_name = self.process_data[key]['cv']
        cvterm_name = self.process_data[key]['cvterm']
        cvterm = get_cvterm(self.session, cv_name, cvterm_name)
        if not cvterm:
            message = "Unable to find cvterm {} for Cv {}.".format(cvterm_name, cv_name)
            self.critical_error(self.process_data[key]['data'], message)
            return None

        prop, _ = get_or_create(self.session, Featureprop, value=self.process_data[key]['data'][FIELD_VALUE],
                                type_id=cvterm.cvterm_id, feature_id=self.gene.feature_id)
        if not prop:
            message = "Unable to create Featue prop??? Sorry wierd one!!"
            self.critical_error(self.process_data[key]['data'], message)

    def ignore(self, key):
        """Ignore, done by initial setup."""
        pass

    def load_synonym(self, key):
        """Load synonym."""
        if not self.has_data(key):
            return

        # some are lists so might as well make life easier and make them all lists
        if type(self.process_data[key]['data']) is not list:
            self.process_data[key]['data'] = [self.process_data[key]['data']]
        cv_name = self.process_data[key]['cv']
        cvterm_name = self.process_data[key]['cvterm']
        is_current = self.process_data[key]['is_current']

        # For some bizzare reason if a merge is taking place then the synonyms
        # have the pud unattributed and not the self.pub???
        if self.has_data('G1f'):
            pub, _ = get_or_create(self.session, Pub, uniquename='unattributed')
        else:
            pub = self.pub

        for item in self.process_data[key]['data']:
            synonym_name = item[FIELD_VALUE]
            # synonym_name = synonym_name.replace('\\', '\\\\')
            fs_add_by_synonym_name_and_type(self.session, self.gene.feature_id,
                                            synonym_name, cv_name, cvterm_name, pub.pub_id,
                                            synonym_sgml=None, is_current=is_current, is_internal=False)

    def load_cvterm(self, key):
        """Ignore, done by initial setup."""
        pass

    def get_gene(self):
        """Get initial gene and check."""
        # G1h is used to check it matches with G1a
        if self.has_data('G1h'):
            self.gene = None
            try:
                self.gene = get_feature_and_check_uname_symbol(self.session,
                                                               self.process_data['G1h']['data'][FIELD_VALUE],
                                                               self.process_data['G1a']['data'][FIELD_VALUE],
                                                               type_name='gene')
            except DataError as e:
                self.critical_error(self.process_data['G1h']['data'], e.error)

            return self.gene
        if self.process_data['G1g']['data'][FIELD_VALUE] == 'y':  # Should exist already
            organism, plain_name, sgml = synonym_name_details(self.session, self.process_data['G1a']['data'][FIELD_VALUE])
            try:
                self.gene = feature_symbol_lookup(self.session, 'gene', self.process_data['G1a']['data'][FIELD_VALUE], organism_id=organism.organism_id)
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
            self.gene, _ = get_or_create(self.session, Feature, name=plain_name,
                                         type_id=cvterm.cvterm_id, uniquename='FBgn:temp_0', organism_id=organism.organism_id)
            # feature pub
            get_or_create(self.session, FeaturePub, feature_id=self.gene.feature_id, pub_id=self.pub.pub_id)
            # add default symbol
            self.load_synonym('G1a')

    def delete_synonym(self, key):
        """Ignore, done by initial setup."""
        pass

    def delete_cvterm(self, key):
        """Ignore, done by initial setup."""
        pass
