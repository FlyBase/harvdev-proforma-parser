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

    def _validate_P22_unattributed_allowed(self, P22_text, field, value):
        """
        May supercede _validate_P22_unattributed_no_value as we can do all at one go
        only P19 and P13 allowed if unattributed.
        Quicker this way but eeror shows up on P22 rather than another field.
        """
        if P22_text and value != 'unattributed':
            return
        allowed = ['P22','P19', 'P13']  # P22 will exist aswell obviously
        bad_fields = []
        for key in (self.document.keys()):
            log.info("P22 unat allow: {} {}".format(key, self.document[key]))
            if key not in allowed:
                bad_fields.append(key)
        if bad_fields:
            self._error(field, 'Error P22 is unattributed so cannot set {}'.format(bad_fields))
