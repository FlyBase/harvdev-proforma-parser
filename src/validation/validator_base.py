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
    """
    def _validate_plain_text(self, plain_text, field, value):
        """
        The docstring statement below provides a schema to validate the 'plain_text' argument.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        log.debug('Plain text validation for field: {} value: {}'.format(field, value))
        if plain_text and not re.match(r'^[a-zA-Z0-9\-:\s]*$', value):
            # Must return a self._error, otherwise the validator believes everything passed!
            self._error(field, 'Error in validation. Only a-z, A-Z, 0-9, -, :, characters permitted.')
            self._error(value, 'Validation failed.')