# Cerberus and yaml
from .validator_base import ValidatorBase
# Additional tools for validation

# logging imports
import logging
log = logging.getLogger(__name__)

class ValidatorPub(ValidatorBase):
    """
    The custom Cerberus validator used for all proforma.
    Subclasses of this validator can be found in the additional files within this directory.
    """
    
    def _validate_P1_valid(self, P1_text, field, value):
        """
        Basically P1 not allowed to be journal or compendium.
        """
        non_valid_P1 = ['compendium', 'journal']
        if P1_text and value in non_valid_P1:
            self._error(field, '{} did not validate. {} are NOT allowed values'.format(value, non_valid_P1))

    def _validate_P22_unattributed_no_value(self, other, field, value):
        """
        if P22 is 'unattributed' then value is not allowed to be defined
        """
        log.info("Testing P22 unat {} {} {}".format(field, other, value))
        if self.document['P22'] == 'unattributed' and value and len(value):
            self._error(field, 'Cannot set {} for an unattributed Pub. You have passed it "{}"'.format(field, value))
