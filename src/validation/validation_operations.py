"""

:synopsis: Functions and Classes for validating data within proformae.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>
"""

# Cerberus and yaml
import yaml
from validation.validator_pub import ValidatorPub
from validation.validator_multipub import ValidatorMultipub
from validation.validator_base import ValidatorBase
from error.error_tracking import ErrorTracking, CRITICAL_ERROR, WARNING_ERROR

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
    log.debug('Validating proforma file.')

    # TODO Add whole file validation.


def get_validate_humanhealth_schema(fields_values):
    """
    Check for special occurance of humanhealth being new.
    If they are we use the humanhealth_new.yaml file instead of
    humanhealth.yaml
    """
    if 'HH1f' in fields_values and fields_values['HH1f'][FIELD_VALUE] == "new":
        return "humanhealth_new.yaml"
    return "humanhealth.yaml"


def get_validate_pub_schema(fields_values):
    """
    Check for special occurances of publication being new.
    If they are we use the publication_new.yaml file instead of
    publication.yaml
    """
    if 'P22' in fields_values and fields_values['P22'][FIELD_VALUE] == "new":
        return "publication_new.yaml"
    return "publication.yaml"


def get_validate_multipub_schema(fields_values):
    return "multipub.yaml"


def get_validate_gene_schema(fields_values):
    return "gene.yaml"


def get_validate_allele_schema(fields_values):
    return "allele.yaml"


def get_validate_aberration_schema(fields_values):
    return "aberration.yaml"


def get_validate_chemical_schema(fields_values):
    return "chemical.yaml"


def get_validate_div_schema(fields_values):
    return "div.yaml"


def get_validate_species_schema(fields_values):
    return "species.yaml"


def get_validate_db_schema(fields_values):
    return "db.yaml"


def get_validate_grp_schema(fields_values):
    return "grp.yaml"


def get_validate_cell_line_schema(fields_values):
    return "cell_line.yaml"


def validation_file_schema_lookup(proforma_type, fields_values):
    """Lookup the file schema.

    Reads the proforma type and returns the appropriate yaml validation file
    and the appropriate schema(s) to validation against.

    Args:
        proforma_type (str): The type of proforma

        field_values (dict): A dictionary of fields and values from the proforma.

    Returns:
        yaml_file_location (str): The file location of the appropriate yaml files

    """

    root_directory = os.path.dirname(os.path.abspath(__file__))
    root_directory += '/yaml'
    # Ignore versions just get name (deal with this later if it ever becomes a problem)
    validation_dict = {"PUBLICATION": get_validate_pub_schema,
                       "MULTIPUBLICATION": get_validate_multipub_schema,
                       "GENE": get_validate_gene_schema,
                       "ALLELE": get_validate_allele_schema,
                       "ABERRATION": get_validate_aberration_schema,
                       "CHEMICAL": get_validate_chemical_schema,
                       "DISEASE": get_validate_div_schema,
                       "HUMAN": get_validate_humanhealth_schema,
                       "DATABASE": get_validate_db_schema,
                       "SPECIES": get_validate_species_schema,
                       "GENEGROUP": get_validate_grp_schema,
                       "CULTURED": get_validate_cell_line_schema}
    # if we have specific validation stuff set it up here.
    validation_base = {"PUBLICATION": ValidatorPub,
                       "MULTIPUBLICATION": ValidatorMultipub,
                       "GENE": ValidatorBase,  # ValidatorGene,
                       "ALLELE": ValidatorBase,  # ValidatorAllele,
                       "ABERRATION": ValidatorBase,
                       "CHEMICAL": ValidatorBase,  # ValidatorChem,
                       "DISEASE": ValidatorBase,  # ValidatorDiv,
                       "HUMAN": ValidatorBase,  # ValidatorHumanhealth,
                       "DATABASE": ValidatorBase,
                       "SPECIES": ValidatorBase,
                       "GENEGROUP": ValidatorBase,
                       "CULTURED": ValidatorBase}
    validator = None

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

    log.debug('Initializing validator using schema %s.' % (yaml_file))

    return yaml_file_location, validator


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
                log.debug("{}: list_object is {}".format(field, type(list_object)))
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
            log.critical('Please contact Harvdev.')
            log.critical('Exiting.')
            sys.exit(-1)
    return field_value_validation_dict


