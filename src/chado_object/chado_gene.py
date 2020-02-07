"""
.. module:: chado_gene
   :synopsis: The "gene" ChadoObject.

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
import os
from .chado_base import ChadoObject, FIELD_VALUE
from harvdev_utils.production import (
    Feature
)
from harvdev_utils.chado_functions import get_or_create, get_cvterm
from .utils.feature_synonym import fs_add_by_synonym_name_and_type
from .utils.feature import feature_symbol_lookup, feature_name_lookup
from .utils.organism import get_default_organism, get_organism
from harvdev_utils.char_conversions import (
    sgml_to_plain_text, sub_sup_to_sgml, sgml_to_unicode
)
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

    def load_content(self):
        """
        Main processing routine
        """
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
            synonym_name = item[FIELD_VALUE]
            # synonym_name = synonym_name.replace('\\', '\\\\')
            fs_add_by_synonym_name_and_type(self.session, self.gene.feature_id,
                                            synonym_name, cv_name, cvterm_name, self.pub.pub_id,
                                            synonym_sgml=None, is_current=is_current, is_internal=False)

    def load_cvterm(self, key):
        pass

    def synonym_check(self, synonym_name):
        """
        Process the synonym_name given and check for organism specific stuff

        if synonym has '\' in it the split and use first bit as the species abbreviation
        Also check for species starting with T: as this is some special shit.

        returns:
        organism for the entry
        plain-text version of name
        unicode version of text woth sup to sgml


        So for synonym_name of 'Hsap\0005-&agr;-[001]

        organism returned is the Organism object for homo sapiens
        plain text -> 'Hsap\\00005-alpha-[001]'
        unicode version -> 'Hsap\\00005-α-<up>001</up>'
        """
        s_res = synonym_name.split('\\')
        if len(s_res) > 1:  # we have a '\' in the synonym
            t_bit = ''
            abbr = s_res[0]
            if s_res[0].startswith('T:'):
                t_bit = 'T:'
                abbr = s_res[0][2:]
            organism = get_organism(self.session, short=abbr)
            name = "{}{}\\{}".format(t_bit, abbr, s_res[1])
            return organism, sgml_to_plain_text(name), sgml_to_unicode(sub_sup_to_sgml(name))
        else:
            return get_default_organism(self.session), sgml_to_plain_text(synonym_name), sgml_to_unicode(sub_sup_to_sgml(synonym_name))

    def get_gene(self):
        # G1h is used to check it matches with G1a
        if self.has_data('G1h'):
            self.gene = self.session.query(Feature).filter(Feature.uniquename == self.process_data['G1h']['data'][FIELD_VALUE],
                                                           Feature.is_obsolete == 'f').one()
            if not self.gene:
                message = "Unable to find Gene with uniquename {}.".format(self.process_data['G1h']['data'][FIELD_VALUE])
                self.critical_error(self.process_data['G1h']['data'], message)
                return None
            # Test the synonym used in Gla matches this.
            organism, plain_name, sgml_name = self.synonym_check(self.process_data['G1a']['data'][FIELD_VALUE])
            feat_check = feature_name_lookup(self.session, 'gene', plain_name, organism_id=organism.organism_id)
            if not feat_check:
                message = "Unable to lookup '{}' using '{}' in chado db.".format(self.process_data['G1a']['data'][FIELD_VALUE], plain_name)
                self.critical_error(self.process_data['G1a']['data'], message)
                return None
            if feat_check.feature_id != self.gene.feature_id:
                message = "Symbol {} does not match that for {}.".format(self.process_data['G1a']['data'][FIELD_VALUE],
                                                                         self.process_data['G1h']['data'][FIELD_VALUE])

                self.critical_error(self.process_data['G1a']['data'], message)
                return None
            return self.gene

        if self.process_data['G1g']['data'][FIELD_VALUE] == 'y':  # Should exist already
            organism, plain_name, sgml = self.synonym_check(self.process_data['G1a']['data'][FIELD_VALUE])
            self.gene = feature_symbol_lookup(self.session, 'gene', self.process_data['G1a']['data'][FIELD_VALUE], organism_id=organism.organism_id)
            if not self.gene:
                message = "Unable to find Gene with symbol {}.".format(self.process_data['G1a']['data'][FIELD_VALUE])
                self.critical_error(self.process_data['G1a']['data'], message)
        else:
            cvterm = get_cvterm(self.session, 'SO', 'gene')
            if not cvterm:
                message = "Unable to find cvterm 'gene' for Cv 'SO'."
                self.critical_error(self.process_data['G1a']['data'], message)
                return None
            organism, plain_name, sgml = self.synonym_check(self.process_data['G1a']['data'][FIELD_VALUE])
            self.gene, _ = get_or_create(self.session, Feature, name=plain_name,
                                         type_id=cvterm.cvterm_id, uniquename='FBgn:temp_0', organism_id=organism.organism_id)
            # add default symbol
            self.load_synonym('G1a')

    def delete_synonym(self, key):
        pass

    def delete_cvterm(self, key):
        pass
