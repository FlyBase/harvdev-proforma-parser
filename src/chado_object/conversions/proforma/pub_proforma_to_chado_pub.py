"""
.. module:: pub_proforma_to_chado_pub
   :synopsis: A set of functions to convert different types of data into ChadoObjects.
   Multiple ChadoObjects can be created from single Proforma (or other) objects.

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
from ...chado_gene import ChadoGene
from ...chado_pub import ChadoPub

import logging
log = logging.getLogger(__name__)

def pub_proforma_to_chado_pub(object_entity, curator_dict):
    """
    Convert a proforma object (of type pub) into a ChadoObject of type pub.
    
    Args:      
        object_entity (obj): The proforma object being submitted.

    Returns:
        chado_pub (list): An list of ChadoPub objects.
    """

    (metadata, proforma_type, fields_values, bang_c, proforma_start_line_number, errors, FBrf) = object_entity.get_proforma_contents()

    # Grab the filename after the last slash.
    filename_short = metadata['filename'].rsplit('/', 1)[-1]
    # Extract and process the curator initials.
    curator_initials = filename_short.split('.', 2)[1]
    log.info('Looking up curator based on filename initials.')
    try:
        curator_fullname = curator_dict[curator_initials]
    except:
        log.error('Curator not found for filename %s' % (filename_short))
    log.info('Found curator %s -> %s' % (curator_initials, curator_fullname))

    params_to_send = {
        'FBrf' : FBrf,
        'bang_c' : bang_c,
        'filename' : metadata['filename'],
        'filename_short' : filename_short,
        'curator_fullname': curator_fullname,
        'proforma_start_line_number' : proforma_start_line_number
    }

    if 'P19' in fields_values:
        params_to_send['P19_internal_notes'] = fields_values['P19']

    if 'P40' in fields_values:
        params_to_send['P40_flag_cambridge'] = fields_values['P40']

    if 'P41' in fields_values:
        params_to_send['P41_flag_harvard'] = fields_values['P41']

    list_of_objects_to_return = []

    chado_pub_object = ChadoPub(params_to_send) # Initialize a ChadoPub object with this new entry.
    attrs = vars(chado_pub_object) 
    log.debug('Object attributes: %s' % (attrs))
    list_of_objects_to_return.append(chado_pub_object)

    return list_of_objects_to_return