def validate_proforma_object(proforma):
    """
    Validate a proforma object against a YAML schema using Cerberus.

    Args:
        proforma (proforma pbject): To be validated.

    Returns:
        errors (dict): A dictionary containing errors from validation.
    """
    proforma_type = proforma.proforma_type
    filename = proforma.file_metadata['filename']
    proforma_start_line = proforma.proforma_start_line_number
    fields_values = proforma.fields_values

    log.debug('Validating proforma object.')

    (yaml_file_location, validatortype) = validation_file_schema_lookup(proforma_type, fields_values)
    try:
        schema_file = open(yaml_file_location, 'r')
    except FileNotFoundError:
        log.critical('Could not open file name "{}" generated for schema {}.'.format(yaml_file_location, proforma_type))
        log.critical('Please contact Harvdev.')
        log.critical('Exiting.')
        sys.exit(-1)

    schema = yaml.full_load(schema_file)
    log.debug('Schema used: {}'.format(yaml_file_location))

    validator = validatortype(record_type=proforma.file_metadata['record_type'],
                              bang_c=proforma.bang_c,
                              bang_d=proforma.bang_d)  # Custom validator for specific object.

    # Changing "fields_values" from a dictionary of tuple values to
    # a dictionary with string/list values.
    # If a value originally existed in the proforma as a list over multiple lines
    # it will also become a list again here (converted from a list of tuples).
    # This makes validation much easier.
    field_value_validation_dict = validation_field_to_dict(fields_values)

    log.debug('Field and values to be used for validation: {}'.format(field_value_validation_dict))
    results = validator.validate(field_value_validation_dict, schema)

    if results is True:
        log.debug('Validation successful.')
        # No critical errors.
        return False
    else:
        for field, values in validator.errors.items():
            log.debug('Error items below:')
            log.debug("Field is {}, values is {}".format(field, values))
            if field not in fields_values:
                critical_error_occurred = check_and_raise_errors(filename, proforma_start_line, 0, field, values)
                continue
            if type(fields_values[field][0]) is tuple:  # Some fields are lists
                line_number = fields_values[field][0][LINE_NUMBER]
            else:
                line_number = fields_values[field][LINE_NUMBER]
            critical_error_occurred = check_and_raise_errors(filename, proforma_start_line, line_number, field,
                                                             values)
        return critical_error_occurred


def check_and_raise_errors(filename, proforma_start_line, line_number, error_field, error_value):
    # Open list of critical errors.
    critical_error_file = open(os.path.dirname(os.path.abspath(__file__)) + '/critical_errors.yaml', 'r')
    critical_errors = yaml.full_load(critical_error_file)

    if type(error_value) is list:
        error_data = error_field + ': ' + " ".join(str(x) for x in error_value)
    else:
        error_data = error_field + ': ' + error_value

    # We want to search for partial matches of error_value against the critical_errors lists:
    if error_field in critical_errors:  # If we have a key in critical_errors, e.g. P22
        for critical_error_entry in critical_errors[error_field]:
            if critical_error_entry in error_data:
                log.debug('Found critical error: \'{}\' in Cerberus error value: \'{}\''.format(critical_error_entry, error_value))
                ErrorTracking(filename, proforma_start_line, line_number, 'Validation unsuccessful', error_data, error_value,
                              CRITICAL_ERROR)
                log.critical(error_data)
                return True
        # If we don't have the critical error in our dictionary, raise a warning instead.
        ErrorTracking(filename, proforma_start_line, line_number, 'Validation unsuccessful', error_data, error_value, WARNING_ERROR)
        log.warning(error_data)
        return False
    else:
        ErrorTracking(filename, proforma_start_line, line_number, 'Validation unsuccessful', error_data, error_value, WARNING_ERROR)
        log.warning(error_data)
        return False
