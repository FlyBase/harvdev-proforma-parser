"""
:synopsis: Synonym functions wrt general.

:moduleauthor: Ian Longden <ianlongden@morgan.harvard.edu>
"""
from chado_object.chado_base import FIELD_VALUE
from harvdev_utils.chado_functions import get_or_create, get_cvterm
from harvdev_utils.char_conversions import sgml_to_plain_text
from harvdev_utils.char_conversions import sub_sup_to_sgml
from harvdev_utils.char_conversions import sgml_to_unicode
from harvdev_utils.chado_functions import CodingError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import logging
from harvdev_utils.production import Synonym, Pub

log = logging.getLogger(__name__)


def synonym_lookup(self, cvterm):
    """filter for synonym lookup

    Args:
        cvterm (cvterm object): type of synonym to look up
    """
    id_statement = getattr(self.alchemy_object['synonym'], self.primary_key_name())
    cur_statement = getattr(self.alchemy_object['synonym'], 'is_current')
    gs = self.session.query(self.alchemy_object['synonym']).join(Synonym).\
        filter(id_statement == self.chado.primary_id(),
               Synonym.type_id == cvterm.cvterm_id,
               cur_statement == 't')
    return gs


def load_synonym(self, key):
    """Load Synonym.

    yml options:
        cv:
        cvterm:
       is_current:
       remove_old: <optional> defaults to False
    NOTE:
      If is_current set to True and cvterm is symbol thensgml to plaintext is done.

    Args:
        key (string): key/field of proforma to add synonym for.
    """
    if not self.has_data(key):
        return
    cv_name = self.process_data[key]['cv']
    cvterm_name = self.process_data[key]['cvterm']
    is_current = self.process_data[key]['is_current']
    if 'check_old_synonym' in self.process_data[key] and self.has_data(self.process_data[key]['check_old_synonym']):
        self.check_old_synonym(self.process_data[key]['check_old_synonym'])

    pubs = self.get_pubs(key)

    # remove the current symbol if is_current is set and yaml says remove old is_current
    # exccept if over rule is passed.        if 'remove_old' in self.process_data[key] and self.process_data[key]['remove_old']:
    if is_current:
        self.remove_current_symbol(key)

    # add the new synonym
    if type(self.process_data[key]['data']) is list:
        items = self.process_data[key]['data']
    else:
        items = [self.process_data[key]['data']]

    for item in items:
        fs = False
        for pub_id in pubs:
            fs = self.add_by_synonym_name_and_type(key, item[FIELD_VALUE], cv_name, cvterm_name, pub_id)
            if is_current and cvterm_name == 'symbol':
                self.chado.name = sgml_to_plain_text(item[FIELD_VALUE])
            fs.is_current = is_current


def add_by_synonym_name_and_type(self, key, synonym_name, cv_name, cvterm_name, pub_id):
    """Add synonym.

    Args:
        key (string): proforma field/key.
       synonym_name (string): name of the synonym to add
       cv_name (string): name of the synonyms cv (usually 'synonym type')
        cvterm_name (string): name of the synonym (i.e. 'symbol' or 'fullname')
       pub_id (int): pub primary key id.
    """
    cvterm = get_cvterm(self.session, cv_name, cvterm_name)

    if not cvterm:
        raise CodingError("HarvdevError: Could not find cvterm '{}' for cv {}".format(cvterm_name, cv_name))
    synonym_sgml = None
    if self.is_subscript_convert(key):
        synonym_sgml = sgml_to_unicode(synonym_name)

    # Then get_create the synonym
    if not synonym_sgml:
        synonym_sgml = sgml_to_unicode(sub_sup_to_sgml(synonym_name))
    synonym_name = sgml_to_plain_text(synonym_name)
    synonym, _ = get_or_create(self.session, Synonym, type_id=cvterm.cvterm_id, name=synonym_name, synonym_sgml=synonym_sgml)
    if not synonym:
        raise CodingError("HarvdevError: Could not create synonym")
    opts = {'{}'.format(self.primary_key_name()): self.chado.primary_id(),
            'synonym_id': synonym.synonym_id,
            'pub_id': pub_id}
    gs, is_new = get_or_create(self.session, self.alchemy_object['synonym'], **opts)
    return gs


