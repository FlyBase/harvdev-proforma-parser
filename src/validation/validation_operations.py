"""
.. module:: validation
   :synopsis: Functions and Classes for validating data within proformae.

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
# Cerberus and yaml
import yaml
from validation.validator_base import ValidatorBase
from error.error_tracking import ErrorTracking

# Additional tools for validation
import re

# System and logging imports
import os
import sys
import logging
log = logging.getLogger(__name__)

# Additional modules
from error.error_tracking import ErrorTracking

def validate_proforma_file():
    log.info('Validating proforma file.')

    # TODO Add whole file validation.

def validation_file_schema_lookup(proforma_type):
    """
    Reads the proforma type and returns the appropriate yaml validation file
    and the appropriate schema(s) to validation against.

    Args:
        proforma_type (str): The type of proforma

    Returns:
        yaml_file_location (str): The file location of the appropriate yaml files

    """

    root_directory = os.path.abspath('src/validation/yaml')

    validation_file_schema_dict = {
        '! PUBLICATION PROFORMA                   Version 47:  25 Nov 2014' : 'publication.yaml',
        '! GENE PROFORMA                          Version 76:  04 Sept 2014' : 'gene.yaml',
        '! GENE PROFORMA                          Version 77:  01 Jun 2016' : 'gene.yaml'
    }

    try:
        yaml_file = validation_file_schema_dict[proforma_type]
    except KeyError:
        log.critical('Proforma type not recognized for validation.')
        log.critical('Type: {}'.format(proforma_type))
        log.critical('Please contact Harvdev with this error.')
        log.critical('Exiting.')
        sys.exit(-1)

    yaml_file_location = root_directory + '/' + yaml_file

    log.info('Initializing validator using schema %s.' % (yaml_file))

    return(yaml_file_location)

def validate_proforma_object(filename, proforma_type, proforma_line, fields_values):
    """
    Validate a proforma object against a YAML schema using Cerberus.
    
    Args:
        proforma_type (str): The type of proforma.
        
        field_values (dict): A dictionary of fields and values from the proforma.

    Returns:
        errors (dict): A dictionary containing errors from validation.
    """

    log.info('Validating proforma object.')

    (yaml_file_location) = validation_file_schema_lookup(proforma_type)
    schema_file = open(yaml_file_location, 'r')
    schema = yaml.load(schema_file)
    log.debug('Schema used: {}'.format(schema))
    validator = ValidatorBase(schema) # Custom validator for specific object.

    # Changing "fields_values" from a dictionary of tuple values to
    # a dictionary with string/list values.
    # If a value originally existed in the proforma as a list over multiple lines
    # it will also become a list again here (converted from a list of tuples).
    # This makes validation much easier.
    field_value_validation_dict = {}

    for field, value in fields_values.items():
        if type(value) is list:
            for list_object in value:
                if field in field_value_validation_dict:
                    field_value_validation_dict[field].append(list_object[1])
                else:
                    field_value_validation_dict[field] = [list_object[1]]
        elif type(value) is tuple:
            field_value_validation_dict[field] = value[1]
        else:
            log.critical('Unexpected value type: {} found, expected list or tuple.'.format(type(value)))
            log.critical(field)
            log.critical(value)
            log.critical('Please contact Harvdev / Chris.')
            log.critical('Exiting.')
            sys.exit(-1)

    log.debug('Field and values validated: {}'.format(field_value_validation_dict))
    results = validator.validate(field_value_validation_dict)

    # The error storage can get really funky with some of the validation schema.
    # Errors in cases of fields with string (e.g. G1a) are simple:
    # error "values" will be a list and you can grab the first entry and you're set (e.g. values[0])
    # However, error values from a list with individual entries which are strings (e.g. G1b) are more complicated.
    # "Values" becomes a list with a single dictionary with a single key with a list as the value. Whew.
    # So everything after the elif below is to deal with this funky data structure.
    if results is True:
        log.info('Validation successful.')
    else:
        for field, values in validator.errors.items():
            log.debug('Error items below:')
            log.debug(validator.errors.items())
            if type(values[0]) is str:
                error_data = field + ": " + values[0]
                ErrorTracking(filename, proforma_line, 'Validation unsuccessful', error_data)
            elif type(values[0]) is dict:
                list_dict_keys = list(values[0].keys())
                if len(list_dict_keys) > 1:
                    log.critical('List with length > 1 unexpectedly found in validation code.')
                    log.critical('Please contact Chris and/or Harvdev with this error.')
                    log.critical('Exiting.')
                    sys.exit(-1)
                error_data = field + ": " + values[0][list_dict_keys[0]][0]
                ErrorTracking(filename, proforma_line, 'Validation unsuccessful', error_data)