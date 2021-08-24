"""
:synopsis: Cvterm functions wrt general.

:moduleauthor: Ian Longden <ianlongden@morgan.harvard.edu>
"""
from chado_object.chado_base import FIELD_VALUE
from harvdev_utils.chado_functions import get_or_create, get_cvterm
from harvdev_utils.chado_functions import CodingError
from harvdev_utils.production import Pub, Cv, Cvterm
import logging
import re

log = logging.getLogger(__name__)


def get_cvterm_by_name(self, key, item):
    """Get the cvterm of interest.

    Args:
        key (string): key/field of proforma to get data from.
        item (list): proforma tuple of (key/field, value, bangc)
    """
    pattern = None
    if 'go' in self.process_data[key] and self.process_data[key]['go']:
        pattern = r'^(.+)\s*;\s*GO:(\d+)$'
    cv_name = item[FIELD_VALUE]
    gocode = None
    if pattern:  # if is a go code we need to split
        fields = re.search(pattern, cv_name)
        if fields:
            cv_name = fields.group(1).strip()
            gocode = fields.group(2)
        else:
            message = "'{}' Does not fit the regex of {}/".format(item[FIELD_VALUE], pattern)
            self.critical_error(self.process_data[key]['data'][0], message)
            return None

    try:
        cvterm = get_cvterm(self.session, self.process_data[key]['cv'], cv_name)
    except CodingError:
        mess = "Could not find cv '{}', cvterm '{}'.".format(self.process_data[key]['cv'], cv_name)
        self.critical_error(item, mess)
        return None
    if pattern and gocode != cvterm.dbxref.accession:
        mess = "{} matches {} but lookup gives {} instead?".format(cv_name, gocode, cvterm.dbxref.accession)
        self.warning_error(item, mess)
    return cvterm


def load_cvterm(self, key):
    """Load cvterms, including GO ones.

    Args:
        key (string): key/field of proforma to get data from.
    """
    if type(self.process_data[key]['data']) is list:
        items = self.process_data[key]['data']
    else:
        items = [self.process_data[key]['data']]

    for item in items:
        cvterm = self.get_cvterm_by_name(key, item)
        if not cvterm:
            continue

        opts = {self.primary_key_name(): self.chado.id(),
                'cvterm_id': cvterm.cvterm_id,
                'pub_id': self.pub.pub_id}
        get_or_create(self.session, self.alchemy_object['cvterm'], **opts)


def delete_cvterm(self, key, bangc=False):
    """Delete cvterm.

    Args:
        key (string): key/field of proforma to get data from.
        bangc (Bool): True if bangc operation.
                      False if a bangd operation.
                      Default is False.
    """

    id_method = getattr(self.alchemy_object['cvterm'], self.primary_key_name())
    count = 0
    if bangc:
        g_cvs = self.session.query(self.alchemy_object['cvterm']).\
            join(Cvterm, self.alchemy_object['cvterm'].cvterm_id == Cvterm.cvterm_id).\
            join(Cv, Cvterm.cv_id == Cv.cv_id).\
            join(Pub, self.alchemy_object['cvterm'].pub_id == Pub.pub_id).\
            filter(id_method == self.chado.id(),
                   Cv.name == self.process_data[key]['cv'],
                   Pub.pub_id == self.pub.pub_id)
        for g_cv in g_cvs:
            count += 1
            self.session.delete(g_cv)
        if not count:  # Nothing got deleted!!!
            mess = "!c produced no deletions for cv {} and pub {}".\
                format(self.process_data[key]['cv'], self.pub.uniquename)
            if type(self.process_data[key]['data']) is not list:
                self.critical_error(self.process_data[key]['data'], mess)
            else:
                self.critical_error(self.process_data[key]['data'][0], mess)
    else:
        if type(self.process_data[key]['data']) is not list:
            data_list = [self.process_data[key]['data']]
        else:
            data_list = self.process_data[key]['data']

        for item in data_list:
            # get the specific cvterm, it could be go which needs extra checks
            cvterm = self.get_cvterm_by_name(key, item)
            g_cvs = self.session.query(self.alchemy_object['cvterm']).join(Cvterm).join(Pub).\
                filter(id_method == self.chado.id(),
                       Cvterm.cvterm_id == cvterm.cvterm_id,
                       Pub.pub_id == self.pub.pub_id)
            count = 0
            for g_cv in g_cvs:
                count += 1
                self.session.delete(g_cv)
        if not count:  # Nothing got deleted!!!
            mess = "Could not !d cvterm '{}'. It did not exist for '{}' with this pub '{}'.".\
                format(cvterm.name, self.chado.name, self.pub.uniquename)
            self.critical_error(item, mess)
