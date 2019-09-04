"""
.. module:: chado_humanhealth
   :synopsis: The "humanhealth" ChadoObject.

.. moduleauthor:: Ian Longden <ilongden@morgan.harvard.edu>
"""
import os
from .chado_base import ChadoObject, FIELD_VALUE
from harvdev_utils.production import (
    Humanhealth, HumanhealthPub, Humanhealthprop, Organism, Cvterm, Cv,
    HumanhealthDbxref, HumanhealthDbxrefprop, Db, Dbxref
)
from harvdev_utils.chado_functions import get_or_create
from error.error_tracking import CRITICAL_ERROR
import logging
from datetime import datetime

log = logging.getLogger(__name__)


class ChadoHumanhealth(ChadoObject):
    def __init__(self, params):
        log.info('Initializing ChadoHumanhealth object.')
        ##########################################
        # Set up how to process each type of input
        ##########################################
        self.type_dict = {'direct': self.load_direct,
                          'relationship': self.load_relationship,
                          'prop': self.load_prop,
                          'synonym': self.load_synonym,
                          'dissociate_pub': self.dissociate_pub,
                          'dissociate_hgnc': self.dissociate_hgnc,
                          'obsolete': self.make_obsolete,
                          'ignore': self.ignore,
                          'data_set': self.ignore,  # Done separately
                          'dbxref': self.load_dbxref,
                          'dbxrefprop': self.load_dbxrefprop,
                          'featureprop': self.load_featureprop}

        # self.delete_dict = {'direct': self.delete_direct,
        #                    'pubauthor': self.delete_author,
        #                    'relationship': self.delete_relationships,
        #                    'pubprop': self.delete_pubprops,
        #                    'dbxref': self.delete_dbxref,
        #                    'ignore': self.delete_ignore,
        #                    'obsolete': self.delete_obsolete}

        self.proforma_start_line_number = params.get('proforma_start_line_number')
        self.reference = params.get('reference')
        self.set_values = params.get('set_values')

        ###########################################################
        # Values queried later, placed here for reference purposes.
        ############################################################
        self.pub = None   # All other proforma need a reference to a pub
        self.newhumanhealth = False

        # Initiate the parent.
        super(ChadoHumanhealth, self).__init__(params)

        ############################################################
        # Get processing info and data to be processed.
        # Please see the yml/humanhealth.yml file for more details
        ############################################################
        yml_file = os.path.join(os.path.dirname(__file__), 'yml/humanhealth.yml')
        # Populated self.process_data with all possible keys.
        self.process_data = self.load_reference_yaml(yml_file, params)

    def process_set_dbxrefprop(self, set_key, data_set):
        valid_set = True
        valid_key = None  # need a valid key incase something is wrong to report line number etc

        params = {'cvterm': self.process_data[set_key]['cvterm'],
                  'cvname': self.process_data[set_key]['cv']}
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
            self.process_dbxrefprop(params)

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

    def process_sets(self):
        """
        Sets have a specific key, normally the shortened version of the fields
        that it uses. i.e. For HH5a, HH5b etc this becomes HH5.
        self.set_values is a dictionary of these and points to an list of the
        actual values the curators have added i.e. HH5a, HH5c
        This is an example of what the set_vales will look like.
        HH5: [{'HH5a': ('HH5a', '1111111', 16),
               'HH5b': ('HH5b', 'HGNC', 17),
               'HH5c': ('HH5c', 'hgnc_1', 18)},
              {'HH5a': ('HH5a', '2', 20),
               'HH5b': ('HH5b', 'UniProtKB/Swiss-Prot', 21),
               'HH5c': ('HH5c', 'sw_2', 22)},
              {'HH5a': ('HH5a', '3', 24),
                'HH5b': ('HH5b', 'UniProtKB/Swiss-Prot', 25),
                'HH5c': ('HH5c', None, 26)},
              {'HH5a': ('HH5a', '4444444', 28),
               'HH5b': ('HH5b', 'HGNC', 29),
               'HH5c': ('HH5c', 'hgnc_4', 30)},
              {'HH5a': ('HH5a', '1', 32),
               'HH5b': ('HH5b', 'HGNC', 33),
               'HH5c': ('HH5c', 'already exists so desc not updated', 34)},
              {'HH5a': ('HH5a', None, 36),
               'HH5b': ('HH5b', None, 37),
               'HH5c': ('HH5c', None, 38)
             ]
        This comes from the test 1505_HH_5abc_good_set.txt.sm.edit.1
        """
        for key in self.set_values.keys():
            log.debug("SV: {}: {}".format(key, self.set_values[key]))
            if key == 'HH5' or key == 'HH14':
                self.process_data_link(key)
            else:
                log.critical("Unknown set {}".format(key))
                return

    def load_content(self):
        """
        Main processing routine
        """
        self.pub = super(ChadoHumanhealth, self).pub_from_fbrf(self.reference, self.session)

        if self.process_data['HH1f']['data'][FIELD_VALUE] == "new":
            self.newhumanhealth = True
        self.humanhealth = self.get_humanhealth()

        if self.humanhealth:  # Only proceed if we have a hh. Otherwise we had an error.
            self.extra_checks()
        else:
            return

        # bang c first as this supersedes all things
        # if self.bang_c:
        #    self.bang_c_it()
        # if self.bang_d:
        #    self.bang_d_it()

        if self.set_values:
            self.process_sets()
        else:
            log.debug("No set values")

        for key in self.process_data:
            self.type_dict[self.process_data[key]['type']](key)

        timestamp = datetime.now().strftime('%c')
        curated_by_string = 'Curator: %s;Proforma: %s;timelastmodified: %s' % (self.curator_fullname, self.filename_short, timestamp)
        log.info('Curator string assembled as:')
        log.info('%s' % (curated_by_string))

    def obtain_session(self, session):
        self.session = session

    def get_humanhealth(self):
        """
        get humanhealth or create humanhealth if new.
        returns None or the humanhealth to be used.
        """
        if not self.newhumanhealth:
            hh = self.session.query(Humanhealth).\
                filter(Humanhealth.uniquename == self.process_data['HH1f']['data'][FIELD_VALUE]).\
                one_or_none()
            if not hh:
                self.critical_error(self.process_data['HH1f']['data'], 'Humanhealth does not exist in the database.')
                return
            # Check synonym name is the same as HH1b
            name = self.process_data['HH1b']['data'][FIELD_VALUE]
            if hh.name != name:
                self.critical_error(self.process_data['HH1b']['data'], 'HH1b field "{}" does NOT match the one in the database "{}"'.format(name, hh.name))
        else:
            # triggers add dbxref and proper uniquename
            # check we have HH2a, HH1g and HH1b
            organism, _ = get_or_create(self.session, Organism, abbreviation='Hsap')
            hh, _ = get_or_create(self.session, Humanhealth, name=self.process_data['HH1b']['data'][FIELD_VALUE],
                                  organism_id=organism.organism_id, uniquename='FBhh:temp_0')
            log.info(hh)
            # db has correct FBhh0000000x in it but here still has 'FBhh:temp_0'. ???
            # presume triggers start after hh is returned. Maybe worth getting form db again
            log.info("New humanhealth created with fbhh {} id={}.".format(hh.uniquename, hh.humanhealth_id))

        # Add to pub to hh if it does not already exist.
        get_or_create(self.session, HumanhealthPub, pub_id=self.pub.pub_id, humanhealth_id=hh.humanhealth_id)
        return hh

    def extra_checks(self):
        pass

    def load_direct(self, key):
        if self.has_data(key):
            old_attr = getattr(self.humanhealth, self.process_data[key]['name'])
            if old_attr:
                self.warning_error(self.process_data[key]['data'], "No !c but still overwriting existing value of {}".format(old_attr))
            setattr(self.humanhealth, self.process_data[key]['name'], self.process_data[key]['data'][FIELD_VALUE])

    def load_relationship(self, key):
        pass

    def load_prop(self, key):
        if not self.has_data(key):
            return

        log.debug("load prop {}: {} {}: {}".format(key, self.process_data[key]['cv'], self.process_data[key]['cvterm'], self.process_data[key]['data']))
        cvterm = self.session.query(Cvterm).join(Cv).\
            filter(Cv.name == self.process_data[key]['cv'],
                   Cvterm.name == self.process_data[key]['cvterm']).\
            one_or_none()

        if type(self.process_data[key]['data']) is not list:
            data_list = []
            data_list.append(self.process_data[key]['data'])
        else:
            data_list = self.process_data[key]['data']

        if not cvterm:
            self.critical_error(data_list[0],
                                'Cvterm missing "{}" for cv "{}".'.format(self.process_data[key]['cvterm'],
                                                                          self.process_data[key]['cv']))
            return

        for data in data_list:
            log.debug("Creating hhp with cvterm {}, hh {}, value {}".format(cvterm.cvterm_id,
                                                                            self.humanhealth.humanhealth_id,
                                                                            data[FIELD_VALUE]))
            get_or_create(self.session, Humanhealthprop, type_id=cvterm.cvterm_id,
                          humanhealth_id=self.humanhealth.humanhealth_id,
                          value=data[FIELD_VALUE])
        return

    def load_synonym(self, key):
        pass

    def dissociate_pub(self, key):
        pass

    def dissociate_hgnc(self, key):
        pass

    def make_obsolete(self, key):
        pass

    def ignore(self, key):
        return

    def load_dbxref(self, key):
        pass

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

        dbxref = self.session.query(Dbxref).join(Db).\
            filter(Dbxref.db_id == db.db_id,
                   Dbxref.accession == params['accession']).\
            one_or_none()
        if not dbxref:
            dbxref, _ = get_or_create(self.session, Dbxref, db_id=db.db_id, accession=params['accession'])
            if 'description' in params:
                dbxref.description = params['description']

        hh_dbxref, _ = get_or_create(self.session, HumanhealthDbxref,
                                     dbxref_id=dbxref.dbxref_id,
                                     humanhealth_id=self.humanhealth.humanhealth_id)
        return hh_dbxref

    def process_dbxrefprop(self, params):
        """
         General rountine for adding humanhealth dbxrefs and their props
         params should contain:-
         dbname:      db name for dbxref
         accession:   accession for dbxref
         cvname:      cv name for prop
         cvterm:      cvterm name for prop
         description: dbxref description (only used if new dbxref) *Also Optional*
         tuple:       one related tuple to help give better errors
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

        hhdp, _ = get_or_create(self.session, HumanhealthDbxrefprop,
                                humanhealth_dbxref_id=hh_dbxref.humanhealth_dbxref_id,
                                type_id=cvterm.cvterm_id)
        return hhdp

    def load_dbxrefprop(self, key):
        """
        load the hh_dbxref and hh_dbxrefprop.

        If db not in yml file then the format must be dbname:accession
        Else just the accession
        """
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
                self.process_dbxrefprop(params)
            else:
                try:
                    fields = item[FIELD_VALUE].split(':')
                    params['dbname'] = fields[0].strip()
                    params['accession'] = fields[1].strip()
                except IndexError:
                    error_message = "{} Not in the corect format of dbname:accession".format(item[FIELD_VALUE])
                    self.error_track(params['tuple'], error_message, CRITICAL_ERROR)
                    continue
                self.process_dbxrefprop(params)

    def load_featureprop(self, key):
        pass
