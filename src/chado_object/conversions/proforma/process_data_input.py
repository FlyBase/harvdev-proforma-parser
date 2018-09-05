"""
.. module:: process_data_input
   :synopsis: A set of functions to convert different types of data into ChadoObjects.
   Multiple ChadoObjects can be created from single Proforma (or other) objects.

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
from .gene_proforma_to_chado_gene import gene_proforma_to_chado_gene
from .pub_proforma_to_chado_pub import pub_proforma_to_chado_pub

import logging
log = logging.getLogger(__name__)

def process_data_input(object_entity, curator_dict):
    """
    Process an object containing data to be loaded into Chado and convert it
    into the appropriate ChadoObject.
    
    Args:
        object_type (str): The type of object being submitted (e.g. 'GENE PROFORMA'). 
        
        object_entity (obj): The object being submitted.

    Returns:
        chado_objects (list): An anonymous list of ChadoObjects to be processed.
    """

    object_type = object_entity.proforma_type
    proforma_start_line_number = object_entity.proforma_start_line_number

    log.info('Processing %s.' % (object_type))
    log.info('From line %s.' % (proforma_start_line_number))

    # This dictionary should be very similar to 'validation_file_schema_dict' found in validation_operations
    # Be sure both are updated whenever new data type sources are incorporated (for proforma-based data types).
    type_conversion_dict = {
        'PUBLICATION PROFORMA                   Version 47:  25 Nov 2014' : (pub_proforma_to_chado_pub),
        'GENE PROFORMA                          Version 76:  04 Sept 2014' : (gene_proforma_to_chado_gene),
        'GENE PROFORMA                          Version 77:  01 Jun 2016' : (gene_proforma_to_chado_gene),
    }

    function_to_execute = type_conversion_dict[object_type] # Lookup the function to execute for this proforma object.
    list_of_chado_objects = function_to_execute(object_entity, curator_dict) # Execute the function with the proforma object as the argument.

    # Return the list of chado objects.
    log.debug('Number of objects in list returned from process_data_input: %s' % (len(list_of_chado_objects)))
    return list_of_chado_objects