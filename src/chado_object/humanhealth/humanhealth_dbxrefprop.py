from harvdev_utils.production import (
    HumanhealthDbxref, HumanhealthDbxrefprop, HumanhealthDbxrefpropPub, FeatureHumanhealthDbxref,
    Cvterm, Cv, Db, Dbxref, Feature
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
            params['create_dbxref_allowed'] = True
            params['create_prop_allowed'] = True
        else:
            params['create_dbxref_allowed'] = False
            params['create_prop_allowed'] = False

        hh_dbxref, hh_dbxrefprop = self.get_or_create_dbxrefprop(params)
        if not create and hh_dbxrefprop:
            # testing of the deletion of dbxref removes prop on cascade?
            # self.session.query(HumanhealthDbxrefprop).\
            #    filter(HumanhealthDbxrefprop.humanhealth_dbxref_id == hh_dbxrefprop.humanhealth_dbxref_id).delete()
            self.session.query(HumanhealthDbxref).\
                filter(HumanhealthDbxref.humanhealth_dbxref_id == hh_dbxrefprop.humanhealth_dbxref_id).delete()
    return hh_dbxref, hh_dbxrefprop

def create_set_initial_params(self, set_key, data_set):
    """
    Create initial params to be used for dbxrefprop generation.
    """
    params = {'cvterm': self.process_data[set_key]['cvterm'],
              'cvname': self.process_data[set_key]['cv'],
              'create_dbxref_allowed': True,
              'create_prop_allowed': True}

    db_key = set_key + self.process_data[set_key]['set_db']
    if db_key not in data_set or not data_set[db_key][FIELD_VALUE]:
        error_message = "Set {} does not have {} specified".format(set_key, db_key)
        self.error_track(data_set[db_key], error_message, CRITICAL_ERROR)
        return False
    else:
        params['dbname'] = data_set[db_key][FIELD_VALUE]

    if desc_key in data_set:
        params['description'] = data_set[desc_key][FIELD_VALUE]

    return params


def process_set_dbxrefprop(self, set_key, data_set):
    """
    Create the dbxref and prop, pubs for this data_set.
    set_key: Key for the set i.r. HH5 or HH14
    data_set: One complete set of data. (dictionary)
    """

    valid_key = self.get_valid_key_for_data_set(data_set)
    if not valid_key:
        return

    params = self.create_set_initial_params(set_key, data_set)
    if not params:
        return

    dis_key = set_key + self.process_data[set_key]['set_dis']
    if dis_key in data_set:
        params['bang_c'] = False  # bang_d equivalent remove the one listed
        self.bang_dbxrefprop(params)
        return

    acc_key = set_key + self.process_data[set_key]['set_acc']

    if type(data_set[acc_key]) is not list:
        data_list = []
        data_list.append(data_set[acc_key])
    else:
        data_list = data_set[acc_key]

    for acc_tuple in data_list:
        if not acc_tuple[FIELD_VALUE]:
            error_message = "Set {} does not have {} specified".format(set_key, acc_key)
            self.error_track(acc_tuple, error_message, CRITICAL_ERROR)
        else:
            params['accession'] = acc_tuple[FIELD_VALUE]
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
        create_dbxef_allowed: Wether we are allowed to create a new dbxref
        create_prop_allowed: Wether we are allowed to create new prop
    """

    db = self.session.query(Db).filter(Db.name == params['dbname']).one_or_none()
    if not db:
        error_message = "{} Not found in db table".format(params['dbname'])
        self.error_track(params['tuple'], error_message, CRITICAL_ERROR)
        return None

    dbxref, is_new = get_or_create(self.session, Dbxref, db_id=db.db_id, accession=params['accession'])
    if is_new and not params['create_dbxref_allowed']:
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
    if is_new and not params['create_prop_allowed']:
        error_message = "Prop for Accession {}: Not found in table for db {}".\
            format(params['accession'], params['dbname'])
        self.error_track(params['tuple'], error_message, CRITICAL_ERROR)
        return None
    return hh_dbxref


def get_or_create_dbxrefprop(self, params):
    """
        General rountine for adding humanhealth dbxrefs and their props + pubs
        params should contain:-
        dbname:      db name for dbxref
        accession:   accession for dbxref
        cvname:      cv name for prop
        cvterm:      cvterm name for prop
        description: dbxref description (only used if new dbxref) *Also Optional*
        tuple:       one related tuple to help give better errors
        value:       prop value.
        create_dbxef_allowed: Wether we are allowed to create a new dbxref
        create_prop_allowed: Wether we are allowed to create new prop

        Return dbxref, dbxrefprop
    """
    hh_dbxref = self.process_dbxref(params)

    if not hh_dbxref:
        return None, None

    cvterm = self.session.query(Cvterm).join(Cv).\
        filter(Cv.name == params['cvname'],
               Cvterm.name == params['cvterm']).\
        one_or_none()
    if not cvterm:
        log.critical("cvterm {} with cv of {} failed lookup".format(params['cvterm'], params['cvname']))
        return None, None

    hhdp, is_new = get_or_create(self.session, HumanhealthDbxrefprop,
                                 humanhealth_dbxref_id=hh_dbxref.humanhealth_dbxref_id,
                                 type_id=cvterm.cvterm_id)
    if is_new and not params['create_prop_allowed']:
        # eror message
        return None, None
    log.debug("Create pub for hdp {}".format(hhdp.humanhealth_dbxrefprop_id))
    hhdpp, is_new = get_or_create(self.session, HumanhealthDbxrefpropPub,
                                  humanhealth_dbxrefprop_id=hhdp.humanhealth_dbxrefprop_id,
                                  pub_id=self.pub.pub_id)
    if 'value' in params and params['value'] != '':
        hhdp.value = params['value']

    return hh_dbxref, hhdp


def process_hh7_e_and_f(self, set_key, data_set, params):
    """
    Process hh7 e and f.
     need to create params for get_or_create_dbxrefprop
        dbname:      db name for dbxref
        accession:   accession for dbxref
        cvname:      cv name for prop
        cvterm:      cvterm name for prop
        description: dbxref description (only used if new dbxref) *Also Optional*
        tuple:       one related tuple to help give better errors
        value:       prop value
        create_dbxef_allowed: Wether we are allowed to create a new dbxref
        create_prop_allowed: Wether we are allowed to create new prop
    """
    dis_key = set_key + 'f'
    if dis_key in data_set and data_set[dis_key] != '':
        log.critical("NOT done dissociate yet")
        return False

    db_acc_key = set_key + 'e'
    params['cvterm'] = self.process_data[set_key]['e_cvterm']
    params['cvname'] = self.process_data[set_key]['e_cv']
    params['tuple'] = data_set[db_acc_key]
    try:
        fields = params['tuple'][FIELD_VALUE].split(':')
        params['dbname'] = fields[0].strip()
        params['accession'] = fields[1].strip()
    except IndexError:
        error_message = "{} Not in the corect format of dbname:accession".format(params['tuple'][FIELD_VALUE])
        self.error_track(params['tuple'], error_message, CRITICAL_ERROR)
        return False

    hh_dbxref, hh_dbxrefprop = self.get_or_create_dbxrefprop(params)
    return True


def process_hh7_c_and_d(self, set_key, data_set, params):
    """
    Process hh7 c and d.
     need to create params for get_or_create_dbxrefprop
        dbname:      db name for dbxref
        accession:   accession for dbxref
        cvname:      cv name for prop
        cvterm:      cvterm name for prop
        description: dbxref description (only used if new dbxref) *Also Optional*
        tuple:       one related tuple to help give better errors
        value:       prop value
        create_dbxef_allowed: Wether we are allowed to create a new dbxref
        create_prop_allowed: Wether we are allowed to create new prop
    """

    for char_key in ('c', 'd'):
        sub_key = set_key + char_key
        params['cvterm'] = self.process_data[set_key]['{}_cvterm'.format(char_key)]
        params['cvname'] = self.process_data[set_key]['{}_cv'.format(char_key)]
        if sub_key not in data_set:
            continue
        for item in data_set[sub_key]:
            params['tuple'] = item
            if char_key == 'c':
                params['value'] = item[FIELD_VALUE]
            else:
                params['value'] = ''
            hh_dbxref, hh_dbxrefprop = self.get_or_create_dbxrefprop(params)
            if char_key == 'd':  # Add feature_hh_dbxref
                feature = self.session.query(Feature).\
                              filter(Feature.name == params['tuple'][FIELD_VALUE],
                                     Feature.uniquename.like("FBgn%")).one_or_none()
                if not feature:
                    error_message = "Name {} not found in feature table with unique name starting with FBgn".\
                        format(params['name'])
                    self.error_track(params['tuple'], error_message, CRITICAL_ERROR)
                else:
                    f_hh_dbxref, _ = get_or_create(self.session, FeatureHumanhealthDbxref,
                                                   feature_id=feature.feature_id,
                                                   humanhealth_dbxref_id=hh_dbxref.humanhealth_dbxref_id,
                                                   pub_id=self.pub.pub_id)


def process_dbxref_link_item(self, set_key, data_set):
    """
    Add hh_dbxref for HH7e and then add hh_dbxrefprops for
    """
    valid_key = None  # need a valid key incase something is wrong to report line number etc
    for key in data_set.keys():
        if type(data_set[key]) is list:
            if data_set[key][0][FIELD_VALUE]:
                valid_key = 1
        elif data_set[key][FIELD_VALUE]:
            valid_key = key
    if not valid_key:  # Whole thing is blank so ignore. This is okay
        return

    params = {'create_dbxref_allowed': True,
              'create_prop_allowed': True}

    if self.process_hh7_e_and_f(set_key, data_set, params):
        self.process_hh7_c_and_d(set_key, data_set, params)


def process_hh7(self, set_key):
    """
    Load HH7 sets c,d, e and f only. (a,b) NOT part of set.
    """

    for data_set in self.set_values[set_key]:
        self.process_dbxref_link_item(set_key, data_set)


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


############################################################################
# Deletion rountines
############################################################################


def delete_specific_dbxrefprop(self, key):
    """
    Delete a specific hh_dbxrefprop from a bang_d.
    """
    params = {'cvterm' = self.process_data[key]['cvterm'],
              'cvname' = self.process_data[key]['cvname'],
              'bang_c' = bangc,
              'key' = key}
    if not self.add_db_accession(params, key):
        return

    params['create_dbxref_allowed'] = False
    params['create_prop_allowed'] = False

    hh_dbxref, hh_dbxrefprop = self.get_or_create_dbxrefprop(params)
    if not create and hh_dbxrefprop:
        hh_dbxrefprop.delete()

def delete_set_dbxrefprop(self, key):
    pass

def delete_hh_dbxref_props(self, params):
    """
    Delete all hh_dbxrefprop for a particular cvterm.
    pub and hh referenced by self. 
    params:-
      cvterm: cvterm name for prop
      cvname: cv name for prop
    """
    cvterm = self.session.query(Cvterm).join(Cv).\
    filter(Cv.name == params['cvname'],
           Cvterm.name == params['cvterm']).one_or_none()
    if not cvterm:
        log.critical("cvterm {} with cv of {} failed lookup".format(params['cvterm'], params['cvname']))
        return None

    # Remove all hh_dbxrefprop for this cvterm, hh and pub.
        self.session.query(HumanhealthDbxrefprop).join(HumanhealthDbxrefpropPub).\
            .join(HumanhealthDbxref).join(Humanhealth).\
            filter(HumanhealthDbxrefpropPub.humanhealth_dbxrefprop_id == HumanhealthDbxrefprop.humanhealth_dbxrefprop_id,
                   HumanhealthDbxrefprop.humanhealth_dbxref_id == HumanhealthDbxref.humanhealth_dbxref_id,
                   HumanhealthDbxref.humanhealth_id == Humanhealth.humanhealth_id,
                   HumanhealthDbxrefprop.type_id == cvterm.cvterm_id,
                   Humanhealth.humanhealth_id = self.humanhealth.humanhealth_id,
                   HumanhealthDbxrefpropPub.pub_id == self.pub.pub_id).delete()


def bang_dbxrefprop(self, params):
    """
    Delete dbxref and its prop.
    params:-
      cvterm: cvterm name for prop
      cvname: cv name for prop
      dbname: db name
      accession: db accession
      bang_c: True if bang_c operation else its a bang_d
      key:    proforma key to get dbxref value from if bang_d
    """
    if params['bang_c']:
        self.add_db_accession(params, key):
        self.delete_hh_dbxref_props(params)
    else:
        self.delete_specific_dbxrefprop(key)
        self.process_data[key]['data'] = None  # Remove data so that it is not re-added.
