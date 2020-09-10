# Cerberus and yaml
# Additional tools for validation
from cerberus import Validator

# logging imports
import logging
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
