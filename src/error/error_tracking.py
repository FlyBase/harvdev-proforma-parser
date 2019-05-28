"""
.. module:: error
   :synopsis: The error tracking class used to track and report errors.

.. moduleauthor:: Christopher Tabone <ctabone@morgan.harvard.edu>
"""
import logging, inspect, os
log = logging.getLogger(__name__)

class ErrorTracking(object):

    instances = [] # Class variable for tracking instances of this class.

    def __init__(self, filename, proforma_line, error_message, error_data):
        self.filename = filename
        self.error_message = error_message
        self.error_data = error_data

        # This bit of code saves the filename which called the error tracking object.
        # We can use it to tailor the error message based on where it was called.
        try:
            error_called_from = (os.path.basename(os.path.normpath(inspect.stack()[1].filename)))
        except:
            log.critical("stack {}".format(inspect.stack()))
            log.critical("COuld not find filename in {}".format(inspect.stack()[1]))
            error_called_from = "No idea"
        # Validation errors always report the "error line" at the start of the proforma object.
        # e.g. Where a "gene" proforma entry begins (or an allele, etc.)
        # Transaction errors always report the *actual* line where the error occurs.
        # The logic below changes the error text to be more accurate based on where the error occurred.
        if error_called_from == 'validation_operations.py':
            self.proforma_line = 'Proforma entry starting on line: {}'.format(proforma_line)
        elif error_called_from == 'transaction_operations.py':
            self.proforma_line = 'Proforma line: {}'.format(proforma_line)
        else:
            self.proforma_line = proforma_line

        ErrorTracking.instances.append(self)
        self.print_error_messages()

    def print_error_messages(self):
        log.critical(self.filename)
        log.critical(self.proforma_line)
        log.critical(self.error_message)
        log.critical(self.error_data)