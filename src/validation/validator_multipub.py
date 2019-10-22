# Cerberus and yaml
# Additional tools for validation
from cerberus import Validator
import re
# logging imports
import logging
log = logging.getLogger(__name__)


class ValidatorMultipub(Validator):
    """
    The custom Cerberus validator used for all proforma.
    Subclasses of this validator can be found in the additional files within this directory.
    """

    def __init__(self, *args, **kwargs):
        self.bang_c = kwargs['bang_c']
        self.bang_d = kwargs['bang_d']
        self.record_type = kwargs['record_type']
        super(ValidatorMultipub, self).__init__(*args, **kwargs)

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

    def _validate_wrapping_values(self, field, dict1, comp_fields):
        """
        This is a "placeholder" validation used to indicate whether a field
        contains wrapping values. It is used by a function in
        proforma_operations to extract a list of fields which have this characteristic.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        pass

    def _validate_no_data(self, field, dict1, comp_fields):
        """
        Throws error if comp_fields do have data.
        The rule's arguments are validated against this schema:
        {'type': 'string'}
        """
        pass

    def _validate_if_new_required(self, field, dict1, comp_fields):
        pass

    def _validate_book_check(self, field, dict1, comp_fields):
        pass
 