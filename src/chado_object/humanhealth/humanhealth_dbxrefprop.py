from harvdev_utils.production import (
    HumanhealthDbxref, HumanhealthDbxrefprop,
    Cvterm, Cv, Db, Dbxref
)
import logging
from ..chado_base import FIELD_VALUE
from error.error_tracking import CRITICAL_ERROR
from harvdev_utils.chado_functions import get_or_create

log = logging.getLogger(__name__)


def process_dbxrefprop(self, key, create=True):
    """
    delete or add hh_dbxrefprop
    Delete and create are similar in processing data to get params
    so code share and call appropriate function after generation of params.
    """
    log.debug("key = {}".format(key))
    log.debug("cv is {}, cvterm is {}".format(self.process_data[key]['cv'], self.process_data[key]['cvterm']))
    params = {'cvterm': self.process_data[key]['cvterm'],
              'cvname': self.process_data[key]['cv']}
    # can be a list or single, so make them all a list to save code dupliction
    if type(self.process_data[key]['data']) is not list:
        data_list = []
        data_list.append(self.process_data[key]['data'])
    else:
        data_list = self.process_data[key]['data']

    for item in data_list:
        log.debug("{}: {} {}".format(key, item, type(item)))
        params['tuple'] = item
        if 'db' in self.process_data[key]:
            params['dbname'] = self.process_data[key]['db']
            params['accession'] = item[FIELD_VALUE]
        else:
            try:
                fields = item[FIELD_VALUE].split(':')
                params['dbname'] = fields[0].strip()
                params['accession'] = fields[1].strip()
            except IndexError:
                error_message = "{} Not in the corect format of dbname:accession".format(item[FIELD_VALUE])
                self.error_track(params['tuple'], error_message, CRITICAL_ERROR)
                continue

        if create:
            params['create_allowed'] = True
        else:
            params['create_allowed'] = False
        hh_dbxrefprop = self.get_or_create_dbxrefprop(params)
        if not create and hh_dbxrefprop:
            # testing of the deletion of dbxref removes prop on cascade?
            # self.session.query(HumanhealthDbxrefprop).\
            #    filter(HumanhealthDbxrefprop.humanhealth_dbxref_id == hh_dbxrefprop.humanhealth_dbxref_id).delete()
            self.session.query(HumanhealthDbxref).\
                filter(HumanhealthDbxref.humanhealth_dbxref_id == hh_dbxrefprop.humanhealth_dbxref_id).delete()


def process_set_dbxrefprop(self, set_key, data_set):
    valid_set = True
    valid_key = None  # need a valid key incase something is wrong to report line number etc

    params = {'cvterm': self.process_data[set_key]['cvterm'],
              'cvname': self.process_data[set_key]['cv'],
              'create_allowed': True}
    acc_key = set_key + self.process_data[set_key]['set_acc']
    db_key = set_key + self.process_data[set_key]['set_db']
    desc_key = set_key + self.process_data[set_key]['set_desc']
    # dis_key = key + postfix['dis']
    for key in data_set.keys():
        if data_set[key][FIELD_VALUE]:
            valid_key = key
    if not valid_key:  # Whole thing is blank so ignore. This is okay
        return
    if acc_key not in data_set or not data_set[acc_key][FIELD_VALUE]:
        valid_set = False
        error_message = "Set {} does not have {} specified".format(set_key, acc_key)
        self.error_track(data_set[valid_key], error_message, CRITICAL_ERROR)
    else:
        params['accession'] = data_set[acc_key][FIELD_VALUE]
    if db_key not in data_set or not data_set[db_key][FIELD_VALUE]:
        valid_set = False
        error_message = "Set {} does not have {} specified".format(set_key, db_key)
        self.error_track(data_set[valid_key], error_message, CRITICAL_ERROR)
    else:
        params['dbname'] = data_set[db_key][FIELD_VALUE]
    if desc_key in data_set:
        params['description'] = data_set[desc_key][FIELD_VALUE]
    if valid_set:
        params['tuple'] = data_set[valid_key]
        self.get_or_create_dbxrefprop(params)


