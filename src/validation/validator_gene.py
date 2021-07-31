"""Customised Cerberus tests for Yaml.

Additional tools for validation.
"""
from cerberus import Validator

import re
import logging
log = logging.getLogger(__name__)


class ValidatorGene(Validator):
    """Base Object for Validating Gene Proforma.

    The custom Cerberus validator used for all proforma.
    Subclasses of this validator can be found in the additional files within this directory.
    """

    def __init__(self, *args, **kwargs):
        """Initialise Object."""
        self.bang_c = kwargs['bang_c']
        self.bang_d = kwargs['bang_d']
        self.record_type = kwargs['record_type']
        super(ValidatorGene, self).__init__(*args, **kwargs)

    def _validate_no_bangc(self, no_bangc, field, value):
        """Throw error if bangc is set.

        NOT allowed here.
        The docstring statement below provides a schema to validate the 'plain_text' argument.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if field in self.bang_c:
            self._error(field, '{} not allowed with bang c or bang d'.format(field))

    def _validate_if_new_required(self, other, field, value):
        """Check if required if new.

        Throws error if required for new.
        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if self.document['G1g'] == 'y':
            return
        if 'G2c' in self.document and len(self.document['G2c']) != 0:
            return

        if value and len(value):
            return
        else:
            self._error(field, 'Error {} Must be set for new gene.'.format(field))

    def _validate_wrapping_values(self, field, dict1, comp_fields):
        """Allow wrapping of values.

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
            if re.search(r"@+.*@+", line) is not None:
                self._error(field, 'Error {} @...@ is forbidden here.'.format(line))

    def _validate_at_required_in_one(self, other, field, value):
        """Make sure we have @something@ on at least one line.

        cerberus does test for ech line but we just need one toi have the @..@
        hence not using a regex there.

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
        okay = False
        for line in check_arr:
            if re.search(r"@+.*@+", line) is not None:
                okay = True
        if not okay:
            self._error(field, '{} @...@ is required on at least one line.'.format(value))
