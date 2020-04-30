"""
:synopsis: The Gene checks that cerberus is unable to do.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>, Ian Longden <ilongden@morgan.harvard.edu>
"""
from chado_object.chado_base import FIELD_VALUE

import logging
log = logging.getLogger(__name__)

###########################################
# Checks, put together to help find easier.
###########################################

##################
# helper functions
##################


def check_only_certain_fields_allowed(self, key, allowed):
    """Check only allowed fields exist."""
    bad_fields = []
    for valid_key in self.process_data:
        if valid_key not in allowed:
            bad_fields.append(valid_key)
    if bad_fields:
        message = "{} prohibits use of {}".format(key, bad_fields)
        self.critical_error(self.process_data[key]['data'], message)

##############################################################
# Gxx checks.
# Try to keep these is field order to make it easier to find.
##############################################################


def g28a_check(self, key):
    """G28a checks.

    1) check that entries flanked by @@ are valid symbols of any FBid type
       (either existing already in chado or instantiated in the curation record).
       NOTE: Still needs doing.

    2)  sub 'check_stamped_free_text' also checks that the line does not
        *start with* either of the following (to catch cases where SoftCV field
        data has been put into a neighbouring free text field by mistake):

       'Source for identity of: '
       'Source for merge of: '
    """
    for line in self.process_data[key]['data']:
        for bad_start in ('Source for identity of: ', 'Source for merge of: '):
            if line.startswith(bad_start):
                message = "Comment should not start with {} for {}".\
                    format(bad_start, line)
                self.warning_error(self.process_data[key]['data'], message)


def g28b_check(self, key):
    """G28b checks.

    1) If you are using G1e to rename a gene symbol, you must fill in G28b.
        using the 'Source for identity of:' SoftCV.
    2) If you are using G1f to merge two (or more) gene reports,
        then you must fill in G28b. using the 'Source for merge of:' SoftCV.
    """
    if self.has_data('G1e'):
        line_segment = 'Source for identity of:'
        sup_key = 'G1e'
    elif self.has_data('G1f'):
        line_segment = 'Source for merge of:'
        sup_key = 'G1f'
    else:
        return
    if line_segment not in self.process_data[key]['data'][FIELD_VALUE]:
        message = "{} not found (required from {}) in {}".\
            format(line_segment, sup_key, self.process_data[key]['data'][FIELD_VALUE])
        self.critical_error(self.process_data[key]['data'], message)


def g31a_check(self, key):
    """G31a checks.

    If G31a contains the value y,
    G1g must also be y and G1a must contain a symbol
    which is the valid symbol of a gene which is already in FlyBase.
    All other fields in this proforma, including the non-renaming fields,
    must be blank.
    """
    self.check_only_certain_fields_allowed('G31a', ['G1a', 'G1g', 'G31a'])


def g31b_check(self, key):
    """G31b checks.

    If G31b contains the value y, G1g must also be y and
    G1a must contain a symbol which is the valid symbol
    of a gene which is already in FlyBase.
    All other fields in this proforma, including the non-renaming fields,
    must be blank.
    """
    self.check_only_certain_fields_allowed('G31b', ['G1a', 'G1g', 'G31b'])
