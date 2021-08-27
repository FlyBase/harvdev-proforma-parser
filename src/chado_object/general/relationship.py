"""
:synopsis: Relationship functions wrt general.

:moduleauthor: Ian Longden <ianlongden@morgan.harvard.edu>
"""
from harvdev_utils.chado_functions.cvterm import get_cvterm
from chado_object.chado_base import FIELD_VALUE
from harvdev_utils.chado_functions import get_or_create
from harvdev_utils.production import Synonym, Pub
from sqlalchemy.orm.exc import NoResultFound
import logging

log = logging.getLogger(__name__)


def load_relationship(self, key):
    """Load relationship (too same type).

    Args:
        key (string): key/field of proforma to get data from.
    """
    # make it a list, this may not always be the case.
    if type(self.process_data[key]['data']) is not list:
        data_list = []
        data_list.append(self.process_data[key]['data'])
    else:
        data_list = self.process_data[key]['data']
    # lookup relationship object
    for item in data_list:
        cvterm = get_cvterm(self.session, 'synonym type', 'symbol')
        try:
            gensyn = self.session.query(self.alchemy_object['synonym']).\
                join(Synonym).join(Pub).\
                filter(Synonym.name == item[FIELD_VALUE],
                       Pub.uniquename == 'unattributed',
                       Synonym.type_id == cvterm.cvterm_id,
                       self.alchemy_object['synonym'].is_current == 't').one()
        except NoResultFound:
            self.critical_error(item, "Could not find '{}' in synonym lookup.".format(item[FIELD_VALUE]))
            return

        # get cvterm for type of relationship
        cvterm = get_cvterm(self.session, self.process_data[key]['rel_cv'], self.process_data[key]['rel_cvterm'])

        # create XXX_relationship
        opts = {'type_id': cvterm.cvterm_id}
        if self.process_data[key]['subject']:
            opts['subject_id'] = gensyn.first_id()
            opts['object_id'] = self.chado.primary_id()
        else:
            opts['object_id'] = gensyn.first_id()
            opts['subject_id'] = self.chado.primary_id()
        gr, _ = get_or_create(self.session, self.alchemy_object['relationship'], **opts)

        # create XXX_relationshipPub
        opts = {'{}_relationship_id'.format(self.table_name): gr.primary_id(),
                'pub_id': self.pub.pub_id}
        get_or_create(self.session, self.alchemy_object['relationshippub'], **opts)


def relatepubs_exist(self, cvterm, subject_lookup):
    """Count of genrelationshippubs"""
    if subject_lookup:
        statement = getattr(self.alchemy_object['relationship'], 'subject_id')
    else:
        statement = getattr(self.alchemy_object['relationship'], 'object_id')
    return self.session.query(self.alchemy_object['relationshippub']).\
        join(self.alchemy_object['relationship']).\
        filter(statement == self.chado.primary_id(),
               self.alchemy_object['relationship'].type_id == cvterm.cvterm_id).count()


def bangc_relationship(self, key):
    """Bangc the rerlationship"""
    cvterm = get_cvterm(self.session, self.process_data[key]['rel_cv'], self.process_data[key]['rel_cvterm'])

    genrelate_statement = getattr(self.alchemy_object['relationship'], "{}_relationship_id".format(self.table_name))
    subject_lookup = False
    # If subject is specified in the yml then it means the self.chado object is the object_id
    if self.process_data[key]['subject']:
        subject_lookup = True
        id_statement = getattr(self.alchemy_object['relationship'], 'object_id')
    else:
        id_statement = getattr(self.alchemy_object['relationship'], 'subject_id')
    genrelate_pubs = self.session.query(self.alchemy_object['relationshippub']).\
        join(self.alchemy_object['relationship']).\
        filter(self.alchemy_object['relationship'].type_id == cvterm.cvterm_id,
               self.alchemy_object['relationshippub'].pub_id == self.pub.pub_id,
               id_statement == self.chado.primary_id())

    count = 0
    for genrelate_pub in genrelate_pubs:
        genrelate_id = genrelate_pub.first_id()
        self.session.delete(genrelate_pub)
        count += 1
        if not self.relatepubs_exist(cvterm, subject_lookup):  # No more relationship pubs
            self.session.query(self.alchemy_object['relationship']).\
                filter(genrelate_statement == genrelate_id).delete()
    if not count:
        mess = "No relationships to bangc for {} and {}".format(self.chado.name, self.pub.uniquename)
        if type(self.process_data[key]['data']) is not list:
            self.critical_error(self.process_data[key]['data'], mess)
        else:
            self.critical_error(self.process_data[key]['data'][0], mess)


def bangd_relationship(self, key):
    """Bangd relationship"""
    genrelate_statement = getattr(self.alchemy_object['relationship'], "{}_relationship_id".format(self.table_name))
    sub_statement = getattr(self.alchemy_object['relationship'], 'subject_id')
    obj_statement = getattr(self.alchemy_object['relationship'], 'object_id')
    syn_cvterm = get_cvterm(self.session, 'synonym type', 'symbol')
    rel_cvterm = get_cvterm(self.session, self.process_data[key]['rel_cv'], self.process_data[key]['rel_cvterm'])

    if type(self.process_data[key]['data']) is not list:
        data_list = [self.process_data[key]['data']]
    else:
        data_list = self.process_data[key]['data']

    for item in data_list:
        # Lookup the synonym in the relationship with self.chado
        try:
            gensyn = self.session.query(self.alchemy_object['synonym']).\
                join(Synonym).join(Pub).\
                filter(Synonym.name == item[FIELD_VALUE],
                       Pub.uniquename == 'unattributed',
                       Synonym.type_id == syn_cvterm.cvterm_id,
                       self.alchemy_object['synonym'].is_current == 't').one()
        except NoResultFound:
            log.critical(item, "Could not find '{}' in synonym lookup.".format(item[FIELD_VALUE]))
            return
        subject_lookup = False
        if self.process_data[key]['subject']:
            subject_lookup = True
            obj_id = self.chado.primary_id()
            sub_id = gensyn.first_id()
        else:
            sub_id = self.chado.primary_id()
            obj_id = gensyn.first_id()

        genrelate_pubs = self.session.query(self.alchemy_object['relationshippub']).\
            join(self.alchemy_object['relationship']).\
            filter(self.alchemy_object['relationship'].type_id == rel_cvterm.cvterm_id,
                   self.alchemy_object['relationshippub'].pub_id == self.pub.pub_id,
                   sub_statement == sub_id,
                   obj_statement == obj_id)
        count = 0
        for genrelate_pub in genrelate_pubs:
            genrelate_id = genrelate_pub.secondary_id()
            self.session.delete(genrelate_pub)
            count += 1
            if not self.relatepubs_exist(rel_cvterm, subject_lookup):  # No more relationship pubs
                self.session.query(self.alchemy_object['relationship']).\
                    filter(genrelate_statement == genrelate_id).delete()
        if not count:
            mess = "No relationship found for bangd for {} {} and {}".\
                format(self.chado.name, item[FIELD_VALUE], self.pub.uniquename)
            self.critical_error(item, mess)


def delete_relationship(self, key, bangc=False):
    """Delete prop.

    Args:
        key (string): key/field of proforma to get data from.
        bangc (Bool): True if bangc operation.
                      False if a bangd operation.
                      Default is False.
    """

    if bangc:
        self.bangc_relationship(key)
    else:
        self.bangd_relationship(key)
