# Cerberus and yaml
# Additional tools for validation
from cerberus import Validator

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

    def _validate_type_None(self, value):
        if value is None:
            log.info('Value is {}'.format(value))
            return True

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

    def _validate_if_new_required(self, other, field, value):
        """
        Throws error if required for new.
        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        log.debug("if_new_required test: {} {}".format(field, value))
        if self.document['MP1'] == 'new':
            if value and len(value):
                return
            else:
                self._error(field, 'Error {} Must be set for new pubs.'.format(field))

    def _validate_book_check(self, other, field, value):
        """
        Throws error if new book and not defined.
        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if self.bang_c == field:
            return
        if self.document['MP1'] == 'new' and self.document['MP17'] == 'book':
            if value and len(value):
                return
            else:
                self._error(field, 'Error {} is not set so cannot set but MP1 is new and MP17 is book, so is required.'.format(field))
        elif value and len(value):
            self._error(field, 'Error cannot set {} if not a new book')
