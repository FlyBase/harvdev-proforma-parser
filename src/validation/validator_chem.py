# Cerberus and yaml
# Additional tools for validation
from cerberus import Validator
import re
# logging imports
import logging
log = logging.getLogger(__name__)


class ValidatorChem(Validator):
    """
    The custom Cerberus validator used for all proforma.
    Subclasses of this validator can be found in the additional files within this directory.
    """

    def __init__(self, *args, **kwargs):
        self.bang_c = kwargs['bang_c']
        self.bang_d = kwargs['bang_d']
        self.record_type = kwargs['record_type']
        super(ValidatorChem, self).__init__(*args, **kwargs)

    def _validate_type_None(self, value):
        if value is None:
            log.info('Value is {}'.foramt(value))
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
        Quicker this way but error shows up on P22 rather than another field.

        The docstring statement below provides a schema to validate the 'P22_text' argument.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}

        """
        if P22_text and value != 'unattributed':
            return
        allowed = ['P22', 'P19', 'P13']  # P22 will exist as well obviously
        bad_fields = []
        for key in (self.document.keys()):
            log.debug("P22 unat allow: {} {}".format(key, self.document[key]))
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
                    if item in dict1 and item is not None:
                        self._error(field, 'Error {} in both {} and {}. Not allowed'.format(item, field, with_field))
                    if item in dict2 and item is not None:
                        self._error(field, 'Error {} listed twice for {}'.format(item, with_field))
                    dict2[item] = 1

    def _validate_no_duplicates(self, comp_fields, field, value):
        """
        Check that no duplicates exist.
        If with_field is not defined them compare to self only.

        The rule's arguments are validated against this schema:
        {'type': 'string'}
        """
        log.debug("Running check -- no duplicates with {} wrt {} {}".format(comp_fields, field, value))
        if type(value) is not list:
            log.debug("Was expecting a list but we have '{}' for {}".format(value, field))
            return

        # self compare and build first dict
        dict1 = self.get_unique_dict(field, value)
        if not comp_fields:
            return
        # check for duplicates in the list of fileds to check.
        self.check_for_duplicates(field, dict1, comp_fields)

    def _validate_P1_dependencies(self, P1_text, field, value):
        """
        for new pubs:-
        if P1 one of [paper, review, note, letter] then P34 MUST be set.
        If P1 one of [paper, journal] the P11a Must be set.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if value in ['paper', 'journal']:
            if 'P11a' not in self.document:
                self._error(field, 'Error P1 is {}, therefore page_range (P11a) must be specified'.format(value))
        if value in ['paper', 'review', 'note', 'letter']:
            if 'P34' not in self.document:
                self._error(field, 'Error P1 is {}, therefore an abstract (P34) must be specified'.format(value))

    def _validate_disease_name(self, do_test, field, value):
        """
        ! P44. Disease(s) relevant to FBrf [free text] :
        DESCRIPTION.
        Internal free text (not web-visible) stating the human disease(s) that are modeled in the paper.

        FIELD TYPE.

        Free text (@@ forbidden)

        REQUIRED ENTRY?

        Yes if P41 and P43 contain the flag disease No otherwise
        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if 'P44' in self.document:
            return
        if 'P41' in self.document and 'P43' in self.document:
            if 'disease' in self.document['P41'] and 'disease' in self.document['P43']:
                self._error('P44', 'Error P44 must have an entry as disease flag is set in both P41 and P43.')
            if 'diseaseHP' in self.document['P41'] and 'diseaseHP' in self.document['P43']:
                self._error('P44', 'Error P44 must have an entry as diseaseHP flag is set in both P41 and P43.')
        else:
            return

    def single_deposited_file(self, field, value):
        """
        Done here as a 1 line regex to check this would be a nightmare and we also
        have to check the file type is one of the allowed ones.

        validate the deposited file which look like the following
        File date: 2003.12.17 ; File size: 225792 ; File format: xls ; File name: Luschnig.2003.12.17-2.xls
        File date: 2018.1.14 ; File size: 913065443 ; File format: wig ; File name: RNA-seq/Oliver_aggregated_RNA-Seq/Oliver_aggregated_RNA-Seq.tar.gz
        File date: 2018.10.31 ; File size: 71680 ; File format: xls ; File name: Meadows.2017.9.14.VDRC_shRNA_sequences.xls

        NOTE: month part of date not allowed to start with 0

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        log.debug("validiating deposited file {}".format(value))
        valid_file_formats = ['xls', 'tsv', 'pdf', 'gif', 'jpeg', 'ppt', 'rtf', 'doc']
        order_pattern = r"""
            ^File\s{1}date[:]   # start with date
            .*                  # anything
            File\s{1}size[:]    # file size next
            .*                  # anything
            File\s{1}format[:]  # file format next
            .*                  # anything
            File\s{1}name[:]    # File name
        """
        fields = re.search(order_pattern, value, re.VERBOSE)
        if not fields:
            message = 'Error {}: One or more of "File date:", "File size:", "File format:", "File name:"'.format(field)
            message += ' Not in the string or in the incorrect order'
            self._error(field, message)

        date_pattern = r"""
            ^File\s{1}date:   # specified start
            \s+          # 1 or more spaces
            \d{4}        # four year digits
            [.]          # date seperator
            [1-9]\d*     # month none 0 first digit then maybe another whcih can be 0
            [.]          # date seperator
            \d+          # day number
            \s+          # 1 or more spaces
            ;            # string separator
        """
        fields = re.search(date_pattern, value, re.VERBOSE)
        if not fields:
            self._error(field, 'Error {}: File date: incorrect format'.format(field))

        size_pattern = r"""
            File\s{1}size:   # file size next
            \s+          # 1 or more spaces
            \d+          # digits
            \s+          # 1 or more spaces
            ;            # string separator
        """
        fields = re.search(size_pattern, value, re.VERBOSE)
        if not fields:
            self._error(field, 'Error {}: File size: incorrect format'.format(field))

        format_pattern = r"""
            File\s{1}format:  # file format
            \s+          # 1 or more spaces
            (\w)+        # chars,  grab them to check they are of a valid type
            \s+          # 1 or more spaces
            ;            # string separator
        """
        fields = re.search(format_pattern, value, re.VERBOSE)
        if not fields:
            self._error(field, 'Error {}: File format: incorrect string format'.format(field))

        if fields:
            if fields.group(1):
                if fields.group(1) not in valid_file_formats:
                    log.warn("{} not in the approved format list {}: Not critial".format(field, fields.group(1)))

        name_pattern = r"""
            File\s{1}name:  # file name
            \s+            # 1 or more spaces
            (\w)+          # chars
        """
        fields = re.search(name_pattern, value, re.VERBOSE)
        if not fields:
            self._error(field, 'Error {}: File name: incorrect string format'.format(field))

    def _validate_deposited_file(self, do_test, field, value):
        """
        We have an array of values so process each individually

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if type(value) is not list:
            if value is not None:
                self.single_deposited_file(field, value)
        else:
            for item in value:
                if item is not None:
                    self.single_deposited_file(field, item)

    def _validate_excludes_other_P11(self, do_test, field, value):
        """
        Check for only one field with data for P11 betweeen a,b,c, and d.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """

        if value is not None:

            list_of_fields = ['P11a', 'P11b', 'P11c', 'P11d']
            list_of_fields.remove(field)

            unallowed_fields = []

            for key in self.document.keys():
                if self.document[key] is not None and key in list_of_fields:
                    unallowed_fields.append(key)

            if unallowed_fields:
                self._error(field, 'Cannot set field(s) {} when using field {}.'.format(unallowed_fields, field))

    def _validate_pages_format(self, do_test, field, value):
        """
        Check for simple page numbers or variants and if two pages make sure page1 < page2.
        generate error if page does not match format ir page1 id higher than page2.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        simple_pages_regex = [
            [r'^(\d+)$', 0],                    # number only
            [r'^(\d+)[p]+$', 0],                # numbers and p or pp or even ppp etc
            [r'^p+(\d+)$', 0],                  # pp then number
            [r'(\d+)--(\d+)$', 0],              # nn--nn
            [r'(\d+) - (\d+)$', 0],             # nn - nn
            [r'^s(\d+)--s(\d+)', 0],            # 's'num--'s'num
            [r'^R(\d+)--R(\d+)', 0],            # 'R'num--'R'num
        ]
        # try a few simple ones first
        page1 = None
        page2 = None
        found = False
        if value is not None:
            for regex in simple_pages_regex:
                fields = re.search(regex[0], value)
                if fields:
                    found = True
                    if fields.group(1):
                        page1 = int(fields.group(1))
                    try:
                        page2 = int(fields.group(2))
                    except IndexError:
                        pass
                if found:
                    continue
            if found and page1 and page2:
                if page1 > page2:
                    self._error(field, 'Error {}: {} is higher than {}.'.format(field, page2, page2))
            if not found:
                self._error(field, 'Error {}: {} is of non-standard format.'.format(field, value))
