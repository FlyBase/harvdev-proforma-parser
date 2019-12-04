from harvdev_utils.production import (
    HumanhealthDbxref, HumanhealthDbxrefprop, HumanhealthDbxrefpropPub, Humanhealth,
    FeatureHumanhealthDbxref, Cvterm, Cv, Db, Dbxref, Feature
)
import logging
from ..chado_base import FIELD_VALUE, SET_BANG
from harvdev_utils.chado_functions import get_or_create
# from harvdev_utils.chado_functions.external_lookups import ExternalLookup
from error.error_tracking import CRITICAL_ERROR
log = logging.getLogger(__name__)


def process_dbxrefprop(self, key):
    """
    Add hh_dbxrefprop
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
                error_message = "{} Not in the correct format of dbname:accession".format(item[FIELD_VALUE])
                self.error_track(params['tuple'], error_message, CRITICAL_ERROR)
                continue
        hh_dbxref, hh_dbxrefprop = self.get_or_create_dbxrefprop(params)
    return hh_dbxref, hh_dbxrefprop


def create_set_initial_params(self, set_key, data_set):
    """
    Create initial params to be used for dbxrefprop generation.
    """
    params = {'cvterm': self.process_data[set_key]['cvterm'],
              'cvname': self.process_data[set_key]['cv']}

    db_key = set_key + self.process_data[set_key]['set_db']
    if db_key not in data_set:
        acc_key = set_key + self.process_data[set_key]['set_acc']
        if acc_key in data_set:
            error_message = "Set {} does not have {} specified".format(set_key, db_key)
            self.error_track(data_set[acc_key], error_message, CRITICAL_ERROR)
            return False
    elif db_key not in data_set or not data_set[db_key][FIELD_VALUE]:
        error_message = "Set {} does not have {} specified".format(set_key, db_key)
        self.error_track(data_set[db_key], error_message, CRITICAL_ERROR)
        return False
    else:
        params['dbname'] = data_set[db_key][FIELD_VALUE]

    desc_key = set_key + self.process_data[set_key]['set_desc']
    if desc_key in data_set:
        params['description'] = data_set[desc_key][FIELD_VALUE]

    return params


def process_set_dbxrefprop(self, set_key, data_set):
    """
    Create/Dissociate the dbxref and prop, pubs for this data_set.
    set_key: Key for the set i.r. HH5 or HH14
    data_set: One complete set of data. (dictionary)
    """

    valid_key = self.get_valid_key_for_data_set(data_set)
    if not valid_key:
        return

    params = self.create_set_initial_params(set_key, data_set)
    if not params:
        return

    acc_key = set_key + self.process_data[set_key]['set_acc']
    if acc_key not in data_set:
        error_message = "Set {} does not have {} specified".format(set_key, acc_key)
        self.error_track(data_set[valid_key], error_message, CRITICAL_ERROR)
        return
    if not data_set[acc_key][FIELD_VALUE]:
        error_message = "Set {} does not have {} specified".format(set_key, acc_key)
        self.error_track(data_set[acc_key], error_message, CRITICAL_ERROR)
        return
    else:
        params['accession'] = data_set[acc_key][FIELD_VALUE]

    dis_key = set_key + self.process_data[set_key]['set_dis']
    if dis_key in data_set and data_set[dis_key][FIELD_VALUE] == 'y':
        log.debug("dis_key is set so delete stuff")
        params['tuple'] = data_set[acc_key]
        self.bangd_dbxref(params)
        return
    else:
        log.debug("Dis key NOT set so create stuff")

    params['tuple'] = data_set[acc_key]
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
    dbxref, is_new = self.get_or_create_dbxref(params)
    if not dbxref:
        return None

    if is_new:
        if 'description' in params:
            dbxref.description = params['description']

    hh_dbxref, is_new = get_or_create(self.session, HumanhealthDbxref,
                                      dbxref_id=dbxref.dbxref_id,
                                      humanhealth_id=self.humanhealth.humanhealth_id)

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
    """

    db_acc_key = set_key + 'e'
    dis_key = set_key + 'f'

    if db_acc_key not in data_set:
        return False

    params['cvterm'] = self.process_data[set_key]['e_cvterm']
    params['cvname'] = self.process_data[set_key]['e_cv']
    params['tuple'] = data_set[db_acc_key]
    try:
        fields = params['tuple'][FIELD_VALUE].split(':')
        params['dbname'] = fields[0].strip()
        params['accession'] = fields[1].strip()
    except IndexError:
        error_message = "{} Not in the correct format of dbname:accession".format(params['tuple'][FIELD_VALUE])
        self.error_track(params['tuple'], error_message, CRITICAL_ERROR)
        return False

    dis_key = set_key + 'f'
    if dis_key in data_set and data_set[dis_key][FIELD_VALUE] == 'y':
        self.bangd_dbxref(params)
        return False

    hh_dbxref, hh_dbxrefprop = self.get_or_create_dbxrefprop(params)
    return True


