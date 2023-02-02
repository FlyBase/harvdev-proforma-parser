"""

:synopsis: Functions and Classes for opening and extracting data from proformae.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
# TODO Split this file into individual files by class.

# System and logging imports
import re
import yaml
import os
import sys
import logging

# Other modules
from itertools import tee, islice, chain
# Validation
from validation.validation_operations import validate_proforma_object
from error.error_tracking import ErrorTracking, CRITICAL_ERROR

log = logging.getLogger(__name__)


def process_proforma_directory(location):
    """Create a list of proformae from a given directory.

    Args:
        location (str): A directory of proforma files.

    Returns:
        filenames (list): A list of filenames for a directory.

    Note:
        Checks for duplciate filenames and fails if found.
    """
    filename_list = []      # A list for storing file names.
    filelocation_list = []  # A list for storing file locations.
    log.debug('Searching for files to process in the directory: %s', location)
    for root, dirs, files in os.walk(location):
        for name in files:
            file_location = os.path.join(root, name)
            log.debug('Adding %s to the list of files to be processed.', file_location)
            filename_list.append(name)
            filelocation_list.append(file_location)
    # Checking for duplicate files.
    seen_filename = set()
    duplicates = set()
    for x in filename_list:
        if x in seen_filename:
            duplicates.add(x)
        seen_filename.add(x)

    if len(duplicates) != 0:
        log.critical('Duplicate filenames found in proforma directory!')
        log.critical('Please remove duplicate files and re-run the loader.')
        log.critical('Location: %s', location)
        log.critical('Filenames: %s', duplicates)
        log.critical('Exiting.')
        sys.exit(1)

    log.debug('Found %s file(s).', len(filename_list))
    return filelocation_list


def process_proforma_file(file_location_from_list, curator_dict):
    """
    Process individual proforma files and the proforma objects within these files.

    Args:
        file_location_from_list (str): The location of an individual proforma file.
        curator_dict (dict): Curator initials to curator full name.

    Returns:
        (list): Proforma Objects that were procressed.
    """
    proforma_file_object = ProformaFile(file_location_from_list, curator_dict)

    list_of_proforma_objects = proforma_file_object.separate_and_identify_proforma_type()

    log.debug('Processed %s proforma objects from %s' % (len(list_of_proforma_objects), file_location_from_list))

    # Process and validate the proforma objects.
    list_of_processed_proforma_objects = []

    for individual_proforma_object in list_of_proforma_objects:
        # FBrf to add is only populated from the publications proforma (after validation).
        # It's added to every other type of proforma object as we loop through the list.

        message = "Processing Proforma object type '{}' from '{}' line '{}'".\
            format(individual_proforma_object.proforma_type,
                   individual_proforma_object.file_metadata['filename'],
                   individual_proforma_object.proforma_start_line_number)
        log.debug(message)
        critical_error_list = validate_proforma_object(individual_proforma_object)

        # Still append to list of list_of_processed_proforma_objects
        # even if the validation fails as we want to see whole process
        # from start to finish.
        # Errors have been logged and will not be saved, so safe.
        list_of_processed_proforma_objects.append(individual_proforma_object)
        if critical_error_list:
            log.critical('Critical error found in {}.'.format(individual_proforma_object.proforma_type))
            log.critical('Starting at line {} from file {}.'
                         .format(individual_proforma_object.proforma_start_line_number,
                                 individual_proforma_object.file_metadata['filename']))
            log.critical('Proforma object will not be processed into a Chado object.')

    # Multipub is the exception as it does not need a pub to start with
    if 'MULTIPUBLICATION' in list_of_proforma_objects[0].proforma_type:
        return list_of_processed_proforma_objects

    return list_of_processed_proforma_objects


class ProformaFile(object):
    """Proforma class object.

    The main proforma class. Handles data from proforma files: opening and validation of file-level data.
    This data is "highest level" looking at overall file structure.
    Individual proforma entries within a proforma file are handled by the separate "Proforma" class.

    Args:
        filename (str): The filename (including directory) of a proforma.
    """

    def __init__(self, filename, curator_dict):
        """Initise Object."""
        log.debug('Creating ProformaFile class object from file: %s', filename)
        self.filename = filename
        self.proforma_file_data = []
        self.curator_dict = curator_dict

        # Open the file and add the contents to a list.
        self.open_file()

    def open_file(self):
        """Open the proforma file loads the lines into a self list stored in the class.

        Args:
            filename (str): The filename (including directory) of a proforma.

        Note:
            Useful for filtering or applying functions to each line.
            Checks for empty files.
        """
        # This approach does load the entire contents of the file into memory (as a list)
        # Alternatively, you could process the file line-by-line.
        # However, these files are small and memory is plentiful, so we're reading everything for now.
        # The code can always be refactored if this becomes a problem.
        with open(self.filename, encoding='utf-8') as the_file:  # We only <3 utf-8!
            for each_line in the_file:
                if each_line.strip():  # If the line isn't blank.
                    self.proforma_file_data.append(each_line.strip())  # Add to array and remove newlines.

        if len(self.proforma_file_data) == 0:
            log.error("Empty Proforma file found: %s" % (the_file))

        log.debug("Processed %s lines." % (len(self.proforma_file_data)))

    def get_proforma_field_and_content(self, individual_proforma_line):
        """Extract the value after a colon from a line of proforma data.

        Args:
            individual_proforma_line (str): An individual line of proforma data with a colon.

        Returns:
            result_field (str): The field found before the colon.

            result_value (str): The value found after the colon.

            result_bang (str): The second character if it is c or d
        """
        result_field = None
        result_value = None
        result_bang = None
        # TODO Add additional format error checking here.

        # Do it all in one go (faster) and explain regex
        pattern = r"""
            ^!           # begining of string must be a bang
            ([cd]?)      # possibly c or d
            \s+          # 1 or more spaces
            (\w+)        # The code (word,no spaces)
            [^:]*        # verbose proforma "chatter" up to the first ":"
            :            # : to mark start of "value"
            (.*)$        # value up to the end of the string"""

        fields = re.search(pattern, individual_proforma_line, re.VERBOSE)
        if fields:
            if fields.group(2):
                result_field = fields.group(2)
            if fields.group(3):
                result_value = fields.group(3)
            if fields.group(1):
                result_bang = fields.group(1)

        return (result_field, result_value, result_bang)

    def next_and_current_item(self, proforma_content):
        """Show the current and next item in an array.

        Used to find proforma values which span more than one line.
        """
        current, nxt = tee(proforma_content, 2)
        nxt = chain(islice(nxt, 1, None), [None])
        return zip(current, nxt)

    def extract_curator_initials_and_filename_short(self):
        """Get curator name info."""
        # Grab the filename after the last slash.
        filename_short = self.filename.rsplit('/', 1)[-1]

        curator_initials = None
        record_type = None
        harv_pattern = r"""
            ^            # match from the start
            \d+          # string of integers
            \.           # a dot
            (\w+)        # The user initials
            \.           # a dot
            (\w+)        # type of proforma
            \.           # a dot
            \d+          # string of integers
            $            # end of the string"""

        cam_pattern = r"""
            ^            # match from the start
            (\D+)        # The user initials
            \d+          # string of integers
            \.           # a dot
            (\w+)        # type of proforma
            $            # end of the string"""

        fields = re.search(harv_pattern, filename_short, re.VERBOSE)
        if fields:
            curator_initials = fields.group(1)
            record_type = fields.group(2)
        else:
            fields = re.search(cam_pattern, filename_short, re.VERBOSE)
            if fields:
                curator_initials = fields.group(1)
                record_type = fields.group(2)

        return curator_initials, record_type, filename_short

    def extract_curator_fullname(self, curator_initials):
        """Get curator fullname."""
        try:
            curator_fullname = self.curator_dict[curator_initials.lower().strip()]
        except KeyError:
            log.critical('Curator not found for filename: {} using initials: {}'.format(self.filename, curator_initials))
            log.critical('Please check config file specified in the execution of this program.')
            for key in self.curator_dict.keys():
                log.critical("{}: {}".format(key, self.curator_dict[key]))
            log.critical('Exiting.')
            sys.exit(-1)

        return curator_fullname

    def process_line(self, field, line_number, current_line, individual_proforma, file_metadata):
        """Process the line and store in the data in the proforma object."""
        # Can't use startswith ('! C') due to CHEMICAL proforma.
        if re.match(r'^! C[0-9]', current_line):
            field, value, type_of_bang = self.get_proforma_field_and_content(current_line)
            if field == 'C1':
                file_metadata['curator_initials'] = value
                file_metadata['curator_fullname'] = self.extract_curator_fullname(file_metadata['curator_initials'])
            #  TODO: C2 C3 but what to do with them anyway???
            if field == 'C4':
                file_metadata['record_type'] = value
            return
        elif current_line.startswith('!c') or current_line.startswith('!d') or current_line.startswith('! '):
            field, value, type_of_bang = self.get_proforma_field_and_content(current_line)
            individual_proforma.add_field_and_value(field, value, type_of_bang, line_number, True)
        else:
            # We're in a line which contains a value for the previously defined field.
            # Add the entire contents of the line to the previously defined field.
            try:
                individual_proforma.add_field_and_value(field, current_line, None, line_number, False)
            except AttributeError:
                log.critical('Attribute error occurred when processing %s' % (self.filename))
                log.critical('Unable to parse line %s' % (line_number))
                log.critical('Please check whether this file is valid proforma.')
                log.critical('Exiting.')
                sys.exit(-1)
        return field

    def separate_and_identify_proforma_type(self):
        """Scan the incoming data from the proforma file and identify the type.

        Splits the proforma data into groups and constructs individual Proforma objects for further processing.

        Returns:
            list_of_proforma_objects (list): A list of new Proforma objects extracted from the file.
        """
        list_of_proforma_objects = []

        # Obtain curator information from the filename and the curator dictionary from the config file.
        curator_initials, record_type, filename_short = self.extract_curator_initials_and_filename_short()
        log.debug('Initials are %s' % (curator_initials))
        if curator_initials:
            curator_fullname = self.extract_curator_fullname(curator_initials)
        else:
            curator_fullname = None

        # This content should remain static and be used for every proforma entry.
        file_metadata = {
            'filename': self.filename,
            'filename_short': filename_short,
            'curator_initials': curator_initials,
            'curator_fullname': curator_fullname,
            'record_type': record_type
        }

        # Variables used for the upcoming loop.
        individual_proforma = None
        proforma_type = None
        field = None
        line_number = 0
        proforma_start = r"""
            ^!        # starts with a bang
            \s+       # at least one space
            .+        # Anything really
            PROFORMA  # word proforma
            \s+       # spaces
            Version   # word Version"""

        # Iterate through the content looking at the current and next line.
        for current_line, next_line in self.next_and_current_item(self.proforma_file_data):
            line_number += 1
            # log.debug('next line: %s' % (next_line))
            # If we find the start of a proforma section, create a new proforma object and set the type.
            if current_line.startswith('!!!!!!!!!!!!!!!!'):
                if individual_proforma is not None:
                    list_of_proforma_objects.append(individual_proforma)
                individual_proforma = None
            elif re.search(proforma_start, current_line, re.VERBOSE):
                proforma_type = current_line
                individual_proforma = Proforma(file_metadata, proforma_type, line_number)  # Create a new Proforma object.
                log.debug('Individual proforma object is %s' % individual_proforma)
            elif current_line == '!':
                continue   # If we're on a line with only an exclamation point.
            elif individual_proforma:
                field = self.process_line(field, line_number, current_line, individual_proforma, file_metadata)
            elif re.match(r'^! C[0-9]', current_line):  # curator line
                field = self.process_line(field, line_number, current_line, individual_proforma, file_metadata)
            else:
                field, value, type_of_bang = self.get_proforma_field_and_content(current_line)
                if not field:
                    log.debug("Ignoring {}".format(current_line))
                    continue
                error_message = "NO Proforma title line."
                ErrorTracking(
                    file_metadata['filename'],
                    "Proforma entry starting on line: {}".format(line_number),
                    "Proforma error around line: {}".format(line_number),
                    error_message,
                    "{}: {}".format(current_line, error_message),
                    "",
                    CRITICAL_ERROR)
        return list_of_proforma_objects


