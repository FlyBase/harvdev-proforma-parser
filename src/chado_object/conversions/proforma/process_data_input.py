"""Process the data input.

:synopsis: A set of functions to convert different types of data into ChadoObjects.

Multiple ChadoObjects can be created from single Proforma (or other) objects.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
from chado_object.gene.chado_gene import ChadoGene
from chado_object.chado_pub import ChadoPub
from chado_object.chado_chem import ChadoChem
from chado_object.chado_multipub import ChadoMultipub
from chado_object.humanhealth.chado_humanhealth import ChadoHumanhealth
from chado_object.chado_species import ChadoSpecies
from chado_object.chado_db import ChadoDb

import logging
import sys
import re
log = logging.getLogger(__name__)


def create_chado_objects(ChadoObjectType, proforma_object):
    """Create the chado objects."""
    (file_metadata, bang_c, bang_d,
     proforma_start_line_number, fields_values, set_values, reference) = proforma_object.get_data_for_loading()

    params_to_send = {
        'file_metadata': file_metadata,
        'fields_values': fields_values,
        'set_values': set_values,
        'bang_c': bang_c,
        'bang_d': bang_d,
        'proforma_start_line_number': proforma_start_line_number,
        'reference': reference
    }

    list_of_objects_to_return = []

    chado_object = ChadoObjectType(params_to_send)  # Initialize a ChadoObject with this new entry.
    attrs = vars(chado_object)
    log.debug('Object attributes: %s' % attrs)
    list_of_objects_to_return.append(chado_object)

    return list_of_objects_to_return


def process_data_input(proforma_object):
    """Convert data to chadoObject.

    Process an object containing data to be loaded into Chado and convert it
    into the appropriate ChadoObject.

    Args:
        object_type (str): The type of object being submitted (e.g. 'GENE PROFORMA').

        proforma_object_entity (obj): The object being submitted.

    Returns:
        chado_objects (list): An anonymous list of ChadoObjects to be processed.

    """
    # TODO These should be simple get functions.
    proforma_type = proforma_object.proforma_type
    proforma_start_line_number = proforma_object.proforma_start_line_number

    log.debug('Processing %s.' % (proforma_type))
    log.debug('From line %s.' % (proforma_start_line_number))

    # This dictionary should be very similar to 'validation_file_schema_dict' found in validation_operations
    # Be sure both are updated whenever new data type sources are incorporated (for proforma-based data types).

    pattern = r"""
              ^!        # start with a bang
              \s+       # one or more spaces
              (\w+)     # the proformat type is a word
              .*        # can have other words like HEALTH etc. ignore
              \s+       # one or more spaces
              PROFORMA  # the word proforma all CAPS
              """
    fields = re.search(pattern, proforma_type, re.VERBOSE)
    proforma_type_name = None
    if fields:
        if fields.group(1):
            proforma_type_name = fields.group(1)

    type_conversion_dict = {
        'PUBLICATION': (ChadoPub),
        'GENE': (ChadoGene),
        'CHEMICAL': (ChadoChem),
        'HUMAN': (ChadoHumanhealth),
        'MULTIPUBLICATION': (ChadoMultipub),
        'SPECIES': (ChadoSpecies),
        'DATABASE': (ChadoDb),
    }

    try:
        ChadoObjectType = type_conversion_dict[proforma_type_name]  # Lookup the function to execute for this proforma object.
    except KeyError:
        log.critical('Proforma type not recognized for conversion into Chado object.')
        log.critical('Type: {}'.format(proforma_type))
        log.critical('Please contact Harvdev with this error.')
        log.critical('Exiting.')
        sys.exit(-1)

    # Execute the function with the proforma object as the argument.
    list_of_chado_objects = create_chado_objects(ChadoObjectType, proforma_object)

    # Return the list of chado objects.
    log.debug('Number of objects in list returned from process_data_input: %s' % (len(list_of_chado_objects)))
    return list_of_chado_objects
