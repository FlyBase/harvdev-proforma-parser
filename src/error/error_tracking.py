"""
.. module:: error
   :synopsis: The error tracking class used to track and report errors.

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
import logging
import inspect
import os
log = logging.getLogger(__name__)

WARNING_ERROR = 1
CRITICAL_ERROR = 2


class ErrorTracking(object):

    instances = []  # Class variable for tracking instances of this class.

    def __init__(self, filename, proforma_start_line, proforma_line, error_message, error_data, level=WARNING_ERROR):
        self.filename = filename
        self.error_message = error_message
        self.error_data = error_data
        self.proforma_start_line = None
        self.error_level = level
        # This bit of code saves the filename which called the error tracking object.
        # We can use it to tailor the error message based on where it was called.
        try:
            stack = inspect.stack()[1]
            # depending on python version, stack gives different structure, so test for this.
            if type(stack) != tuple:
                error_called_from = (os.path.basename(os.path.normpath(inspect.stack()[1].filename)))
            else:
                error_called_from = (os.path.basename(os.path.normpath(stack[1])))
        except Exception as e:
            log.critical('Unexpected Exception {}'.format(e))
            log.critical("stack {}".format(inspect.stack()))
            log.critical("Could not find filename in {}".format(inspect.stack()[1]))
            error_called_from = "No idea"
        # Validation errors always report the "error line" at the start of the proforma object.
        # e.g. Where a "gene" proforma entry begins (or an allele, etc.)
        # Transaction errors always report the *actual* line where the error occurs.
        # The logic below changes the error text to be more accurate based on where the error occurred.
        if error_called_from == 'validation_operations.py':
            self.proforma_start_line = 'Proforma entry starting on line: {}'.format(proforma_start_line)
            self.proforma_line = 'Proforma error around line: {}'.format(proforma_line)
        elif error_called_from == 'transaction_operations.py':
            self.proforma_line = 'Proforma line: {}'.format(proforma_line)
        else:
            self.proforma_line = proforma_line

        ErrorTracking.instances.append(self)

    def print_error_messages(self, index_to_print):
        if self.error_level == WARNING_ERROR:
            log_message = log.warning
        else:
            log_message = log.critical

        log_message('Error #{}'.format(index_to_print))
        log_message(self.filename)
        if self.proforma_start_line:
            log_message(self.proforma_start_line)
        log_message(self.proforma_line)
        log_message(self.error_message)
        log_message(self.error_data)
        log_message('')  # Blank line
