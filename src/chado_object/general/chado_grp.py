"""
:synopsis: The "Allele" ChadoObject.

:overview: Cut down version of Allele to start with to enable DIV Proforma to work.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>
               Ian Longden <ianlongden@morgan.harvard.edu>
"""

import logging
import os
import re


# from sqlalchemy.sql.functions import ReturnTypeFromArgs
from chado_object.general.chado_general import ChadoGeneralObject
from harvdev_utils.production import (
    Grp, GrpSynonym
)
from chado_object.chado_base import FIELD_VALUE
from sqlalchemy.orm.exc import NoResultFound

log = logging.getLogger(__name__)


class ChadoGrp(ChadoGeneralObject):
    """Process the Disease Implicated Variation (DIV) Proforma."""

    def __init__(self, params):
        """Initialise the chado object."""
        log.debug('Initializing ChadoGrp object.')

        # Initiate the parent.
        super(ChadoGrp, self).__init__(params)

        self.proforma_start_line_number = params.get('proforma_start_line_number')
        self.set_values = params.get('set_values')
        self.new = False

        self.chado = None
        # Add the chado object type
        self.alchemy_object = {"general": Grp,
                               "synonym": GrpSynonym}

        # add the chado table name i.i. grp, cell_line, library
        self.table_name = 'grp'

        self.creation_keys = {
            'symbol': 'GG1a',
            'merge': None,
            'id': 'GG1h',
            'is_current': 'GG1g',
            'rename': 'GG1e',
            'type': None,
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
        # if not self.checks(references):
        #    return None

        self.chado = self.initialise_object()

        print("We got here!!!!")
        print("chado is {}".format(self.chado)) 