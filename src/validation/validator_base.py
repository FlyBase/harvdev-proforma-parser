# Cerberus and yaml
from cerberus import Validator

# Additional tools for validation
import re

# logging imports
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
            self._error(field, '{} did not validate. Only a-z, A-Z, 0-9, -, :, characters permitted.'.format(value))

    def _validate_no_bangc(self, no_bangc, field, value):
        """
        Throw error if bangc is set. NOT allowed here.

        The docstring statement below provides a schema to validate the 'plain_text' argument.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        log.debug("NO BANG C TEST:{}".format(self.document))
        if 'bang_c' in self.document and self.document['bang_c'] == field:
            self._error(field, '{} not allowed with bang c'.format(field))

    def _validate_need_data(self, field, dict1, comp_fields):
        """
        Throws error if comp_fields do NOT have data.
        The rule's arguments are validated against this schema:
        {'type': 'string'}
        """
        pass

    def _validate_no_data(self, field, dict1, comp_fields):
        """
        Throws error if comp_fields do have data.
        The rule's arguments are validated against this schema:
        {'type': 'string'}
        """
        pass
