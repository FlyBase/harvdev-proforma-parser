""" Cerberus validation.

   This is the list of validation routines used by cerberus.
   _validate_XXX methods are called if in the yaml file we have the field XXX.

    i.e. in species.yaml
    SP2:
        type: string
        if_new_required: SP1g
        nullable: True
        no_bang: True

    type and nullable are built in cerberus methods so are okay.
    We do need to add _validate_if_new_required and _validate_no_bang methods.

    These all need 4 arguments (listed here so we do not have to do it for each method)
    1) self
    2) (depends on definition in yaml) The value in the yaml file
       i.e. for if_new_required (above) it would be SP1g
    3) (string) field name (i.e. here it is SP2)
    4) (varies depending on type) Value in the proforma file

    NOTE: You must add a  {'type': 'YYYY'} in the comments for the method where YYYY is the type.
          Odd i know but that is the way cerberus does things.

    Here is a list of SOME of the cerberus defined methods:-
      type, required, nullable, regex, allowed, dependencies, excludes
      See https://docs.python-cerberus.org/en/stable/validation-rules.html for descriptions.

    NOTE: Even though we are calling self._error if there is a problem, this is dumped as a warning
          unless part of the string output is in the critical_errors.yaml
          So for SP2 above you will find the following in the file above.
            SP2:
              - Must be set for new
          So with the above set then we will now get a critical error.
"""
from cerberus import Validator
from urllib.parse import urlparse
from urllib.error import URLError

# Additional tools for validation
import re

# logging imports
import logging
log = logging.getLogger(__name__)


class ValidatorBase(Validator):
    """
    The custom Cerberus validator used for all proforma.
    Subclasses of this validator can be found in the additional files within this directory.
    """
    def __init__(self, *args, **kwargs):
        self.bang_c = kwargs['bang_c']
        self.bang_d = kwargs['bang_d']
        self.record_type = kwargs['record_type']
        super(ValidatorBase, self).__init__(*args, **kwargs)

    ############################################
    # Most common validations are listed first.
    ############################################

    def _no_bangc(self, field):
        """Check no bang c for this field."""
        if field in self.bang_c:
            self._error(field, '{} not allowed with bang c.'.format(field))

    def _no_bangd(self, field):
        """Check no bang d for this field."""
        if field in self.bang_d:
            self._error(field, '{} not allowed with bang d.'.format(field))

    def _validate_no_bang(self, no_bangc, field, value):
        """
        Throw error if and bang is set. NOT allowed here.

        The docstring statement below provides a schema to validate the 'plain_text' argument.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        self._no_bangc(field)
        self._no_bangd(field)

    def _validate_no_bangc(self, no_bangc, field, value):
        """
        Throw error if bangc is set. NOT allowed here.

        The docstring statement below provides a schema to validate the 'plain_text' argument.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        self._no_bangc(field)

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

    def _validate_if_new_required(self, yml_value, field, value):
        """
        Throws error if required for new.

        Args:
            yml_value (string): Value of field to use to determine if this is
                                is a new object or not. Set in yml.
            field (string): proforma field being validated.

        The rule's arguments are validated against this schema:
        {'type': 'string'}
        """
        if yml_value not in self.document:
            return
        if self.document[yml_value] == 'n' or self.document[yml_value] == 'new':
            if value and len(value):
                return
            else:
                self._error(field, 'Error {} Must be set for new.'.format(field))

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

    def _validate_wrapping_values(self, field, dict1, comp_fields):
        """Allow wrapping of values.

        This is a "placeholder" validation used to indicate whether a field
        contains wrapping values. It is used by a function in
        proforma_operations to extract a list of fields which have this characteristic.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        pass

    #########################################
    # less frequently used validation methods
    #########################################
    def _validate_plain_text(self, plain_text, field, value):
        """
        The docstring statement below provides a schema to validate the 'plain_text' argument.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        log.debug('Plain text validation for field: {} value: {}'.format(field, value))
        if plain_text and not re.match(r'^[a-zA-Z0-9\-:\s]*$', value):
            # Must return a self._error, otherwise the validator believes everything passed!
            self._error(field, '{} did not validate. Only a-z, A-Z, 0-9, -, :, characters permitted.'.format(value))

    def _validate_only_allowed(self, field_keys, field, comp_fields):
        """
        Check only fields in the list are allowed. (including self)
        So IF this field has a value then ONLY the fields listed are allowed.
        This is only used for things like deletion, merge etc where we want to make sure
        nothing else is done.

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

    def _validate_url_format(self, checkit, field, value):
        """
        Throw error if check it is set and value is not a valid url.

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

    ###########################################
    # These may be specific to certain proforma.
    # If used by more than one, please move it up
    ###########################################

    # used in DB proforma
    def _validate_required_if_bangc(self, check, field, value):
        """
        Throw error if bangc is set and we have no value. NOT allowed here.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if check and not value:
            self._error(field, '!c MUST have a value to be replaced with')

    # Used in HH Proforma
    def _validate_set(self, value):
        """
        No testing here this is just to enable us to use sets of data.
        The docstring statement below provides a schema to validate the 'plain_text' argument.

        The rule's arguments are validated against this schema:
        {'type': 'string'}
        """
        return True

    # Used in Allele Proforma
    def _validate_genomic_location_format(self, required, field, value):
        """
        Throw error if it is not in a sequence format.

        chromosome:nnnn..nnnn

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if not value:
            return

        pattern = r"""
        ^\s*          # may have spaces
        (\S+)         # arm
        :             # chrom separator
        (\d+)         # start pos
        [.]{2}        # double dots
        (\d+)         # end pos
        """
        s_res = re.search(pattern, value, re.VERBOSE)

        if s_res:  # matches the pattern above
            return

        pattern = r"""
        ^\s*          # possible spaces
        (\S+)         # arm
        :             # chrom separator
        (\d+)         # start pos
        /s+           # possible spaces
        $             # end
        """
        s_res = re.search(pattern, value, re.VERBOSE)

        if s_res:  # matches the pattern above
            return

        self._error(field, 'Error {} not in a recognised format'.format(value))
