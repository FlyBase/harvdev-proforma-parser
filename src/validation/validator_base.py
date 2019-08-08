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
    def __init__(self, record_type, bang_c, bang_d):
        """
        Validator needs info on what record type it is i.e. skim, biblio etc
        Will add bangc or bang as we go along.
        """
        self.bang_c = bang_c
        self.bang_d = bang_d
        self.record_type = record_type

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
        if self.bang_c == field:
            self._error(field, '{} not allowed with bang c or bang d'.format(field))

    def _validate_only_allowed(self, field_keys, field, comp_fields):
        """
        Check only fields in the list are allowed. (including self)
        The rule's arguments are validated against this schema:
        {'type': 'string'}
        """

        allowed = field_keys.split()
        allowed.append(field)  # itself allowed
        bad_fields = []
        log.debug("allowed values are {}".format(allowed))
        for key in (self.document.keys()):
            log.debug("Only allowed check: {} {}".format(key, self.document[key]))
            if key not in allowed:
                bad_fields.append(key)
        if bad_fields:
            self._error(field, 'Error {} is set so cannot set {}'.format(field, bad_fields))

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
