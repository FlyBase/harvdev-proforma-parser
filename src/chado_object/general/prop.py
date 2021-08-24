"""
:synopsis: Prop functions wrt general.

:moduleauthor: Ian Longden <ianlongden@morgan.harvard.edu>
"""
from harvdev_utils.chado_functions.cvterm import get_cvterm
from chado_object.chado_base import FIELD_VALUE
from harvdev_utils.chado_functions import get_or_create
from datetime import datetime

import logging

log = logging.getLogger(__name__)


def load_generalproplist(self, key, prop_cv_id):
    """Load a general props that are in a list.

    Args:
        key (string): key/field of proforma to get data from.
        prop_cv_id (int): id of the prop cvterm
    """
    for item in self.process_data[key]['data']:
        opts = {self.primary_key_name(): self.chado.id(),
                'type_id': prop_cv_id,
                'value': item[FIELD_VALUE]}
        gp, _ = get_or_create(self.session, self.alchemy_object['prop'], **opts)
        opts = {"{}prop_id".format(self.table_name): gp.id(),
                "pub_id": self.pub.pub_id}
        get_or_create(self.session, self.alchemy_object['proppub'], **opts)


def load_generalprop(self, key):
    """Store the feature prop.

    If there is a value then it will have a 'value' in the yaml
    pointing to the field that is holding the value.

    yml options:
        cv:
        cvterm:
        value:    <optional>, key to value field.
        only_one: <optional>, defaults to False.

    Args:
        key (string): key/field of proforma to get data from.
    """
    if not self.has_data(key):
        return
    value = None
    prop_cv_id = self.cvterm_query(self.process_data[key]['cv'], self.process_data[key]['cvterm'])
    if type(self.process_data[key]['data']) is list:
        self.load_generalproplist(key, prop_cv_id)
        return
    if 'only_one' in self.process_data[key] and self.process_data[key]['only_one']:
        opts = {self.primary_key_name(): self.chado.id(),
                'type_id': prop_cv_id}
        fp, is_new = get_or_create(self.session, self.alchemy_object['prop'], **opts)
        if 'value' in self.process_data[key] and self.process_data[key]['value'] != 'YYYYMMDD':
            value = self.process_data[self.process_data[key]['value']]['data'][FIELD_VALUE]
        elif 'value' in self.process_data[key]:
            value = datetime.today().strftime('%Y%m%d')
        if is_new:
            fp.value = value
        elif fp.value:
            message = "Already has a value. Use bangc to change it"
            self.critical_error(self.process_data[self.process_data[key]['value']]['data'], message)
    elif ('value' in self.process_data[key] and self.has_data(self.process_data[key]['value'])):
        opts = {self.primary_key_name(): self.chado.id(),
                'type_id': prop_cv_id,
                'value': self.process_data[self.process_data[key]['value']]['data'][FIELD_VALUE]}
        fp, is_new = get_or_create(self.session, self.alchemy_object['prop'], **opts)
    else:
        message = "Coding error. only_one or value must be specified if not a list."
        self.critical_error(self.process_data[self.process_data[key]['value']]['data'], message)
        return

    # create general prop pub
    opts = {"{}prop_id".format(self.table_name): fp.id(),
            "pub_id": self.pub.pub_id}
    get_or_create(self.session, self.alchemy_object['proppub'], **opts)


def proppubs_exist(self, prop_cvterm, genprop_method):
    """ Count"""
    return self.session.query(self.alchemy_object['proppub']).join(self.alchemy_object['prop']).\
        filter(genprop_method == self.chado.id(),
               self.alchemy_object['prop'].type_id == prop_cvterm.cvterm_id).count()


def bangc_prop(self, key):
    """Bangc prop"""
    prop_cvterm = get_cvterm(self.session, self.process_data[key]['cv'], self.process_data[key]['cvterm'])
    genprop_method = getattr(self.alchemy_object['prop'], self.primary_key_name())

    grpprop_pubs = self.session.query(self.alchemy_object['proppub']).join(self.alchemy_object['prop']).\
        filter(genprop_method == self.chado.id(),
               self.alchemy_object['prop'].type_id == prop_cvterm.cvterm_id,
               self.alchemy_object['proppub'].pub_id == self.pub.pub_id)

    count = 0
    for grpprop_pub in grpprop_pubs:
        grpprop_id = grpprop_pub.gen_id()
        count += 1
        self.session.delete(grpprop_pub)
        if not self.proppubs_exist(prop_cvterm, genprop_method):  # No more prop
            self.session.query(self.alchemy_object['prop']).\
                filter(genprop_method == grpprop_id).delete()
        if not count:
            mess = "!d produced no deletions for cv '{}'  and pub '{}'".\
                format(prop_cvterm.name, self.pub.uniquename)
            if type(self.process_data[key]['data']) is not list:
                self.critical_error(self.process_data[key]['data'], mess)
            else:
                self.critical_error(self.process_data[key]['data'][0], mess)


def bangd_prop(self, key):
    """Bangd prop"""
    prop_cvterm = get_cvterm(self.session, self.process_data[key]['cv'], self.process_data[key]['cvterm'])
    genprop_method = getattr(self.alchemy_object['prop'], self.primary_key_name())

    if type(self.process_data[key]['data']) is not list:
        data_list = [self.process_data[key]['data']]
    else:
        data_list = self.process_data[key]['data']
    for item in data_list:
        grpprop_pubs = self.session.query(self.alchemy_object['proppub']).join(self.alchemy_object['prop']).\
            filter(genprop_method == self.chado.id(),
                   self.alchemy_object['prop'].type_id == prop_cvterm.cvterm_id,
                   self.alchemy_object['prop'].value == item[FIELD_VALUE],
                   self.alchemy_object['proppub'].pub_id == self.pub.pub_id)
        count = 0
        for grpprop_pub in grpprop_pubs:
            grpprop_id = grpprop_pub.gen_id()
            count += 1
            print("BOB: deleting {}".format(grpprop_pub))
            self.session.delete(grpprop_pub)
            if not self.proppubs_exist(prop_cvterm, genprop_method):  # No more prop
                self.session.query(self.alchemy_object['prop']).\
                    filter(genprop_method == grpprop_id).delete()
        if not count:
            mess = "!d produced no deletions for cv '{}', value '{}' and pub '{}'".\
                format(prop_cvterm.name, item[FIELD_VALUE], self.pub.uniquename)
            self.critical_error(item, mess)


def delete_prop(self, key, bangc=False):
    """Delete prop.

    Args:
        key (string): key/field of proforma to get data from.
        bangc (Bool): True if bangc operation.
                      False if a bangd operation.
                      Default is False.
    """

    if bangc:
        self.bangc_prop(key)
    else:
        self.bangd_prop(key)
