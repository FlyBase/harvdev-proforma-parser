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

    def _validate_P22_unattributed_no_value(self, other, field, value):
        """
        if P22 is 'unattributed' then value is not allowed to be defined

        The docstring statement below provides a schema to validate the 'other' argument.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        log.debug("Testing P22 unat {} {} {}".format(field, other, value))
        if self.document['P22'] == 'unattributed' and value and len(value):
            self._error(field, 'Cannot set {} for an unattributed Pub. You have passed it "{}"'.format(field, value))

    def _validate_P22_unattributed_allowed(self, P22_text, field, value):
        """
        May supercede _validate_P22_unattributed_no_value as we can do all at one go
        only P19 and P13 allowed if unattributed.
        Quicker this way but eeror shows up on P22 rather than another field.

        The docstring statement below provides a schema to validate the 'P22_text' argument.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}

        """
        if P22_text and value != 'unattributed':
            return
        allowed = ['P22', 'P19', 'P13']  # P22 will exist aswell obviously
        bad_fields = []
        for key in (self.document.keys()):
            log.info("P22 unat allow: {} {}".format(key, self.document[key]))
            if key not in allowed:
                bad_fields.append(key)
        if bad_fields:
            self._error(field, 'Error P22 is unattributed so cannot set {}'.format(bad_fields))

    def get_unique_dict(self, field, value):
        """
        Create dict and produce error if duplications are there
        """
        dict1 = {}
        for item in value:
            if item in dict1:
                self._error(field, 'Error {} has {} listed more than once'.format(field, item))
            dict1[item] = 1
        return dict1

    def check_for_duplicates(self, field, dict1, comp_fields):
        """
        Check that no values are duplicated from itself (dict1)
        and the other fields listed as no duplicates allowed (comp_fields)
        """

        for with_field in comp_fields.split():
            log.info("Looking up {}".format(with_field))
            # compare to list given by field
            if with_field in self.document:
                dict2 = {}
                list2 = self.document[with_field]
                if type(list2) is not list:  # Could be a single value i.e. P22
                    list2 = []
                    list2.append(self.document[with_field])
                log.debug("{} => {}".format(with_field, list2))
                for item in list2:
                    if item in dict1:
                        self._error(field, 'Error {} in both {} and {}. Not allowed'.format(item, field, with_field))
                    if item in dict2:
                        self._error(field, 'Error {} listed twice for {}'.format(item, with_field))
                    dict2[item] = 1

    def _validate_no_duplicates(self, comp_fields, field, value):
        """
        Check that no duplicates exist.
        If with_field is not defined them compare to self only.

        The rule's arguments are validated against this schema:
        {'type': 'string'}
        """
        log.debug("Running check no duplicates with {} wrt {} {}".format(comp_fields, field, value))
        if type(value) is not list:
            log.debug("Was expecting a list but we have '{}' for {}".format(value, field))
            return

        # self compare and build first dict
        dict1 = self.get_unique_dict(field, value)
        if not comp_fields:
            return
        # check for duplicates in the list of fileds to check.
        self.check_for_duplicates(field, dict1, comp_fields)
