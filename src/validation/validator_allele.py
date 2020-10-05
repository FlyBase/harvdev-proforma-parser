# Cerberus and yaml
# Additional tools for validation
from cerberus import Validator
import re

import logging
log = logging.getLogger(__name__)


class ValidatorAllele(Validator):
    """
    The custom Cerberus validator used for all proforma.

    Subclasses of this validator can be found in the additional files within this directory.
    """

    def __init__(self, *args, **kwargs):
        """Initialise the Alelle validator."""
        self.bang_c = kwargs['bang_c']
        self.bang_d = kwargs['bang_d']
        self.record_type = kwargs['record_type']
        super(ValidatorAllele, self).__init__(*args, **kwargs)

    def _validate_no_bangc(self, no_bangc, field, value):
        """
        Throw error if bangc is set. NOT allowed here.

        The docstring statement below provides a schema to validate the 'plain_text' argument.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if field in self.bang_c:
            self._error(field, '{} not allowed with bang c or bang d'.format(field))

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
            if re.search(r"@+.*@+", line) is not None:
                self._error(field, 'Error {} @...@ is forbidden here.'.format(line))
