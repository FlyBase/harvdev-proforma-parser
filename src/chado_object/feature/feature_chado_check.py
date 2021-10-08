"""
:synopsis: The Feature checks that cerberus is unable to do.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>,
               Ian Longden <ianlongden@morgan.harvard.edu>
"""
from chado_object.chado_base import FIELD_VALUE
from harvdev_utils.chado_functions import feature_symbol_lookup

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

import re
##################
# helper functions
##################


def check_only_certain_fields_allowed(self, key: str, allowed: list) -> None:
    """Check only allowed fields exist.

    Args:
        key (string): key/field of proforma to get pub for.
        allowed (list): list of valid allowed strings.
    """
    bad_fields = []
    for valid_key in self.process_data:
        if valid_key not in allowed:
            bad_fields.append(valid_key)
    if bad_fields:
        message = "{} prohibits use of {}".format(key, bad_fields)
        self.critical_error(self.process_data[key]['data'], message)


def check_at_symbols_exist(self, key: str) -> None:
    """Check that symbols in @@ exist.

    If @..@ found then check that the symbol inbetween these exists.

    Args:
        key (string): key/field of proforma to get pub for.
    """
    # Make sure it is a list to process.
    if type(self.process_data[key]['data']) is list:
        check_list = self.process_data[key]['data']
    else:
        check_list = [self.process_data[key]['data']]

    pattern = '@(.+?)@'
    for line in check_list:
        for match in re.findall(pattern, line[FIELD_VALUE]):
            try:
                feature_symbol_lookup(self.session, None, match)
            except MultipleResultsFound:  # No type so we could find multiple
                pass
            except NoResultFound:
                message = "Could not lookup symbol '{}'".format(match)
                self.critical_error(line, message)


def check_bad_starts(self, key: str, bad_list: list) -> None:
    """Generate warning if any lines contain bad start.

    Args:
        key (string): key/field of proforma to get pub for.
        bad_list (list): list of bad strings.
    """
    # Make sure it is a list to process.
    if type(self.process_data[key]['data']) is list:
        check_list = self.process_data[key]['data']
    else:
        check_list = [self.process_data[key]['data']]

    for line in check_list:
        for bad_start in bad_list:
            if line[FIELD_VALUE].startswith(bad_start):
                message = "Comment should not start with '{}' for {}".\
                    format(bad_start, line[FIELD_VALUE])
                self.warning_error(line, message)
