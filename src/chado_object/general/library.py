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
