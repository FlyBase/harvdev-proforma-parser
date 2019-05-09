"""
.. module:: proforma
   :synopsis: Functions and Classes for opening and extracting data from proformae.

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
#TODO Split this file into individual files by class.

# System and logging imports
import os
import sys
import logging
log = logging.getLogger(__name__)

# Validation
from validation.validation_operations import validate_proforma_file
from validation.validation_operations import validate_proforma_object

# Other modules
from itertools import tee, islice, chain
import re

def process_proforma_directory(location):
    """
    Creates a list of proformae from a given directory.

    Args:
        location (str): A directory of proforma files.

    Returns: 
        filenames (list): A list of filenames for a directory.

    Note:
        Checks for duplciate filenames and fails if found.
    """

    filename_list = []     # A list for storing file names.
    filelocation_list = [] # A list for storing file locations.
    log.info('Searching for files to process in the directory: %s', location)
    for root, dirs, files in os.walk(location):
        for name in files:
            file_location = os.path.join(root, name)
            log.info('Adding %s to the list of files to be processed.', file_location)
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

    log.info('Found %s file(s).', len(filename_list))
    return filelocation_list

# def extract_data_for_field()

def process_proforma_file(file_location_from_list, curator_dict):
    """
    Process individual proforma files and the proforma objects within these files.

    Args:
        file_location_from_list (str): The location of an individual proforma file.
    """
    proforma_file_object = ProformaFile(file_location_from_list, curator_dict)

    list_of_proforma_objects = proforma_file_object.separate_and_identify_proforma_type()

    log.info('Processed %s proforma objects from %s' % (len(list_of_proforma_objects), file_location_from_list))

    # Process and validate the proforma objects.
    list_of_processed_proforma_objects = []

    for individual_proforma_object in list_of_proforma_objects:
        # FBrf to add is only populated from the publications proforma (after validation).
        # It's added to every other type of proforma object as we loop through the list.

        proforma_type, filename, proforma_start_line_number, fields_values = individual_proforma_object.get_data_for_processing()

        log.info('Processing Proforma object type %s' % (proforma_type))
        log.info('From file: %s' % (filename))
        log.info('From line: %s' % (proforma_start_line_number))

        validate_proforma_object(filename, proforma_type, proforma_start_line_number, fields_values)

        # individual_proforma_object.update_errors(errors)

        list_of_processed_proforma_objects.append(individual_proforma_object)

    # After extracting the publication proforma, we'll need to associate publication information with
    # the rest of the proforma objects. This involves a second loop through the validated list.
    # Obtain the FBrf and other data from the first item in the list. Should be a pub proforma.
    
    # TODO Check that this entry is a pub proforma. Also implement workaround for processing DATABASE proforma which don't have pubs.
    proforma_type, filename, proforma_start_line_number, fields_values = list_of_proforma_objects[0].get_data_for_processing()
    log.info('Found reference %s from %s.' % (fields_values['P22'][1], filename))
    log.info('Attaching %s from field %s, line %s to all subsequent proforma objects.' % (fields_values['P22'][1], 'P22', fields_values['P22'][2]))

    for individual_proforma_object in list_of_processed_proforma_objects:
        individual_proforma_object.add_pub_data(fields_values['P22'])

    log.info('Successfully attached pub data to {} proforma objects'.format(len(list_of_processed_proforma_objects)))

    return(list_of_processed_proforma_objects)

class ProformaFile(object):
    """
    The main proforma class. Handles data from proforma files: opening and validation of file-level data.
    This data is "highest level" looking at overall file structure.
    Individual proforma entries within a proforma file are handled by the separate "Proforma" class.

    Args: 
        filename (str): The filename (including directory) of a proforma.
    """
    def __init__(self, filename, curator_dict):
        log.info('Creating ProformaFile class object from file: %s', filename)
        self.filename = filename
        self.proforma_file_data = []
        self.curator_dict = curator_dict

        # Open the file and add the contents to a list.
        self.open_file()

    def open_file(self):
        """
        Opens the proforma file loads the lines into a self list stored in the class.

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
        with open(self.filename, encoding='utf-8') as the_file: # We only <3 utf-8!
            for each_line in the_file:
                if each_line.strip(): # If the line isn't blank.
                    self.proforma_file_data.append(each_line.strip()) # Add to array and remove newlines.

        if len(self.proforma_file_data) == 0:
            log.error("Empty Proforma file found: %s" % (the_file))
        
        log.info("Processed %s lines." % (len(self.proforma_file_data)))

    def get_proforma_field_and_content(self, individual_proforma_line):
        """
        Extracts the value after a colon from a line of proforma data. 

        Args:
            individual_proforma_line (str): An individual line of proforma data with a colon.

        Returns:
            result_field (str): The field found before the colon.

            result_value (str): The value found after the colon.

            result_bang (str): The second character if it is c or d
        """

        result_field = None
        result_value = ''
        result_bang = None
        # TODO Add additional format error checking here.

        # Do it all in one go (faster) and explain regex
        pattern = """
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

        return(result_field, result_value, result_bang)
    
    
    def next_and_current_item(self, proforma_content):
        """
        Show the current and next item in an array.
        Used to find proforma values which span more than one line.
        """

        current, nxt = tee(proforma_content, 2)
        nxt = chain(islice(nxt, 1, None), [None])
        return zip(current, nxt)
    
    def extract_curator_initials_and_filename_short(self):

        # Grab the filename after the last slash.
        filename_short = self.filename.rsplit('/', 1)[-1]
        
        # TODO Add support for Cambridge-style filenames
        # Extract and process the curator initials.
        curator_initials = filename_short.split('.', 2)[1]

        return curator_initials, filename_short

    def extract_curator_fullname(self, curator_initials):

        log.info('Looking up curator based on filename initials.')
        
        try:
            curator_fullname = self.curator_dict[curator_initials]
            log.info('Found curator %s -> %s' % (curator_initials, curator_fullname))
        except:
            log.critical('Curator not found for filename: {} using initials: {}'.format(self.filename, curator_initials))
            log.critical('Please check config file specified in the execution of this program.')
            log.critical('Exiting.')
            sys.exit(-1)
        
        return curator_fullname

    def separate_and_identify_proforma_type(self):
        """
        Scan the incoming data from the proforma file and identify the type.
        Splits the proforma data into groups and constructs individual Proforma objects for further processing.

        Returns:
            list_of_proforma_objects (list): A list of new Proforma objects extracted from the file.
        """

        list_of_proforma_objects = []

        # Obtain curator information from the filename and the curator dictionary from the config file.
        curator_initials, filename_short = self.extract_curator_initials_and_filename_short()
        curator_fullname = self.extract_curator_fullname(curator_initials)
        
        # This content should remain static and be used for every proforma entry.
        file_metadata = {
        'filename' : self.filename,
        'filename_short' : filename_short,
        'curator_initials' : curator_initials,
        'curator_fullname' : curator_fullname
        }

        # Variables used for the upcoming loop.
        individual_proforma = None
        proforma_type = None
        field = None
        line_number = 0 

        # Iterate through the content looking at the current and next line.
        for current_line, next_line in self.next_and_current_item(self.proforma_file_data):
            line_number += 1
            # If we find the start of a proforma section, create a new proforma object and set the type.
            if current_line.startswith('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!') and not 'END OF RECORD FOR THIS PUBLICATION' in next_line:
                if individual_proforma is not None:
                    list_of_proforma_objects.append(individual_proforma)
                proforma_type = next_line
                line_number = line_number + 1 # The proforma starts on the next line.
                individual_proforma = Proforma(file_metadata, proforma_type, line_number) # Create a new Proforma object.
            elif proforma_type is not None and current_line == proforma_type:
                continue # If we're on the proforma_type line, go to the next line.
            elif current_line == '!':
                continue # If we're on a line with only an exclamation point.
            elif 'END OF RECORD FOR THIS PUBLICATION' in next_line:
                list_of_proforma_objects.append(individual_proforma) # add the last proforma entry to the list.
                break # fin.
            else:
                if current_line.startswith('! C'):
                    # We're still in the "header" of the proforma (additional '! C' fields)
                    # Skip to the next line
                    continue
                elif (current_line.startswith('!c') or 
                    current_line.startswith('!d') or
                    current_line.startswith('! ')):
                    field, value, type_of_bang = self.get_proforma_field_and_content(current_line)
                    log.debug(current_line)
                    log.debug(line_number)
                    individual_proforma.add_field_and_value(field, value, line_number)
                    if type_of_bang:
                       individual_proforma.add_bang(field, type_of_bang)
                else:
                    # We're in a line which contains a value for the previously defined field.
                    # Add the entire contents of the line to the previously defined field.
                    try: 
                        individual_proforma.add_field_and_value(field, current_line, line_number)
                    except AttributeError:
                        log.critical('Attribute error occurred when processing %s' % (self.filename))
                        log.critical('Unable to parse line %s' % (line_number))
                        log.critical('Please check whether this file is valid proforma.')
                        log.critical('Exiting.')
                        sys.exit(-1)
            
        return(list_of_proforma_objects)

class Proforma(object):
    """
    This class handles the individual proforma entries obtained from a ProformaFile class.

    Args: 
        filename (str): The filename (including directory) of a proforma.
    """

    def __init__(self, file_metadata, proforma_type, line_number):
        self.file_metadata = file_metadata # Store our file metadata dictionary.
        self.errors = None # Error tracking. This will become a dict if used.
        self.bang_c = None # Becomes the field flagged for !c (if used).
        self.bang_d = None # Becomes the field flagged for !d (if used).
        self.proforma_start_line_number = line_number # Used later for data retrieval.
        self.proforma_type = proforma_type # Used later for data retrieval.
        
        self.fields_values = {}

        log.info('Creating Proforma class object from individual proforma entry in: %s', self.file_metadata['filename'])
        log.info('Proforma type defined as: %s' % (proforma_type))
        log.info('Proforma object begins at line: %s' % (line_number))

    def add_field_and_value(self, field, value, line_number):
        """
        Adds the field and value from a proforma into a dictionary.

        Args:
            field (str): The field from the proforma.

            value (str): The value from the proforma.
        """

        if value == '': # Leave this function if the value is an empty string.
            return

        # A list of fields where values might span multiple lines
        # but they need to be treated as a single entry.
        # Not a fan of hard-coding fields here but I can't seem to find a way around it.
        list_of_fields_with_wrapping_values = [
            'P19'
        ]

        # TODO Generate this list from the validation YAML.
        # A list of fields which should always be handled as lists, even if they are single values.
        # This saves a tremendous amount of downstream code in handling strings vs lists.
        # Basically, if a field *can* be a list, it will be turned into a list.
        list_of_fields_that_should_be_lists = [
            'P40',
            'P41',
            'G1b',
            'G2b',
        ]

        # Field values are stored in tuples of (field, value, line number).
        # The field value key name is the same as the first part of this tuple.
        # This is redundant but useful because the key name will change when this gets loaded into a ChadoObject.
        # If we always bring along the field value in the tuple, we can always reference it later.

        if field in self.fields_values: # If we have a previously defined key.
            if field in list_of_fields_with_wrapping_values: # In this case, we want to concantenate the existing and new values.
                log.info('Found field %s with wrapping values over multiple lines.' % (field))
                log.info('Concantenating field %s existing value \'%s\' with new value \'%s\'' % (field, self.fields_values[field][1], value))
                self.fields_values[field] = (field, self.fields_values[field][1] + '\n' + value, line_number) # This is currently stored with a newline. Keeping the same system, unfortunately.
            else:
                if type(self.fields_values[field]) is list:
                    self.fields_values[field].append((field, value, line_number)) # Otherwise, if it is a list already, just append the value.
                    log.info('Appending field %s : value %s from line %s to the existing list for this field.' % (field, value, line_number))
                else: 
                    log.critical('Attempted to add an additional value: {} to field: {} from line: {}'.format(value, field, line_number))
                    log.critical('Unfortunately, this field is not current specified to support multiple values.')
                    log.critical('Please contact Harvdev if you believe this is a mistake.')
                    log.critical('Exiting.')
                    sys.exit(-1)
        else: # If the key doesn't exist, add it.
            if field in list_of_fields_that_should_be_lists:
                log.info('Adding field %s : value %s from line %s to the Proforma object as a new list.' % (field, value, line_number))
                self.fields_values[field] = []
                self.fields_values[field].append((field, value, line_number))
            else:
                self.fields_values[field] = (field, value, line_number) 
                log.info('Adding field %s : value %s from line %s to the Proforma object.' % (field, value, line_number))

    def add_bang(self, field, type_of_bang):
        """
        Sets the bang_c or bang_d property of the object if found on a proforma line.

        Args:
            field (str): The field to be assigned to the bang_c or bang_d variable.

        """
        if type_of_bang == 'c':
            if self.bang_c is not None:
                log.critical('Multiple !c entries found. This is not currently supported.')
                field_total = self.bang_c + ', ' + field
                self.update_errors({field_total: ['Multiple !d entries found. This is not currently supported.']})
                # TODO Update error tracking.

            self.bang_c = field
            log.info('!c field detected for %s. Adding flag to object.' % (field))
            
        elif type_of_bang == 'd':
            if self.bang_d is not None:
                log.critical('Multiple !d entries found. This is not currently supported.')
                field_total = self.bang_d + ', ' + field
                self.update_errors({field_total: ['Multiple !d entries found. This is not currently supported.']})
                # TODO Update to new error tracking.

            self.bang_d = field
            log.info('!d field detected for %s. Adding flag to object.' % (field))

    def get_data_for_processing(self):
        return(self.proforma_type, self.file_metadata['filename'], self.proforma_start_line_number, self.fields_values)

    def get_data_for_loading(self):
        return(self.file_metadata, self.bang_c, self.bang_d, self.proforma_start_line_number, self.fields_values)

    def update_errors(self, errors):
        """
        Adds errors to a proforma object. Creates a dictionary for self.errors if one doesn't already exist.

        Args:
            errors (dict): A dictionary containing {field : [values]} for errors. Values must be a list.
        """
        if self.errors is None:
            self.errors = errors
        else:
            self.errors.update(errors)

    def add_pub_data(self, pub_data):
        self.fields_values['P22'] = pub_data

    def get_file_metadata(self):
        return self.file_metadata

    def get_errors(self):
        return self.errors