def process_hh7_c_and_d(self, set_key, data_set, params):  # noqa: C901
    """
    Process hh7 c and d.
      params already defined
        dbname:      db name for dbxref
        accession:   accession for dbxref
      need to create params for get_or_create_dbxrefprop
        cvname:      cv name for prop
        cvterm:      cvterm name for prop
        description: dbxref description (only used if new dbxref) *Also Optional*
        tuple:       one related tuple to help give better errors
        value:       prop value
    """
    for char_key in ('c', 'd'):
        sub_key = set_key + char_key
        params['cvterm'] = self.process_data[set_key]['{}_cvterm'.format(char_key)]
        params['cvname'] = self.process_data[set_key]['{}_cv'.format(char_key)]
        if sub_key not in data_set:
            continue
        for item in data_set[sub_key]:
            params['tuple'] = item
            if item and item[SET_BANG]:
                params['bang_type'] = item[SET_BANG]
                self.bang_dbxrefprop_only(params)
                log.debug("Bang for {} is set too {}".format(sub_key, item[SET_BANG]))
                if char_key == 'd':
                    self.bang_feature_hh_dbxref(params)
                if item[SET_BANG] == 'd':
                    continue
            if not item or not item[FIELD_VALUE]:
                continue
            if char_key == 'c':
                params['value'] = item[FIELD_VALUE]
            else:
                params['value'] = ''
            hh_dbxref, hh_dbxrefprop = self.get_or_create_dbxrefprop(params)

            if char_key == 'd' and hh_dbxref:  # Add feature_hh_dbxref
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
    params = {}
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
    if self.process_data[key]['data']:
        log.debug("Loading {}: {}".format(key, self.process_data[key]['data']))
        self.process_dbxrefprop(key)


############################################################################
# Deletion rountines
# For humanhealth_dbxref we do not care what the pub or props are we just
# want to dissociate the whole thing.
# If we delete the hh_dbxref then casding will deal with the rest.
############################################################################

def delete_dbxref(self, key, bangc):
    """
    General first call from
    """
    params = {'cvterm': self.process_data[key]['cvterm'],
              'cvname': self.process_data[key]['cv']}
    if 'db' in self.process_data[key]:
        params['dbname'] = self.process_data[key]['db']
    log.debug("Bangc is {}: {} {}".format(bangc, params['cvterm'], params['dbname']))
    if bangc:
        self.bangc_dbxref(params)
    else:
        if type(self.process_data[key]['data']) is not list:
            data_list = []
            data_list.append(self.process_data[key]['data'])
        else:
            data_list = self.process_data[key]['data']

        for item in data_list:
            log.debug("{}: {} {}".format(key, item, type(item)))
            params['tuple'] = item
            params['accession'] = item[FIELD_VALUE]
            self.bangd_dbxref(params)
            self.process_data[key]['data'] = None