class Proforma(object):
    """This class handles the individual proforma entries obtained from a ProformaFile class."""

    #
    # NOTE: first two are 'sets' where as the set_fields_to_key needs info
    # on what the 'main' key is for the set
    #
    set_of_fields_that_should_be_lists = set()
    set_of_fields_with_wrapping_values = set()
    set_fields_to_key = {}
    excludes = set()

    location = os.getcwd() + '/src/validation/yaml'
    for filename in os.listdir(location):  # noqa: C901
        if filename.endswith('.yaml'):
            log.debug("Getting list of multi from {}".format(filename))
            with open(os.path.join(location, filename)) as yaml_location:
                yaml_to_process = yaml.full_load(yaml_location)
                for field_name in yaml_to_process.keys():
                    # Check whether field_type is list.
                    field_type = None
                    try:
                        field_type = yaml_to_process[field_name]['type']
                    except KeyError:
                        continue
                    if 'set' in yaml_to_process[field_name]:
                        set_fields_to_key[field_name] = yaml_to_process[field_name]['set']
                        log.debug("Adding {} with value {} for sets".format(field_name, yaml_to_process[field_name]['set']))
                    if 'excludes' in yaml_to_process[field_name]:
                        for item in yaml_to_process[field_name]['excludes']:
                            excludes.add(item)
                    if type(field_type) is list:
                        if 'list' in field_type:
                            set_of_fields_that_should_be_lists.add(field_name)
                    else:
                        if field_type == 'list':
                            set_of_fields_that_should_be_lists.add(field_name)
                    # Check whether wrapping values are used.
                    wrapping_values = None
                    try:
                        wrapping_values = yaml_to_process[field_name]['wrapping_values']
                        set_of_fields_with_wrapping_values.add(field_name)
                    except KeyError:
                        continue

    def __init__(self, file_metadata, proforma_type, line_number):
        """Initialise Object."""
        self.file_metadata = file_metadata  # Store our file metadata dictionary.
        self.errors = None                  # Error tracking. This will become a dict if used.
        self.bang_c = []                    # List of fields flagged for !c (if used).
        self.bang_d = []                    # List of fields flagged for !d (if used).
        self.reference = None               # Becomes the FBrf used for attribution.
        self.genus = None
        self.species = None
        self.proforma_start_line_number = line_number  # Used later for data retrieval.
        self.proforma_type = proforma_type  # Used later for data retrieval.

        self.fields_values = {}
        self.set_values = {}

        log.debug('Creating Proforma class object from individual proforma entry in: %s', self.file_metadata['filename'])
        log.debug('Proforma type defined as: %s' % proforma_type)
        log.debug('Proforma object begins at line: %s' % line_number)

        log.debug("List codes are: {}".format(Proforma.set_of_fields_that_should_be_lists))

    def add_field_and_value(self, field, value, type_of_bang, line_number, new_line):
        """Add the field and value from a proforma into a dictionary.

        Args:
            field (str): The field from the proforma.
            value (str): The value from the proforma.
            line_number (int): The line number.
            new_line (bool): True if line starts with ! blah else False (continuation of line)
        """
        if type_of_bang and field not in Proforma.set_fields_to_key:
            self.add_bang(field, value, type_of_bang, line_number)

        if value is not None:
            # remove spaces from start and end of string
            value = value.strip()

        # Field values are stored in tuples of (field, value, line number).
        # The field value key name is the same as the first part of this tuple.
        # This is redundant but useful because the key name will change when this gets loaded into a ChadoObject.
        # If we always bring along the field value in the tuple, we can always reference it later.

        if field in self.fields_values:  # If we have a previously defined key.
            if field in Proforma.set_of_fields_with_wrapping_values:  # In this case, we want to concantenate the existing and new values.
                try:
                    log.debug('Found field %s with wrapping values over multiple lines.' % (field))
                    log.debug(self.fields_values[field])
                    log.debug('Concatenating field %s existing value \'%s\' with new value \'%s\'' % (field, self.fields_values[field][1], value))
                    # This following is currently stored with a newline. Keeping the same system, unfortunately.
                    self.fields_values[field] = (field, self.fields_values[field][1] + '\n' + value, line_number)
                except IndexError:
                    log.error(f"Problem wrappung {field} {value} {self.fields_values[field]}")
            else:
                if type(self.fields_values[field]) is list and value is not None:
                    self.fields_values[field].append((field, value, line_number))  # Otherwise, if it is a list already, just append the value.
                    log.debug('Appending field %s : value %s from line %s to the existing list for this field.' % (field, value, line_number))
                elif not value:
                    pass
                else:
                    message = 'Attempted to add an additional value: {} to field: {} from line: {}'.format(value, field, line_number)
                    message += '\nCRITICAL -- Previous value was "{}"\n'.format(self.fields_values[field])
                    message += '\nCRITICAL -- Unfortunately, this field is not current specified to support multiple values.'
                    message += '\nCRITICAL --Please contact Harvdev if you believe this is a mistake.'
                    ErrorTracking(
                        self.file_metadata['filename'],
                        "Proforma entry starting on line: {}".format(line_number),
                        "Proforma error around line: {}".format(line_number),
                        message,
                        "{}:".format(field),
                        value,
                        CRITICAL_ERROR)

                    # log.critical('Exiting.')
                    # sys.exit(-1)
        else:  # If the key doesn't exist, add it.
            # Always add None objects as strings, not lists. 'None' in list format breaks Cerberus (as of 1.2)!
            if field in Proforma.set_fields_to_key:
                self.process_set(field, value, line_number, new_line, type_of_bang)
                log.debug('Adding SET data field %s : value %s from line %s to the Proforma object.' % (field, value, line_number))
            elif field in Proforma.set_of_fields_that_should_be_lists and value is not None:
                log.debug('Adding field %s : value %s from line %s to the Proforma object as a new list.' % (field, value, line_number))
                self.fields_values[field] = []
                self.fields_values[field].append((field, value, line_number))
            elif value or type_of_bang:
                self.fields_values[field] = (field, value, line_number)
                log.debug('Adding field %s : value %s from line %s to the Proforma object.' % (field, value, line_number))
            else:
                log.debug("Skipping field %s with value  '%s'" % (field, value))

    def process_set(self, field, value, line_number, new_line, type_of_bang):
        """Process set data.

        Args:
            field (str): The field from the proforma.
            value (str): The value from the proforma.
            line_number: The line number.
            new_line: True if line starts with ! blah else False (continuation of line)
            type_of_bang: 'c' or 'd'
        """
        # Example:
        # self.set_values['HH5'] = [{'HH5a': [('HH5a','acc1', 17), ('HH5a', 'acc4', 18)]}, 'HH5b': ('HH5b', 'SWISSPROT', 19)},
        #                           {'HH5a': [('HH5a','acc2', 23)], 'HH5b': ('HH5b', 'SWISSPROT', 24)}]
        set_key = self.set_fields_to_key[field]
        if set_key not in self.set_values:
            self.set_values[set_key] = []
            self.set_values[set_key].append({})

        # if field is already in the last array element and it is a new line then it must be a new one
        if new_line and field in self.set_values[set_key][-1]:
            # so add a new one
            log.debug("{} already seen so create next element in the array".format(field))
            self.set_values[set_key].append({})

        log.debug("Adding {} to {}".format(field, type(self.set_values[set_key][-1])))
        if field in Proforma.set_of_fields_that_should_be_lists and value is not None:
            if new_line:
                self.set_values[set_key][-1][field] = [(field, value, line_number, type_of_bang)]
            else:
                self.set_values[set_key][-1][field].append((field, value, line_number, type_of_bang))
        elif value is not None:
            self.set_values[set_key][-1][field] = (field, value, line_number, type_of_bang)
        elif type_of_bang == 'd':
            error_message = 'Cannot have bangd with an empty value'
            ErrorTracking(
                self.file_metadata['filename'],
                "Proforma entry starting on line: {}".format(line_number),
                "Proforma error around line: {}".format(line_number),
                error_message,
                "{}: {}".format(field, error_message),
                value,
                CRITICAL_ERROR)

    def has_bang(self, field):
        """Return true is filed has bag c or d."""
        if field in self.bang_c or field in self.bang_d:
            return True
        return False

    def add_bang(self, field, value, type_of_bang, line_number):
        """Set the bang_c or bang_d property of the object if found on a proforma line.

        Args:
            field (str): The field to be assigned to the bang_c or bang_d variable.
            value (str): Value
            type_of_bang (str): can be 'c' or 'd'
            line_number (str): line of the bang
        """
        # Sets (dependent fileds groups together)
        # No reason why we cannot have multiples bangs of these as they are
        # independent. So store the set_key for this and allow multiple.
        # the actual filed name is stored in the process_data bit.
        if field in self.set_fields_to_key:
            set_key = self.set_fields_to_key[field]
            if type_of_bang == 'c':
                self.bang_c.append(field)
                log.debug('!c field detected for {} in set {}. Adding flag to object.'.format(field, set_key))
            else:
                self.bang_d.append(field)
                log.debug('!d field detected for {} in set {}. Adding flag to object.'.format(field, set_key))
            return

        # None set data can only have one as appling one bangc may have unknown
        # consequences on others. So we only allow one for these.
        if type_of_bang == 'c':
            self.bang_c.append(field)
            log.debug('!c field detected for %s. Adding flag to object.' % field)

        elif type_of_bang == 'd':
            self.bang_d.append(field)
            log.debug('!d field detected for %s. Adding flag to object.' % field)

    def get_data_for_processing(self):
        """Get data for processing."""
        return self.proforma_type, self.file_metadata['filename'], self.proforma_start_line_number, self.fields_values

    def get_data_for_loading(self):
        """Get data for loading."""
        return self.file_metadata, \
            self.bang_c, self.bang_d, self.proforma_start_line_number, self.fields_values, self.set_values, self.reference

    def update_errors(self, errors):
        """Add errors to a proforma object.

        Creates a dictionary for self.errors if one doesn't already exist.

        Args:
            errors (dict): A dictionary containing {field : [values]} for errors. Values must be a list.
        """
        if self.errors is None:
            self.errors = errors
        else:
            self.errors.update(errors)

    def add_reference_data(self, reference_data):
        """Add reference data to self."""
        self.reference = reference_data

    def get_file_metadata(self):
        """Return metadata form reference data."""
        return self.file_metadata

    def get_errors(self):
        """Get the errors."""
        return self.errors
