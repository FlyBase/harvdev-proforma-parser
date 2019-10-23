"""
.. module:: chado_pub
   :synopsis: The "multipub" ChadoObject.

.. moduleauthor:: Ian Longden <ilongden@morgan.harvard.edu>
"""
import re
import os
from .chado_base import ChadoObject, FIELD_VALUE, FIELD_NAME
from harvdev_utils.production import (
    Cv, Cvterm, Pub, Pubprop, Pubauthor, PubRelationship, Db, Dbxref, PubDbxref
)
from harvdev_utils.chado_functions import get_or_create

import logging
from datetime import datetime

log = logging.getLogger(__name__)


class ChadoMultipub(ChadoObject):
    def __init__(self, params):
        log.info('Initializing ChadoMultipub object.')
        ##########################################
        # Set up how to process each type of input
        ##########################################
        self.type_dict = {'direct': self.load_direct,
                          'pubauthor': self.load_author,
                          'relationship': self.load_relationship,
                          'pubprop': self.load_pubprop,
                          'dbxref': self.load_dbxref,
                          'ignore': self.ignore,
                          'obsolete': self.make_obsolete}

        self.delete_dict = {'direct': self.delete_direct,
                            'pubauthor': self.delete_author,
                            'relationship': self.delete_relationships,
                            'pubprop': self.delete_pubprops,
                            'dbxref': self.delete_dbxref,
                            'ignore': self.delete_ignore,
                            'obsolete': self.delete_obsolete}

        self.proforma_start_line_number = params.get('proforma_start_line_number')

        ###########################################################
        # Values queried later, placed here for reference purposes.
        ############################################################
        self.newmultipub = False  # Modified later for new publications.

        # Initiate the parent.
        super(ChadoPub, self).__init__(params)

        ############################################################
        # Get processing info and data to be processed.
        # Please see the yml/publication.yml file for more details
        ############################################################
        yml_file = os.path.join(os.path.dirname(__file__), 'yml/publication.yml')
        # Populated self.process_data with all possible keys.
        self.process_data = self.load_reference_yaml(yml_file, params)
