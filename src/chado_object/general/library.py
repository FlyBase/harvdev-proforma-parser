"""
:synopsis: Library functions wrt general.

:moduleauthor: Ian Longden <ianlongden@morgan.harvard.edu>
"""
from chado_object.chado_base import FIELD_VALUE
from harvdev_utils.chado_functions import get_or_create, get_cvterm
from harvdev_utils.production import Library, LibrarySynonym, Synonym, Pub
from sqlalchemy.orm.exc import NoResultFound
import logging

log = logging.getLogger(__name__)


def load_library(self, key):
    """Load general to library."""
    if type(self.process_data[key]['data']) is list:
        items = self.process_data[key]['data']
    else:
        items = [self.process_data[key]['data']]

    syn_cvterm = get_cvterm(self.session, 'synonym type', 'symbol')
    prop_cvterm = None
    if 'cv' in self.process_data[key] and 'cvterm' in self.process_data[key]:  # we have cvterm for the prop
        try:
            prop_cvterm = get_cvterm(self.session, self.process_data[key]['cv'], self.process_data[key]['cvterm'])
        except NoResultFound:
            mess = "Lookup failed to find get cv term for cv '{}' cvterm '{}'".format(self.process_data[key]['cv'], self.process_data[key]['cvterm'])
            self.critical_error(items[0], mess)
            return
    for item in items:
        # lookup by symbol
        try:
            library = self.session.query(Library).\
                join(LibrarySynonym).\
                join(Synonym).join(Pub).\
                filter(Synonym.name == item[FIELD_VALUE],
                       # Pub.uniquename == 'unattributed',
                       Synonym.type_id == syn_cvterm.cvterm_id,
                       self.alchemy_object['synonym'].is_current == 't').one()
        except NoResultFound:
            self.critical_error(item, "Could not find '{}' in synonym lookup.".format(item[FIELD_VALUE]))
            return

        opts = {'{}_id'.format(self.table_name): self.chado.primary_id(),
                'library_id': library.library_id,
                'pub_id': self.pub.pub_id}
        gen_lib, _ = get_or_create(self.session,  self.alchemy_object['library'], **opts)
        # now generate the prop if we have cv and cvterms defined for this.
        if prop_cvterm:
            opts = {'{}_library_id'.format(self.table_name): gen_lib.primary_id(),
                    'type_id': prop_cvterm.cvterm_id}
            get_or_create(self.session,  self.alchemy_object['libraryprop'], **opts)


def bangc_library(self, key):
    """Bangc library"""
    id_statement = getattr(self.alchemy_object['library'], self.primary_key_name())
    count = 0
    g_libs = self.session.query(self.alchemy_object['library']).\
        join(Pub, self.alchemy_object['library'].pub_id == Pub.pub_id).\
        filter(id_statement == self.chado.primary_id(),
               Pub.pub_id == self.pub.pub_id)
    for g_lib in g_libs:
        count += 1
        self.session.delete(g_lib)
    if not count:  # Nothing got deleted!!!
        mess = "!c produced no deletions for cell line {} and pub {}".\
            format(self.chado.name, self.pub.uniquename)
        if type(self.process_data[key]['data']) is not list:
            self.critical_error(self.process_data[key]['data'], mess)
        else:
            self.critical_error(self.process_data[key]['data'][0], mess)


def bangd_library(self, key):
    """Bangd library"""
    id_statement = getattr(self.alchemy_object['library'], self.primary_key_name())
    syn_cvterm = get_cvterm(self.session, 'synonym type', 'symbol')
    if type(self.process_data[key]['data']) is not list:
        data_list = [self.process_data[key]['data']]
    else:
        data_list = self.process_data[key]['data']

    for item in data_list:
        # get the specific cvterm, it could be go which needs extra checks
        try:
            library = self.session.query(Library).\
                join(LibrarySynonym).\
                join(Synonym).join(Pub).\
                filter(Synonym.name == item[FIELD_VALUE],
                       # Pub.uniquename == 'unattributed',
                       Synonym.type_id == syn_cvterm.cvterm_id,
                       self.alchemy_object['synonym'].is_current == 't').one()
        except NoResultFound:
            self.critical_error(item, "Could not find '{}' in synonym lookup.".format(item[FIELD_VALUE]))
            return
        g_libs = self.session.query(self.alchemy_object['library']).join(Library).join(Pub).\
            filter(id_statement == self.chado.primary_id(),
                   Library.library_id == library.library_id,
                   Pub.pub_id == self.pub.pub_id)
        count = 0
        for g_lib in g_libs:
            count += 1
            self.session.delete(g_lib)
        if not count:  # Nothing got deleted!!!
            mess = "Could not !d library '{}'. It did not exist for '{}' with this pub '{}'.".\
                format(library.name, self.chado.name, self.pub.uniquename)
            self.critical_error(item, mess)


def delete_library(self, key, bangc=False):
    """Delete library.

    Args:
        key (string): key/field of proforma to get data from.
        bangc (Bool): True if bangc operation.
                      False if a bangd operation.
                      Default is False.
    """
    if bangc:
        self.bangc_library(key)
    else:
        self.bangd_library(key)
