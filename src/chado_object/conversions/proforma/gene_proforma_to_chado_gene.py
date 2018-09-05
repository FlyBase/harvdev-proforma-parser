"""
.. module:: gene_proforma_to_chado_gene
   :synopsis: A set of functions to convert different types of data into ChadoObjects.
   Multiple ChadoObjects can be created from single Proforma (or other) objects.

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
from ...chado_gene import ChadoGene
from ...chado_pub import ChadoPub

import logging
log = logging.getLogger(__name__)

def gene_proforma_to_chado_gene(object_entity, curator_dict):
    """
    Convert a proforma object (of type gene) into a ChadoObject of type gene.
    
    Args:      
        object_entity (obj): The proforma object being submitted.

    Returns:
        chado_genes (list): An list of gene ChadoObjects
    """

    (metadata, proforma_type, fields_values, bang_c, proforma_start_line_number, errors, FBrf) = object_entity.get_proforma_contents()

    # If certain fields contain more than one value (e.g. two G1b fields), we need to create two ChadoObjects out of one.

    # Create new dictionary of items for initializing a ChadoGene object.

    params_to_send = {
        'FBrf' : FBrf,
        'G1a_symbol_in_FB' : fields_values['G1a'],
        'bang_c' : bang_c,
        'filename' : metadata['filename'],
        'proforma_start_line_number' : proforma_start_line_number
    }

    dict_of_fields_to_create_multiple_objects = {
        'G1b' : 'G1b_symbol_used_in_ref',
        'G2b' : 'G2b_name_used_in_ref'
    }

    list_of_objects_to_return = []

    # We need to process fields that can contain more than one value.
    # Only one of these fields should be used in a ChadoGene object at once.
    for key, value in dict_of_fields_to_create_multiple_objects.items(): # Loop through our dict above.
        if key in fields_values: # If we find a key from our dict in the proforma object.
            for entry in fields_values[key]: # For each entry in the list with a specific key.
                params_to_send[value] = entry # Create a new entry in our params_to_send dict using the value from dict_of_fields as a key (this is cool).
                chado_gene_object = ChadoGene(params_to_send) # Initialize a ChadoGene object with this new entry.
                attrs = vars(chado_gene_object) 
                log.debug('Object attributes: %s' % (attrs))
                del params_to_send[value] # Remove the key/value pair when we're finished.
                list_of_objects_to_return.append(chado_gene_object)

    return list_of_objects_to_return