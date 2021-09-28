"""
:synopsis: The "Cell_line" ChadoObject.

:overview: Code to setup and process CULTURED CELL LINE PROFORMA.

:moduleauthor: Ian Longden <ianlongden@morgan.harvard.edu>

 public | cell_line_cvterm                                                | table    | go
 public | cell_line_cvtermprop                                            | table    | go
 public | cell_line_dbxref                                                | table    | go
 public | cell_line_feature                                               | table    | go
 public | cell_line_library                                               | table    | go
 public | cell_line_libraryprop                                           | table    | go
 public | cell_line_pub                                                   | table    | go
 public | cell_line_relationship                                          | table    | go
 public | cell_line_strain                                                | table    | go
 public | cell_line_strainprop                                            | table    | go
 public | cell_line_synonym                                               | table    | go
 public | cell_lineprop                                                   | table    | go
 public | cell_lineprop_pub                                               | table    | go

"""

import logging
import os

from harvdev_utils.chado_functions import get_or_create
from chado_object.general.chado_general import ChadoGeneralObject
from harvdev_utils.production import (
    CellLine, CellLineCvterm, CellLineCvtermprop, CellLineDbxref, CellLinePub,
    CellLineprop, CellLinepropPub, CellLineSynonym, CellLineRelationship,
    CellLineFeature, CellLineLibrary, CellLineLibraryprop
)

log = logging.getLogger(__name__)


class ChadoCellLine(ChadoGeneralObject):
    """Process the Cell line Proforma."""

    def __init__(self, params):
        """Initialise the chado object."""
        log.debug('Initializing ChadoGrp object.')

        # Initiate the parent.
        super(ChadoCellLine, self).__init__(params)

        self.proforma_start_line_number = params.get('proforma_start_line_number')
        self.set_values = params.get('set_values')
        self.new = False
        self.pub = None
        self.chado = None
        # Add the chado object types needed
        self.alchemy_object = {"general": CellLine,
                               "synonym": CellLineSynonym,
                               "pub": CellLinePub,
                               "prop": CellLineprop,
                               "proppub": CellLinepropPub,
                               "cvterm": CellLineCvterm,
                               "cvtermprop": CellLineCvtermprop,
                               "dbxref": CellLineDbxref,
                               "feature": CellLineFeature,
                               "library": CellLineLibrary,
                               "libraryprop": CellLineLibraryprop,
                               "relationship": CellLineRelationship}

        self.dissociate_list = ['synonym', 'cvterm', 'pub']

        # add the chado table name
        self.table_name = 'cell_line'
        self.fb_code = 'tc'
        self.creation_keys = {
            'symbol': 'TC1a',
            'merge': 'TC1g',
            'dissociate': 'TC1i',
            'id': 'TC1f',
            'uniquename': 'TC1f',
            'new_uniquename': 'TC1j',
            'is_new': 'TC1f',
            'rename': 'TC1e',
            'type': None,
            'org': 'TC1d',
            'delete': 'TC1h',
            'no_obsolete': True,  # wether the chado object has an obsolete field
            'add_dbxref': 'FlyBase:uniquename',  # db name ':' and what to substitute
        }

        ############################################################
        # Get processing info and data to be processed.
        # Please see the yml/chemical.yml file for more details
        ############################################################
        yml_file = os.path.join(os.path.dirname(__file__), '../yml/cell_line.yml')
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
        # if not self.checks(references):
        #    return None
        ##########################################
        # Set up how to process each type of input
        ##########################################
        self.type_dict = {'synonym': self.load_synonym,
                          'ignore': self.load_ignore,
                          'prop': self.load_generalprop,
                          'cvterm': self.load_cvterm,
                          'dbxref': self.load_dbxref,
                          'relationship': self.load_relationship,
                          'cvtermprop': self.load_cvtermprop,
                          'feature': self.load_feature,
                          'library': self.load_library,
                          'obsolete': self.make_obsolete,
                          'dis_pub': self.dis_pub}

        self.delete_dict = {'synonym': self.delete_synonym,
                            'prop': self.delete_prop,
                            'cvterm': self.delete_cvterm,
                            'relationship': self.delete_relationship,
                            'library': self.delete_library}

        self.initialise_object()

        # add pub if not dissociate from pub
        if not self.creation_keys['dissociate'] or not self.has_data(self.creation_keys['dissociate']):
            get_or_create(self.session, self.alchemy_object['pub'], cell_line_id=self.chado.cell_line_id, pub_id=self.pub.pub_id)
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
