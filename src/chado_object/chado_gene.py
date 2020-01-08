"""
.. module:: chado_gene
   :synopsis: The "gene" ChadoObject.

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
import os
from .chado_base import ChadoObject, FIELD_VALUE
from harvdev_utils.production import (
    Feature, Cv, Cvterm, Synonym, FeatureSynonym, Organism
)
from harvdev_utils.chado_functions import get_or_create
from .utils.feature_synonym import fs_add_by_synonym_name_and_type

# from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime

import logging
log = logging.getLogger(__name__)


class ChadoGene(ChadoObject):
    def __init__(self, params):
        log.info('Initializing ChadoGene object.')

        # Initiate the parent.
        super(ChadoGene, self).__init__(params)
        ##########################################
        # Set up how to process each type of input
        ##########################################
        self.type_dict = {'synonym': self.load_synonym,
                          'ignore': self.ignore,
                          'cvterm': self.load_cvterm}

        self.delete_dict = {'synonym': self.delete_synonym,
                            'cvterm': self.delete_cvterm}

        self.proforma_start_line_number = params.get('proforma_start_line_number')

        ###########################################################
        # Values queried later, placed here for reference purposes.
        ############################################################
        self.pub = None

        ############################################################
        # Get processing info and data to be processed.
        # Please see the yml/publication.yml file for more details
        ############################################################
        yml_file = os.path.join(os.path.dirname(__file__), 'yml/gene.yml')
        # Populated self.process_data with all possible keys.
        self.process_data = self.load_reference_yaml(yml_file, params)
        self.reference = params.get('reference')
        self.genus = "Drosophila"
        self.species = "melanogaster"
        # IF we need different species work out why params.get('species') is not working
        # OR remove that code form proforma_operations.py.
        log.info("species = {}, genus = {}".format(self.species, self.genus))

    def load_content(self):
        """
        Main processing routine
        """
        self.pub = super(ChadoGene, self).pub_from_fbrf(self.reference)

        self.gene = self.get_gene()
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

    def ignore(self, key):
        pass

    def load_synonym(self, key):
        if not self.has_data(key):
            return
        # some are lists so might as well make life easier and make them all lists
        if type(self.process_data[key]['data']) is not list:
            self.process_data[key]['data'] = [self.process_data[key]['data']]
        cv_name = self.process_data[key]['cv']
        cvterm_name = self.process_data[key]['cvterm']
        is_current = self.process_data[key]['is_current']
        for item in self.process_data[key]['data']:
            synonym_name =  item[FIELD_VALUE]

            fs = fs_add_by_synonym_name_and_type(self.session, self.gene.feature_id, 
                                                 synonym_name, cv_name, cvterm_name, self.pub.pub_id,
                                                 synonym_sgml=None, is_current=is_current, is_internal=False)

    def load_cvterm(self, key):
        pass

    def get_gene(self):
        # G1h is used to check it matches with G1a
        # For two reasons. 1) synonym has many genes, 2) curation sanity check
        if self.has_data('G1h'):
            gene = self.session.query(Feature).filter(Feature.uniquename == self.process_data['G1h']['data'][FIELD_VALUE],
                                                      Feature.is_obsolete == 'f').one()
            if not gene:
                message = "Unable to find Gene with uniquename {}.".format(self.process_data['G1h']['data'][FIELD_VALUE])
                self.critical_error(self.process_data['G1h']['data'], message)
                return None
            # Test the synonym used in Gla matches this.
            synonym = self.session.query(FeatureSynonym).join(Synonym).join(Cvterm).\
                filter(FeatureSynonym.feature_id == gene.feature_id,
                       Synonym.name == self.process_data['G1a']['data'][FIELD_VALUE],
                       FeatureSynonym.is_current == 't',
                       Cvterm.name == 'symbol').one()
            if not synonym:
                message = "Symbol {} does not match that for {}.".format(self.process_data['G1a']['data'][FIELD_VALUE],
                                                                         self.process_data['G1h']['data'][FIELD_VALUE])
                self.critical_error(self.process_data['G1a']['data'], message)
                return gene
            return gene

        if self.process_data['G1g']['data'][FIELD_VALUE] == 'y':  # Should exist already
            gene = self.session.query(Feature).join(FeatureSynonym).join(synonym.join(Cvterm)).\
                filter(Cvterm.name == 'symbol',
                       Synonym.name == self.process_data['G1a']['data'][FIELD_VALUE],
                       FeatureSynonym.is_current == 't',
                       Feature.is_obsolete == 'f'
                       ).one()
            if not gene:
                message = "Unable to find Gene with symbol {}.".format(self.process_data['G1a']['data'][FIELD_VALUE])
                self.critical_error(self.process_data['G1a']['data'], message)
        else:
            cvterm = self.session.query(Cvterm).join(Cv).filter(Cv.name == 'SO', Cvterm.name == 'gene').one()
            if not cvterm:
                message = "Unable to find cvterm 'gene' for Cv 'SO'."
                self.critical_error(self.process_data['G1a']['data'], message)
                return None
            log.info("looking up genus {} species {}".format(self.genus, self.species))
            organism = self.session.query(Organism).filter(Organism.genus == self.genus, Organism.species == self.species).one()
            if not organism:
                message = "Unable to find Organism with genus {} and species {}.".format(self.genus, self.species)
                self.critical_error(self.process_data['G1a']['data'], message)
                return None
            gene, _ = get_or_create(self.session, Feature, type_id=cvterm.cvterm_id, uniquename='FBgn:temp_0', organism_id=organism.organism_id)
        return gene

    def delete_synonym(self, key):
        pass

    def delete_cvterm(self, key):
        pass