def bangd_dbxref(self, params):
    """
    Params needed are:-
    'dbname' and 'accession': to get the dbxref.
    'tuple': to allow reporting of problems
    humanhealth obtained from self.
    """
    dbxref = self.session.query(Dbxref).join(Db).\
        filter(Dbxref.db_id == Db.db_id,
               Db.name == params['dbname'],
               Dbxref.accession == params['accession']).one_or_none()
    if not dbxref:
        error_message = "Could not found accession {} in dbxref table for db {}".format(params['accession'], params['dbname'])
        self.error_track(params['tuple'], error_message, CRITICAL_ERROR)
        return None

    self.session.query(HumanhealthDbxref).\
        filter(HumanhealthDbxref.humanhealth_id == self.humanhealth.humanhealth_id,
               HumanhealthDbxref.dbxref_id == dbxref.dbxref_id).delete()


def bangc_dbxref(self, params):
    """
    Params needed are:-
    'cvterm', 'cv': to get cvterm of those to remove
    'dbname': to get the db type. *Optional else remove all dbnames*.
    'tuple': to allow reporting of problems
    humanhealth obtained from self.

    So for this humanhealth and cvterm remove all hh_dbxrefs.
    Dbxrefs given by links to cvterms and possibly db's.
    The cvterm is defined in the hh_dbxref_prop.
    """

    # get cvterm
    cvterm = self.session.query(Cvterm).join(Cv).\
        filter(Cv.name == params['cvname'],
               Cvterm.name == params['cvterm']).\
        one_or_none()
    if not cvterm:
        log.critical("cvterm {} with cv of {} failed lookup".format(params['cvterm'], params['cvname']))
        return

    if 'dbname' in params:
        db = self.session.query(Db).filter(Db.name == params['dbname']).one_or_none()
        if not db:
            error_message = "{} Not found in db table".format(params['dbname'])
            self.error_track(params['tuple'], error_message, CRITICAL_ERROR)
            return None
        hh_dbxrefs = self.session.query(HumanhealthDbxref).\
            join(Humanhealth, HumanhealthDbxref.humanhealth_id == Humanhealth.humanhealth_id).\
            join(HumanhealthDbxrefprop, HumanhealthDbxref.humanhealth_dbxref_id == HumanhealthDbxrefprop.humanhealth_dbxref_id).\
            join(Dbxref, Dbxref.dbxref_id == HumanhealthDbxref.dbxref_id).\
            filter(Dbxref.db_id == db.db_id,
                   HumanhealthDbxrefprop.type_id == cvterm.cvterm_id,
                   Humanhealth.humanhealth_id == self.humanhealth.humanhealth_id)
        for hh_dbxref in hh_dbxrefs:
            self.session.delete(hh_dbxref)
    else:
        self.session.query(HumanhealthDbxref).join(Humanhealth).join(HumanhealthDbxrefprop).\
            filter(HumanhealthDbxref.humanhealth_dbxref_id == HumanhealthDbxrefprop.humanhealth_dbxref_id,
                   HumanhealthDbxref.humanhealth_id == Humanhealth.humanhealth_id,
                   HumanhealthDbxrefprop.type_id == cvterm.cvterm_id,
                   Humanhealth.humanhealth_id == self.humanhealth.humanhealth_id).delete()


