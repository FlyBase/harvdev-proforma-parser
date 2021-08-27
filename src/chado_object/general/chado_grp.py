"""
:synopsis: The "Grp" ChadoObject.

:overview: Code to setup and process GENEGROUP PROFORMA.

:moduleauthor: Ian Longden <ianlongden@morgan.harvard.edu>
"""

import logging
import os

from harvdev_utils.chado_functions import get_or_create
from harvdev_utils.production.production import GrpRelationship, GrpRelationshipPub
from chado_object.general.chado_general import ChadoGeneralObject
from harvdev_utils.production import (
    Grp, GrpCvterm, GrpDbxref, GrpPub, Grpprop, GrppropPub, GrpSynonym
)

log = logging.getLogger(__name__)


class ChadoGrp(ChadoGeneralObject):
    """Process the GeneGroup Proforma."""

    def __init__(self, params):
        """Initialise the chado object."""
        log.debug('Initializing ChadoGrp object.')

        # Initiate the parent.
        super(ChadoGrp, self).__init__(params)

        self.proforma_start_line_number = params.get('proforma_start_line_number')
        self.set_values = params.get('set_values')
        self.new = False
        self.pub = None
        self.chado = None
        # Add the chado object types needed
        self.alchemy_object = {"general": Grp,
                               "synonym": GrpSynonym,
                               "pub": GrpPub,
                               "prop": Grpprop,
                               "proppub": GrppropPub,
                               "cvterm": GrpCvterm,
                               "dbxref": GrpDbxref,
                               "relationship": GrpRelationship,
                               "relationshippub": GrpRelationshipPub}

        self.dissociate_list = ['synonym', 'cvterm', 'pub']
        # add the chado table name
        self.table_name = 'grp'
        self.fb_code = 'gg'
        self.creation_keys = {
            'symbol': 'GG1a',
            'merge': None,
            'dissociate': 'GG3b',
            'id': 'GG1h',
            'is_current': 'GG1g',
            'rename': 'GG1e',
            'type': 'GG1a',  # where type_cv and type_cvterm are defined
            'org': None
        }
        ############################################################
        # Get processing info and data to be processed.
        # Please see the yml/chemical.yml file for more details
        ############################################################
        yml_file = os.path.join(os.path.dirname(__file__), '../yml/grp.yml')
        # Populated self.process_data with all possible keys.
        self.process_data = self.load_reference_yaml(yml_file, params)

    def load_content(self, references):
        """Process the data.

        Args:
            references: <dict> previous reference proforma objects
        return:
            <Feature object> Allele feature object.
        """
        try:
            self.pub = references['ChadoPub']
        except KeyError:
            message = "Unable to find publication."
            self.critical_error(self.process_data['GG1a']['data'], message)
            return None

        ##########################################
        # Set up how to process each type of input
        ##########################################
        self.type_dict = {'synonym': self.load_synonym,
                          'ignore': self.load_ignore,
                          'prop': self.load_generalprop,
                          'cvterm': self.load_cvterm,
                          'dbxref': self.load_dbxref,
                          'relationship': self.load_relationship,
                          'obsolete': self.make_obsolete,
                          'dis_pub': self.dis_pub}

        self.delete_dict = {'synonym': self.delete_synonym,
                            'prop': self.delete_prop,
                            'cvterm': self.delete_cvterm,
                            'relationship': self.delete_relationship}

        self.chado = self.initialise_object()
        if not self.chado:
            return

        # add pub if not dissociate from pub
        if not self.creation_keys['dissociate'] or not self.has_data(self.creation_keys['dissociate']):
            get_or_create(self.session, self.alchemy_object['pub'], grp_id=self.chado.grp_id, pub_id=self.pub.pub_id)
        # bang c first as this supersedes all things
        if self.bang_c:
            self.bang_c_it()
        if self.bang_d:
            self.bang_d_it()

        for key in self.process_data:
            log.debug("Processing {}".format(self.process_data[key]['data']))
            if 'type' not in self.process_data[key]:
                self.critical_error(self.process_data[key]['data'],
                                    "No sub to deal type '{}' yet!! Report to HarvDev".format(key))
            self.type_dict[self.process_data[key]['type']](key)
