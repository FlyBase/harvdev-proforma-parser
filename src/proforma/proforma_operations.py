"""
.. module:: proforma
   :synopsis: Functions and Classes for opening and extracting data from proformae.

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
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

    filename_list = [] # A list for storing file locations.

    log.info('Searching for files to process in the directory: %s', location)
    for root, dirs, files in os.walk(location):
        for name in files:
            file_location = os.path.join(root, name)
            log.info('Adding %s to the list of files to be processed.', file_location)
            filename_list.append(file_location)

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
        log.critical('Critical error, exiting.')
        sys.exit(1)

    log.info('Found %s file(s).', len(filename_list))
    return filename_list

# def extract_data_for_field()

def process_proforma_file(file_location_from_list):
    """
    Process individual proforma files and the proforma objects within these files.

    Args:
        file_location_from_list (str): The location of an individual proforma file.
    """
    proforma_file_object = ProformaFile(file_location_from_list)
    proforma_file_object.open_file()
    list_of_proforma_objects = proforma_file_object.separate_and_identify_proforma_type()

    log.info('Processed %s proforma objects from %s' % (len(list_of_proforma_objects), file_location_from_list))

    # After extracting the publication proforma, we'll need to associate the FBrf with
    # the rest of the proforma objects. We'll store it as a string and add it to the other objects as needed.
    FBrf_to_add = list_of_proforma_objects[0].obtain_FBrf() # Obtain the FBrf from the first item in the list. Should be a pub proforma.

    # TODO: Move this FBrf addition to after validation?
    log.info('Found reference %s from %s.' % (FBrf_to_add[1], file_location_from_list))
    log.info('Attaching %s from field %s, line %s to all subsequent proforma objects.' % (FBrf_to_add[1], FBrf_to_add[0], FBrf_to_add[2]))

    list_of_processed_proforma_objects = []

    for individual_proforma in list_of_proforma_objects:
        # FBrf to add is only populated from the publications proforma (after validation).
        # It's added to every other type of proforma object as we loop through the list.
        processed_proforma_object = process_proforma_object(individual_proforma, FBrf_to_add)
        list_of_processed_proforma_objects.append(processed_proforma_object)

    return(list_of_processed_proforma_objects)

def process_proforma_object(proforma_object, FBrf_to_add):
    """
    Process individual proforma objects.
    This is the lowest level of proforma processing:
    Directory -> Files -> Objects

    Args:
        proforma_object (object): A single object from the Proforma class.

        FBrf_to_add (str): The FBrf from the proforma file (if available).
    """
    metadata, proforma_type, fields_values, bang_c, proforma_start_line_number, errors, FBrf = proforma_object.get_proforma_contents()

    filename = metadata.get('filename')
    c1_curator_id = metadata.get('c1_curator_id')
    c2_date = metadata.get('c2_date')
    c3_curator_notes_to_self = metadata.get('c3_curator_notes_to_self')

    proforma_object.add_FBrf(FBrf_to_add) # Add the FBrf this proforma object.

    log.info('Processing Proforma object type %s' % (proforma_type))
    log.info('From file: %s' % (filename))
    log.info('From line: %s' % (proforma_start_line_number))

    errors = validate_proforma_object(proforma_type, fields_values)

    proforma_object.update_errors(errors)

    return(proforma_object)

class ProformaFile(object):
    """
    The main proforma class. Handles data from proforma files: opening and validation of file-level data.
    This data is "highest level" looking at overall file structure.
    Individual proforma entries within a proforma file are handled by the separate "Proforma" class.

    Args: 
        filename (str): The filename (including directory) of a proforma.
    """
    def __init__(self, filename):
        log.info('Creating ProformaFile class object from file: %s', filename)
        self.filename = filename
        self.proforma_file_data = []

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
        """

        result_field = None
        result_value = None

        field = re.search(r"!\s*(\w+)", individual_proforma_line)
        if field:
            result_field = field.group(1)

        value = re.search(r":(.*)", individual_proforma_line)
        if value:
            result_value = value.group(1)

        return(result_field, result_value)
    
    def next_and_current_item(self, proforma_content):
        """
        Show the current and next item in an array.
        Used to find proforma values which span more than one line.

        Args:
            proforma_content (list): The list of lines from a proforma.

        Returns:
            current (str): The current line of the iterator.

            nxt (str): The next line of the iterator.
        """
        current, nxt = tee(proforma_content, 2)
        nxt = chain(islice(nxt, 1, None), [None])
        return zip(current, nxt)
    
    def separate_and_identify_proforma_type(self):
        """
        Scan the incoming data from the proforma file and identify the type.
        Splits the proforma data into groups and constructs individual Proforma objects for further processing.

        Returns:
            list_of_proforma_objects (list): A list of new Proforma objects extracted from the file.
        """

        list_of_proforma_objects = []

        field, c1_curator_id = self.get_proforma_field_and_content(self.proforma_file_data[0])
        field, c2_date = self.get_proforma_field_and_content(self.proforma_file_data[1])
        field, c3_curator_notes_to_self = self.get_proforma_field_and_content(self.proforma_file_data[2])

        # This content should remain static and be used for every proforma entry.
        proforma_metadata = {
            'filename' : self.filename,
            'c1_curator_id' : c1_curator_id,
            'c2_date' : c2_date,
            'c3_curator_notes_to_self' : c3_curator_notes_to_self
        }

        # Variables used for the upcoming loop.
        individual_proforma = None
        proforma_type = None
        field = None
        # TODO Need a better way to assess starting line number.
        line_number = 3 # We expect to start at line 4. The first three lines should be the proforma metadata used above.

        # Iterate through the content looking at the current and next line.
        for current, nxt in self.next_and_current_item(self.proforma_file_data[3:]):
            line_number += 1
            # If we find the start of a proforma section, create a new proforma object and set the type.
            # TODO Make this work more efficiently (without special case for first entry...)
            if current.startswith('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!') and not nxt.startswith('!!!!!!!!!!!!!!!!!! END OF RECORD FOR THIS PUBLICATION '):
                if individual_proforma is not None:
                    list_of_proforma_objects.append(individual_proforma)
                proforma_type = nxt[2:] # Remove ! and whitespace from beginning of line for type.
                individual_proforma = Proforma(proforma_metadata, proforma_type, line_number)
            elif proforma_type is not None and current == '! ' + proforma_type: # Add back the '! +' which was removed from proforma_type above.
                continue # if we're on the proforma_type line, go to the next line.
            elif current == '!':
                continue # if we're on a line with only an exclamation point.
            elif nxt.startswith('!!!!!!!!!!!!!!!!!! END OF RECORD FOR THIS PUBLICATION '):
                list_of_proforma_objects.append(individual_proforma) # add the last proforma entry to the list.
                break # fin.
            else:
                if current.startswith('!c'):
                    # We're in a line with a bang_c indiciator.
                    # We need the values AND we need to flag this field for banc_c processing later
                    field, value = self.get_proforma_field_and_content(current)
                    individual_proforma.add_field_and_value(field, value, line_number)
                    individual_proforma.add_bang_c(field)
                elif current.startswith('! C'):
                    # We're still in the "header" of the proforma (additional '! C' fields)
                    # Skip to the next line
                    continue
                elif current.startswith('! '):
                    # We're in a line within a proforma. Get the field and value.
                    # Field is a string, value is an array (to which other items may be added).
                    field, value = self.get_proforma_field_and_content(current)
                    individual_proforma.add_field_and_value(field, value, line_number)
                else:
                    # We're in a line which contains a value for the previously defined field.
                    # Add the entire contents of the line to the previously defined field.
                    try: 
                        individual_proforma.add_field_and_value(field, current, line_number)
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

    def __init__(self, metadata, proforma_type, proforma_start_line_number):
        self.metadata = metadata
        self.proforma_type = proforma_type
        self.errors = [] # To track whether an error has occurred. 
        self.bang_c = None
        self.proforma_start_line_number = proforma_start_line_number
        self.FBrf = None

        self.fields_values = {}

        log.info('Creating Proforma class object from individual proforma entry in: %s', self.metadata.get('filename'))
        log.info('Proforma type defined as: %s' % (proforma_type))
        log.info('Proforma object begins at line: %s' % (proforma_start_line_number))

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
        # but they need to be treated as a single string.
        list_of_fields_with_wrapping_values = [
            'P19'
        ]

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
                self.fields_values[field].append((field, value, line_number)) # Otherwise, if it is a list already, just append the value.
                log.info('Appending field %s : value %s from line %s to the existing list for this field.' % (field, value, line_number))
        else: # If the key doesn't exist, add it.
            if field in list_of_fields_that_should_be_lists:
                log.info('Adding field %s : value %s from line %s to the Proforma object as a new list.' % (field, value, line_number))
                self.fields_values[field] = []
                self.fields_values[field].append((field, value, line_number))
            else:
                self.fields_values[field] = (field, value, line_number) 
                log.info('Adding field %s : value %s from line %s to the Proforma object.' % (field, value, line_number))

    def add_bang_c(self, field):
        """
        Sets the bang_c property of the object if a bang_c is found on a proforma line.

        Args:
            field (str): The field to be assigned to the bang_c variable.

        """
        self.bang_c = field
        log.info('!c field detected for %s. Adding flag to object.' % (field))

    def get_proforma_contents(self):
        """
        Returns all the information about a proforma object.

        Returns:
            metadata(dict): The metadata (from the top of a proforma file) for a proforma object.

            proforma_type(str): The type of proforma object.

            fields_values(dict): A large dictionary containing the contents of the proforma object. Fields and values.
            
            bang_c(str): The bang_c'ed field, if one exists. Otherwise this value is None.

            error (str) OR (list): If no errors have occured, this will be None. Otherwise it will contain a list of error messages.
        """
        return(self.metadata, self.proforma_type, self.fields_values, self.bang_c, self.proforma_start_line_number, self.errors, self.FBrf)

    def update_errors(self, errors):
        if errors:
            self.errors = errors

    def obtain_FBrf(self):
        return(self.fields_values['P22'])

    def add_FBrf(self, FBrf_to_add):
        self.FBrf = FBrf_to_add