def bang_dbxrefprop_only(self, params):
    """
    Params needed are:-
    'cvterm', 'cvname': to get prop
    'dbname' and 'accession': to get the dbxref.
    'tuple': to allow reporting of problems
    'bang_type': d or c
    humanhealth and pub obtained from self.
    """
    # get dbxref
    dbxref = self.session.query(Dbxref).join(Db).\
        filter(Dbxref.db_id == Db.db_id,
               Db.name == params['dbname'],
               Dbxref.accession == params['accession']).one_or_none()
    if not dbxref:
        error_message = "Could not found accession {} in dbxref table for db {}".format(params['accession'], params['dbname'])
        self.error_track(params['tuple'], error_message, CRITICAL_ERROR)
        return

    # get cvterm
    cvterm = self.session.query(Cvterm).join(Cv).\
        filter(Cv.name == params['cvname'],
               Cvterm.name == params['cvterm']).\
        one_or_none()
    if not cvterm:
        log.critical("cvterm {} with cv of {} failed lookup".format(params['cvterm'], params['cvname']))
        return

    # get humanhealth_dbxref
    hh_dbxref = self.session.query(HumanhealthDbxref).\
        filter(HumanhealthDbxref.dbxref_id == dbxref.dbxref_id,
               HumanhealthDbxref.humanhealth_id == self.humanhealth.humanhealth_id).one_or_none()
    if not hh_dbxref:
        error_message = "Could not find link between {}:{} and {} in DB".format(params['dbname'], params['accession'], self.humanhealth.uniquename)
        self.error_track(params['tuple'], error_message, CRITICAL_ERROR)

    if params['bang_type'] == 'c':
        # delete all hh_dbxref_props for this hh, dbxref and cvterm
        self.session.query(HumanhealthDbxrefprop).\
            filter(HumanhealthDbxrefprop.type_id == cvterm.cvterm_id,
                   HumanhealthDbxrefprop.humanhealth_dbxref_id == hh_dbxref.humanhealth_dbxref_id).delete()
    else:
        # delete hh_dbxref_props for this hh, dbxref and cvterm AND value of that was specified
        self.session.query(HumanhealthDbxrefprop).\
            filter(HumanhealthDbxrefprop.type_id == cvterm.cvterm_id,
                   HumanhealthDbxrefprop.humanhealth_dbxref_id == hh_dbxref.humanhealth_dbxref_id,
                   HumanhealthDbxrefprop.value == params['tuple'][FIELD_VALUE]).delete()


def bang_feature_hh_dbxref(self, params):
    # get dbxref
    dbxref = self.session.query(Dbxref).join(Db).\
        filter(Dbxref.db_id == Db.db_id,
               Db.name == params['dbname'],
               Dbxref.accession == params['accession']).one_or_none()
    if not dbxref:
        error_message = "Could not found accession {} in dbxref table for db {}".format(params['accession'], params['dbname'])
        self.error_track(params['tuple'], error_message, CRITICAL_ERROR)
        return

    # get hh_dbxref
    hh_dbxref = self.session.query(HumanhealthDbxref).\
        filter(HumanhealthDbxref.dbxref_id == dbxref.dbxref_id,
               HumanhealthDbxref.humanhealth_id == self.humanhealth.humanhealth_id).one_or_none()
    if not hh_dbxref:
        error_message = "Could not find dbxref ({}:{}) -> humanhealth relationship {}in database.".\
            format(params['dbname'], params['accession'], self.humanhealth.uniquename)

    if params['bang_type'] == 'd':
        # get the feature
        feature = self.session.query(Feature).\
                      filter(Feature.name == params['tuple'][FIELD_VALUE],
                             Feature.uniquename.like("FBgn%")).one_or_none()
        if not feature:
            error_message = "Name {} not found in feature table with unique name starting with FBgn".\
                format(params['name'])
            self.error_track(params['tuple'], error_message, CRITICAL_ERROR)
            return

        self.session.query(FeatureHumanhealthDbxref).\
            filter(FeatureHumanhealthDbxref.feature_id == feature.feature_id,
                   FeatureHumanhealthDbxref.humanhealth_dbxref_id == hh_dbxref.humanhealth_dbxref_id,
                   FeatureHumanhealthDbxref.pub_id == self.pub.pub_id).delete()
    else:
        self.session.query(FeatureHumanhealthDbxref).\
            filter(FeatureHumanhealthDbxref.humanhealth_dbxref_id == hh_dbxref.humanhealth_dbxref_id,
                   FeatureHumanhealthDbxref.pub_id == self.pub.pub_id).delete()
