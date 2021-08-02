# Cerberus and yaml
# Additional tools for validation
from cerberus import Validator

# logging imports
import logging
import re
log = logging.getLogger(__name__)


class ValidatorHumanhealth(Validator):
    """
    The custom Cerberus validator used for all proforma.
    Subclasses of this validator can be found in the additional files within this directory.
    """

    def __init__(self, *args, **kwargs):
        self.bang_c = kwargs['bang_c']
        self.bang_d = kwargs['bang_d']
        self.record_type = kwargs['record_type']
        super(ValidatorHumanhealth, self).__init__(*args, **kwargs)

    def _validate_set(self, value):
        """
        No testing here this is just to enable us to use sets of data.
        The docstring statement below provides a schema to validate the 'plain_text' argument.

        The rule's arguments are validated against this schema:
        {'type': 'string'}
        """
        return True

    def _validate_type_None(self, value):
        if value is None:
            log.debug('Value is {}'.format(value))
            return True

    def _validate_no_bangc(self, no_bangc, field, value):
        """
        Throw error if bangc is set. NOT allowed here.

        The docstring statement below provides a schema to validate the 'plain_text' argument.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if field in self.bang_c:
            self._error(field, '{} not allowed with bang c or bang d'.format(field))

    def _validate_at_required(self, required, field, value):
        """
        Throw error if it is required and not there.

        The docstring statement below provides a schema to validate the 'plain_text' argument.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        check_arr = []
        if type(value) is list:
            check_arr = value
        else:
            check_arr.append(value)
        okay = True
        for line in check_arr:
            if not line or len(line) == 0:
                continue
            if re.search(r"@+.*@+", line) is None:
                okay = False
        if not okay:
            self._error(field, '{} @...@ is required.'.format(value))

    def _validate_wrapping_values(self, field, dict1, comp_fields):
        """
        This is a "placeholder" validation used to indicate whether a field
        contains wrapping values. It is used by a function in
        proforma_operations to extract a list of fields which have this characteristic.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        pass

    def _validate_at_forbidden(self, other, field, value):
        """Make sure we do not have @something@.

        Not sure how to negate a regex easily in cerberus, so
        doing here where we have more control and can testfor negatice results.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if not value:
            return
        check_arr = []
        if type(value) is list:
            check_arr = value
        else:
            check_arr.append(value)
        for line in check_arr:
            if not line or len(line) == 0:
                continue
            if re.search(r"@+.*@+", line):
                self._error(field, 'Error {} @...@ is forbidden here.'.format(line))
