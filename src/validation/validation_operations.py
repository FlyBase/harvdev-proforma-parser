"""
.. module:: validation
   :synopsis: Functions and Classes for validating data within proformae.

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""

# Cerberus and yaml
import yaml
from validation.validator_base import ValidatorBase
from validation.validator_pub import ValidatorPub
from error.error_tracking import ErrorTracking

# Additional tools for validation
import re

# System and logging imports
import os
import sys
import logging
from chado_object.chado_base import (
    FIELD_VALUE, LINE_NUMBER
)

log = logging.getLogger(__name__)


def validate_proforma_file():
    log.info('Validating proforma file.')

    # TODO Add whole file validation.


def get_validate_pub_schema(fields_values):
    """
    Check for special occurances of publication being new.
    If they are we use the publication_new.yaml file instead of
    publication.yaml
    """
    if 'P22' in fields_values and fields_values['P22'][FIELD_VALUE] == "new":
        return "publication_new.yaml"
    return "publication.yaml"


def get_validate_gene_schema(fields_values):
    return "gene.yaml"


def validation_file_schema_lookup(proforma_type, fields_values):
    """
    Reads the proforma type and returns the appropriate yaml validation file
    and the appropriate schema(s) to validation against.

    Args:
        proforma_type (str): The type of proforma

    Returns:
        yaml_file_location (str): The file location of the appropriate yaml files

    """

    root_directory = os.path.abspath('src/validation/yaml')
    # Ignore versions just get name (deal with this later if it evers becomes a problem)
    validation_dict = {"PUBLICATION": get_validate_pub_schema,
                       "GENE": get_validate_gene_schema}
    validator = ValidatorBase
    # if we have specific validation stuff set it up here.
    validation_base = {"PUBLICATION": ValidatorPub}

    pattern = r"""
              ^!        # start with a bang
              \s+       # one or more spaces
              (\w+)     # the proformat type is a word
              \s+       # one or more spaces
              PROFORMA  # the word proforma all CAPS
              """
    fields = re.search(pattern, proforma_type, re.VERBOSE)
    proforma_type_name = None
    if fields:
        if fields.group(1):
            proforma_type_name = fields.group(1)

    try:
        yaml_file = validation_dict[proforma_type_name](fields_values)
        if proforma_type_name in validation_base:
            validator = validation_base[proforma_type_name]
    except KeyError:
        log.critical('Proforma type not recognized for validation.')
        log.critical('Type: {}'.format(proforma_type))
        log.critical('Please contact Harvdev with this error.')
        log.critical('Exiting.')
        sys.exit(-1)

    yaml_file_location = root_directory + '/' + yaml_file

    log.info('Initializing validator using schema %s.' % (yaml_file))

    return(yaml_file_location, validator)


def validation_field_to_dict(fields_values):
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
                    field_value_validation_dict[field].append(list_object[FIELD_VALUE])
                else:
                    field_value_validation_dict[field] = [list_object[FIELD_VALUE]]
        elif type(value) is tuple:
            field_value_validation_dict[field] = value[FIELD_VALUE]
        else:
            log.critical('Unexpected value type: {} found, expected list or tuple.'.format(type(value)))
            log.critical(field)
            log.critical(value)
            log.critical('Please contact Harvdev / Chris.')
            log.critical('Exiting.')
            sys.exit(-1)
    return field_value_validation_dict


def validate_proforma_object(proforma):
    """
    Validate a proforma object against a YAML schema using Cerberus.

    Args:# Error tracking modules
        proforma_type (str): The type of proforma.

        field_values (dict): A dictionary of fields and values from the proforma.

    Returns:
        errors (dict): A dictionary containing errors from validation.
    """
    proforma_type = proforma.proforma_type
    filename = proforma.file_metadata['filename']
    proforma_start_line = proforma.proforma_start_line_number
    fields_values = proforma.fields_values

    log.info('Validating proforma object.')

    (yaml_file_location, validatortype) = validation_file_schema_lookup(proforma_type, fields_values)
    try:
        schema_file = open(yaml_file_location, 'r')
    except FileNotFoundError:
        log.critical('Could not open file name "{}" generated for schema {}.'.format(yaml_file_location, proforma_type))
        log.critical('Please contact Harvdev / Chris.')
        log.critical('Exiting.')
        sys.exit(-1)

    schema = yaml.full_load(schema_file)
    log.debug('Schema used: {}'.format(yaml_file_location))

    validator = validatortype(schema, proforma.file_metadata['record_type'], proforma.bang_c, proforma.bang_d)  # Custom validator for specific object.

    # Changing "fields_values" from a dictionary of tuple values to
    # a dictionary with string/list values.
    # If a value originally existed in the proforma as a list over multiple lines
    # it will also become a list again here (converted from a list of tuples).
    # This makes validation much easier.
    field_value_validation_dict = validation_field_to_dict(fields_values)

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
            log.debug("field tuple is {}".format(fields_values))
            if type(fields_values[field][0]) is tuple:  # Some fields are lists
                line_number = fields_values[field][0][LINE_NUMBER]
            else:
                line_number = fields_values[field][LINE_NUMBER]
            if type(values[0]) is str and type(field) is str:
                error_data = field + ": " + values[0]
                ErrorTracking(filename, proforma_start_line, line_number, 'Validation unsuccessful', error_data)
            elif type(values[0]) is dict:
                list_dict_keys = list(values[0].keys())
                if len(list_dict_keys) > 1:
                    log.critical('List with length > 1 unexpectedly found in validation code.')
                    log.critical('Please contact Chris and/or Harvdev with this error.')
                    log.critical('Exiting.')
                    sys.exit(-1)
                error_data = field + ": " + values[0][list_dict_keys[0]][0]
                ErrorTracking(filename, proforma_start_line, line_number, 'Validation unsuccessful', error_data)
