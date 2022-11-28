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

    def _validate_no_bang(self, yml_value, proforma_field, proforma_value):
        """
        Throw error if and bang is set. NOT allowed here.

        The docstring statement below provides a schema to validate the 'plain_text' argument.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if yml_value:
            self._no_bangc(proforma_field)
            self._no_bangd(proforma_field)

    def _validate_no_bangc(self, yml_value, proforma_field, proforma_value):
        """
        Throw error if bangc is set. NOT allowed here.

        The docstring statement below provides a schema to validate the 'plain_text' argument.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if yml_value:
            self._no_bangc(proforma_field)

    def _validate_at_required(self, yml_value, proforma_field, proforma_value):
        """
        Throw error if it is required and not there.

        The docstring statement below provides a schema to validate the 'plain_text' argument.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if not yml_value:
            return
        check_arr = []
        if type(proforma_value) is list:
            check_arr = proforma_value
        else:
            check_arr.append(proforma_value)
        okay = True
        for line in check_arr:
            if not line or len(line) == 0:
                continue
            if re.search(r"@+.*@+", line) is None:
                okay = False
        if not okay:
            self._error(proforma_field, '{} @...@ is required.'.format(proforma_value))

    def _validate_at_forbidden(self, yml_value, proforma_field, proforma_value):
        """Make sure we do not have @something@.

        Not sure how to negate a regex easily in cerberus, so
        doing here where we have more control and can testfor negatice results.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if not yml_value:
            return
        if not proforma_value:
            return
        check_arr = []
        if type(proforma_value) is list:
            check_arr = proforma_value
        else:
            check_arr.append(proforma_value)
        for line in check_arr:
            if re.search(r"@+.*@+", line) is not None:
                self._error(proforma_field, 'Error {} @...@ is forbidden here.'.format(line))

    def _validate_if_new_required(self, yml_value, proforma_field, proforma_value):
        """
        Throws error if required for new.

        Args:
            yml_value (string): Value of field to use to determine if this is
                                is a new object or not. Set in yml.
            field (string): proforma field being validated.

        The rule's arguments are validated against this schema:
        {'type': 'string'}
        """
        print(f"if_new_required {yml_value}, {proforma_field}, {proforma_value}")
        if yml_value not in self.document:
            return
        if self.document[yml_value] == 'n' or self.document[yml_value] == 'new':
            if proforma_value and len(proforma_value):
                return
            else:
                self._error(proforma_field, 'Error {} Must be set for new.'.format(proforma_field))

    def _validate_at_required_in_one(self, yml_value, proforma_field, proforma_value):
        """Make sure we have @something@ on at least one line.

        cerberus does test for ech line but we just need one toi have the @..@
        hence not using a regex there.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if not proforma_value or not yml_value:
            return
        check_arr = []
        if type(proforma_value) is list:
            check_arr = proforma_value
        else:
            check_arr.append(proforma_value)
        okay = False
        for line in check_arr:
            if re.search(r"@+.*@+", line) is not None:
                okay = True
        if not okay:
            self._error(proforma_field, '{} @...@ is required on at least one line.'.format(proforma_value))

    def _validate_wrapping_values(self, yml_value, proforma_field, proforma_value):
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
    def _validate_plain_text(self, yml_value, proforma_field, proforma_value):
        """
        The docstring statement below provides a schema to validate the 'plain_text' argument.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        log.debug('Plain text validation for field: {} value: {}'.format(proforma_field, proforma_value))
        if yml_value and not re.match(r'^[a-zA-Z0-9\-:\s]*$', proforma_value):
            # Must return a self._error, otherwise the validator believes everything passed!
            self._error(proforma_field, '{} did not validate. Only a-z, A-Z, 0-9, -, :, characters permitted.'.format(proforma_value))

    def _validate_only_allowed(self, yml_value, proforma_field, proforma_value):
        """
        Check only fields in the list are allowed. (including self)
        So IF this field has a value then ONLY the fields listed are allowed.
        This is only used for things like deletion, merge etc where we want to make sure
        nothing else is done.

        The rule's arguments are validated against this schema:
        {'type': 'string'}
        """

        allowed = yml_value.split()
        allowed.append(proforma_field)  # itself allowed
        bad_fields = []
        log.debug("allowed values are {}".format(allowed))
        for key in (self.document.keys()):
            log.debug("Only allowed check: {} {}".format(key, self.document[key]))
            if key not in allowed:
                bad_fields.append(key)
        if bad_fields:
            self._error(proforma_field, 'Error {} is set so cannot set {}'.format(proforma_field, bad_fields))

    def _validate_url_format(self, yml_value, proforma_field, proforma_value):
        """
        Throw error if check it is set and value is not a valid url.

        The docstring statement below provides a schema to validate the 'plain_text' argument.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if yml_value and proforma_value:
            try:
                ret = urlparse(proforma_value)
                if not ret.scheme or not ret.netloc:
                    self._error(proforma_field, '{} does not match a valid url format'.format(proforma_field))
                    log.debug("{} FAILED url checking".format(proforma_value))
                    return
                log.debug("{} PASSED URL checking:".format(proforma_value))
            except URLError:
                log.debug("{} FAILED url checking".format(proforma_value))
                self._error(proforma_field, '{} does not match a valid url format'.format(proforma_field))

    ###########################################
    # These may be specific to certain proforma.
    # If used by more than one, please move it up
    ###########################################

    # used in DB proforma
    def _validate_required_if_bangc(self, yml_value, proforma_field, proforma_value):
        """
        Throw error if bangc is set and we have no value. NOT allowed here.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if yml_value and not proforma_value:
            self._error(proforma_field, '!c MUST have a value to be replaced with')

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
    def _validate_genomic_location_format(self, yml_value, proforma_field, proforma_value):
        """
        Throw error if it is not in a sequence format.

        chromosome:nnnn..nnnn

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if not proforma_value or not yml_value:
            return

        pattern = r"""
        ^\s*          # may have spaces
        (\S+)         # arm
        :             # chrom separator
        (\d+)         # start pos
        [.]{2}        # double dots
        (\d+)         # end pos
        """
        s_res = re.search(pattern, proforma_value, re.VERBOSE)

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
        s_res = re.search(pattern, proforma_value, re.VERBOSE)

        if s_res:  # matches the pattern above
            return

        self._error(proforma_field, 'Error {} not in a recognised format'.format(proforma_value))
