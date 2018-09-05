# Cerberus and yaml
from cerberus import Validator

# Additional tools for validation
import re

# System and logging imports
import os
import sys
import logging
log = logging.getLogger(__name__)

class ValidatorBase(Validator):
    """
    The custom Cerberus validator used for all proforma.
    Subclasses of this validator can be found in the additional files within this directory.

    Cerberus will return a warning due to the fact that we use custom fields because we 
    load schemas via YAML files: 'No validation schema is defined for the arguments of rule...'.
    This can be safely ignored.
    """

    def str_or_loop(self, field_type, field, value, function_name):
        """
        Sorts through proforma values and executes a function based on whether the value type is a string or a list.
        Used for many validation functions in this class.

        Args:
            field_type (str): The custom field type used in the YAML.

            field (str): The name of the field.

            value (str) OR (list): The value of the proforma field. Can be either a string OR list.

            function_name (func): The function to be executed for validation.
        """
        if type(value) == str:
            function_name(field_type, field, value)
        elif type(value) == list:
            for entry in value:
                function_name(field_type, field, entry)

    def _validate_plain_text(self, plain_text, field, value):
        """
        Enables validation for "plain text" schema attributes via Cerberus.
        The name of the function _validate_<schema rule> is important. See Cerberus documentation.
        Wraps another function which looks for only a-zA-Z0-9 and '-' ':' characters.

        Args:
            plain_text (bool): The field being sent to the validator. Should be True if not empty.

            field (str): The name of the field.

            value (str) OR (list): The value of the proforma field.  Can be either a string OR list.
        """

        def check(plain_text, field, value):
            """
            The actual check for "plain text" schema attribute.
            Regex searches for  a-zA-Z0-9 and '-' ':' characters.

            Args:
                plain_text (bool): The field being sent to the validator. Should be True if not empty.

                field (str): The name of the field.

                value (str) OR (list): The value of the proforma field.  Can be either a string OR list.
            """
            if plain_text and not re.match('^[a-zA-Z0-9\-:\s]*$', value):
                # Must return a self._error, otherwise the validator believes everything passed!
                self._error(field, 'Error in validation. Only a-z, A-Z, 0-9, -, :, characters permitted.')
                self._error(value, 'validation failed.')

        # The validate function executes this single line of code below.
        # It calls the "str_or_loop" function which, in turn, executes the check function above.
        self.str_or_loop(plain_text, field, value, check)