def process_data_link(self, set_key):
    """
    set_key: Key to process i.e HH5 or HH14

    TODO: disassociation 'd' still needs to be coded.
    """
    for data_set in self.set_values[set_key]:
        if self.process_data[set_key]['sub_type'] == 'dbxrefprop':
            self.process_set_dbxrefprop(set_key, data_set)
        else:
            log.critical("sub_type for this data set unknown")


def process_dbxref(self, params):
    """
    General rountine for adding humanhealth dbxrefs.
    params should contain:-
        dbname:      db name for dbxref
        accession:   accession for dbxref
        tuple:       one related tuple to help give better errors
    """

    db = self.session.query(Db).filter(Db.name == params['dbname']).one_or_none()
    if not db:
        error_message = "{} Not found in db table".format(params['dbname'])
        self.error_track(params['tuple'], error_message, CRITICAL_ERROR)
        return None

    dbxref, is_new = get_or_create(self.session, Dbxref, db_id=db.db_id, accession=params['accession'])
    if is_new and not params['create_allowed']:
        error_message = "Accession {}: Not found in table for db {}".\
            format(params['accession'], params['dbname'])
        self.error_track(params['tuple'], error_message, CRITICAL_ERROR)
        return None
    if is_new:
        if 'description' in params:
            dbxref.description = params['description']

    hh_dbxref, is_new = get_or_create(self.session, HumanhealthDbxref,
                                      dbxref_id=dbxref.dbxref_id,
                                      humanhealth_id=self.humanhealth.humanhealth_id)
    if is_new and not params['create_allowed']:
        error_message = "Prop for Accession {}: Not found in table for db {}".\
            format(params['accession'], params['dbname'])
        self.error_track(params['tuple'], error_message, CRITICAL_ERROR)
        return None
    return hh_dbxref


def get_or_create_dbxrefprop(self, params):
    """
        General rountine for adding humanhealth dbxrefs and their props
        params should contain:-
        dbname:      db name for dbxref
        accession:   accession for dbxref
        cvname:      cv name for prop
        cvterm:      cvterm name for prop
        description: dbxref description (only used if new dbxref) *Also Optional*
        tuple:       one related tuple to help give better errors
        create_allowed: Wether we are allowed to create new prop

        Return dbxrefprop
    """
    hh_dbxref = self.process_dbxref(params)

    if not hh_dbxref:
        return None

    cvterm = self.session.query(Cvterm).join(Cv).\
        filter(Cv.name == params['cvname'],
               Cvterm.name == params['cvterm']).\
        one_or_none()
    if not cvterm:
        log.critical("cvterm {} with cv of {} failed lookup".format(params['cvterm'], params['cvname']))
        return None

    hhdp, is_new = get_or_create(self.session, HumanhealthDbxrefprop,
                                 humanhealth_dbxref_id=hh_dbxref.humanhealth_dbxref_id,
                                 type_id=cvterm.cvterm_id)
    if is_new and not params['create_allowed']:
        # eror message
        return None
    return hhdp


def load_dbxrefprop(self, key):
    """
    load the hh_dbxref and hh_dbxrefprop.

    If db not in yml file then the format must be dbname:accession
    Else just the accession
    """
    # If this is to be deleted rather than created by then return
    if 'not_if_defined' in self.process_data[key]:
        check_key = self.process_data[key]['not_if_defined']
        if check_key in self.process_data:
            return

    self.process_dbxrefprop(key, create=True)


def delete_dbxrefprop(self, key, bangc=True):
    """
    Delete dbxref and its prop.
    """
    if bangc:
        cvterm = self.session.query(Cvterm).join(Cv).\
            filter(Cv.name == self.process_data[key]['cvname'],
                   Cvterm.name == self.process_data[key]['cvterm']).one_or_none()
        if not cvterm:
            log.critical("cvterm {} with cv of {} failed lookup".format(self.process_data[key]['cvterm'], self.process_data[key]['cvname']))
            return None

        self.session.query(HumanhealthDbxref).join(HumanhealthDbxrefprop).\
            filter(HumanhealthDbxrefprop.type_id == cvterm.cvterm_id,
                   HumanhealthDbxref.humanhealth_dbxref_id == HumanhealthDbxrefprop.humanhealth_dbxref_id,
                   HumanhealthDbxref.humanhealth_id == self.humanhealth.humanhealth_id).delete()
    else:
        self.process_dbxrefprop(key, create=False)