def check_old_synonym(self, key):
    """Check current synonyms match.

    Args:
        key (string): proforma field/key.
    """
    cv_name = self.process_data[key]['cv']
    cvterm_name = self.process_data[key]['cvterm']
    cvterm = get_cvterm(self.session, cv_name, cvterm_name)

    old_syn = self.process_data[key]['data'][FIELD_VALUE]
    gss = self.synonym_lookup(cvterm)
    if gss[0].synonym.name != old_syn:
        mess = "current {} synonym {} does not equal {}".format(cvterm.name, gss[0].synonym.name, old_syn)
        self.critical_error(self.process_data[key]['data'], mess)


def remove_current_symbol(self, key):
    """Remove is_current for this feature_synonym.

    Make the current symbol for this feature is_current=False.
    Usually done when assigning a new symbol we want to set the old one
    to is_current = False and not to delete it.

    Args:
        key (string): key/field of proforma to get data from.
    Raises:
        CodingError: cv/cvterm lookup fails. unable to get synonym type.
    """
    cv_name = self.process_data[key]['cv']
    cvterm_name = self.process_data[key]['cvterm']
    cvterm = get_cvterm(self.session, cv_name, cvterm_name)
    if not cvterm:
        raise CodingError("HarvdevError: Could not find cvterm '{}' for cv {}".format(cvterm_name, cv_name))

    try:
        fss = self.synonym_lookup(cvterm)
        for fs in fss:
            fs.is_current = False
    except MultipleResultsFound:
        log.error("More than one result for BLAH id = {}".format(self.chado.primary_id()))
        fss = self.session.query(self.alchemy_object['synonym']).join(Synonym).\
            filter(self.alchemy_object['synonym'].feature_id == self.chado.primary_id(),
                   Synonym.type_id == cvterm.cvterm_id,
                   self.alchemy_object['synonym'].is_current == 't')
        for fs in fss:
            log.error(fs)
        raise MultipleResultsFound
    except NoResultFound:
        return


def delete_synonym(self, key, bangc=False):
    """Delete synonym.

    Args:
        key (string): key/field of proforma to get data from.
        bangc (Bool): True if bangc operation.
                      False if a bangd operation.
                      Default is False.
    """
    if type(self.process_data[key]['data']) is not list:
        data_list = []
        data_list.append(self.process_data[key]['data'])
    else:
        data_list = self.process_data[key]['data']

    cv_name = self.process_data[key]['cv']
    cvterm_name = self.process_data[key]['cvterm']
    cvterm = get_cvterm(self.session, cv_name, cvterm_name)
    if not cvterm:
        message = "Unable to find cvterm {} for Cv {}.".format(cvterm_name, cv_name)
        self.critical_error(self.process_data[key]['data'], message)
        return None

    id_statement = getattr(self.alchemy_object['synonym'], self.primary_key_name())
    if bangc:
        gss = self.session.query(self.alchemy_object['synonym']).join(Synonym).join(Pub).\
            filter(id_statement == self.chado.primary_id(),
                   Synonym.type_id == cvterm.cvterm_id,
                   Pub.pub_id == self.pub.pub_id)
        for gs in gss:
            self.session.delete(gs)
    else:
        for data in data_list:
            synonyms = self.session.query(Synonym).\
                filter(Synonym.name == sgml_to_plain_text(data[FIELD_VALUE]),
                       Synonym.type_id == cvterm.cvterm_id)
            syn_count = 0
            f_syn_count = 0
            for syn in synonyms:
                syn_count += 1
                f_syns = self.session.query(self.alchemy_object['synonym']).\
                    filter(id_statement == self.chado.primary_id(),
                           self.alchemy_object['synonym'].synonym_id == syn.synonym_id,
                           self.alchemy_object['synonym'].pub_id == self.pub.pub_id)
                for f_syn in f_syns:
                    f_syn_count += 1
                    self.session.delete(f_syn)

            if not syn_count:
                self.critical_error(data, "Synonym '{}' of type '{}' Does not exist.".format(data[FIELD_VALUE], cvterm.name))
                continue
            elif not f_syn_count:
                self.critical_error(data, 'Synonym {} Does not exist for this Feature that is not current.'.format(data[FIELD_VALUE]))
                continue
