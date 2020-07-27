# Cerberus and yaml
# Additional tools for validation
from cerberus import Validator
from urllib.parse import urlparse
from urllib.error import URLError
import logging
log = logging.getLogger(__name__)


class ValidatorDb(Validator):
    """
    The custom Cerberus validator used for all proforma.
    Subclasses of this validator can be found in the additional files within this directory.
    """

    def __init__(self, *args, **kwargs):
        self.bang_c = kwargs['bang_c']
        self.bang_d = kwargs['bang_d']
        self.record_type = kwargs['record_type']
        super(ValidatorDb, self).__init__(*args, **kwargs)

    def _validate_no_bangc(self, no_bangc, field, value):
        """
        Throw error if bangc is set. NOT allowed here.

        The docstring statement below provides a schema to validate the 'plain_text' argument.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if field in self.bang_c:
            self._error(field, '{} not allowed with bang c or bang d'.format(field))

    def _validate_url_format(self, checkit, field, value):
        """
        Throw error if check it is set and value is not a vlid url.

        The docstring statement below provides a schema to validate the 'plain_text' argument.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if checkit and value:
            try:
                ret = urlparse(value)
                if not ret.scheme or not ret.netloc:
                    self._error(field, '{} does not match a valid url format'.format(field))
                    log.debug("{} FAILED url checking".format(value))
                    return
                log.debug("{} PASSED URL checking:".format(value))
            except URLError:
                log.debug("{} FAILED url checking".format(value))
                self._error(field, '{} does not match a valid url format'.format(field))

    def _validate_required_if_bangc(self, check, field, value):
        """
        Throw error if bangc is set and we have no value. NOT allowed here.

        The docstring statement below provides a schema to validate the 'plain_text' argument.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if check and not value:
            self._error(field, '!c MUST have a value to be replaced with')
