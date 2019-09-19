"""
.. module:: chado_humanhealth
   :synopsis: The "humanhealth" ChadoObject.

.. moduleauthor:: Ian Longden <ilongden@morgan.harvard.edu>
"""
import os
from ..chado_base import ChadoObject, FIELD_VALUE
from harvdev_utils.production import (
    Humanhealth, HumanhealthPub, Humanhealthprop, HumanhealthpropPub,
    HumanhealthRelationship, HumanhealthSynonym, HumanhealthFeature,
    Organism, Cvterm, Cv, Synonym
)
from harvdev_utils.chado_functions import get_or_create
from error.error_tracking import CRITICAL_ERROR
import logging
from datetime import datetime

log = logging.getLogger(__name__)


class ChadoHumanhealth(ChadoObject):
    from .humanhealth_dbxrefprop import (
        process_dbxrefprop, process_set_dbxrefprop, process_data_link,
        process_dbxref, get_or_create_dbxrefprop, load_dbxrefprop,
        delete_dbxrefprop, process_hh7, process_dbxref_link_item,
        process_hh7_c_and_d, process_hh7_e_and_f, create_set_initial_params
    )
    from .humanhealth_featureprop import (
        process_feature, process_featureprop, load_featureprop
    )

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
                          'obsolete': self.make_obsolete,
                          'ignore': self.ignore,
                          'data_set': self.ignore,  # Done separately
                          'dbxrefprop': self.load_dbxrefprop,
                          'featureprop': self.load_featureprop}

        self.delete_dict = {'dbxrefprop': self.bang_dbxrefprop,
                            'ignore': self.delete_ignore}
        #                    'relationship': self.delete_relationships,
        #                    'prop': self.delete_prop,
        #                    'synonym': self.delete_synonym,
        #                    'dbxref': self.delete_dbxrefprop,
        #                    'ignore': self.delete_ignore,
        #                     'dbxrefprop': self.delete_specific_dbxrefprop,
        #                  'featureprop': self.delete_featureprop,
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
        yml_file = os.path.join(os.path.dirname(__file__), '../yml/humanhealth.yml')
        # Populated self.process_data with all possible keys.
        self.process_data = self.load_reference_yaml(yml_file, params)

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
        if 'data' not in self.process_data[key]:  # MUST be part of set.
            self.delete_set_dbxrefprop(key)
        else:
            if self.bang_c:
                self.bang_c_it()
            if self.bang_d:
                self.bang_d_it()

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
            elif key == 'HH7':
                self.process_hh7(key)
            else:
                log.critical("Unknown set {}".format(key))
                return

    def load_direct(self, key):
        if self.has_data(key):
            old_attr = getattr(self.humanhealth, self.process_data[key]['name'])
            if old_attr:
                self.warning_error(self.process_data[key]['data'], "No !c but still overwriting existing value of {}".format(old_attr))
            setattr(self.humanhealth, self.process_data[key]['name'], self.process_data[key]['data'][FIELD_VALUE])

    def load_relationship(self, key):
        cvterm = self.session.query(Cvterm).join(Cv).\
            filter(Cv.name == self.process_data[key]['cv'],
                   Cvterm.name == self.process_data[key]['cvterm']).\
            one_or_none()

        if type(self.process_data[key]['data']) is not list:
            data_list = []
            data_list.append(self.process_data[key]['data'])
        else:
            data_list = self.process_data[key]['data']

        if not cvterm:  # after datalist set up as we need to pass a tuple
            self.critical_error(data_list[0],
                                'Cvterm missing "{}" for cv "{}".'.format(self.process_data[key]['cvterm'],
                                                                          self.process_data[key]['cv']))
            return

        for data in data_list:
            log.debug("Creating hhr with cvterm {}, hh {}, value {}".format(cvterm.cvterm_id,
                                                                            self.humanhealth.humanhealth_id,
                                                                            data[FIELD_VALUE]))
            hh_object = self.session.query(Humanhealth).\
                filter(Humanhealth.uniquename == data[FIELD_VALUE]).one_or_none()
            if not hh_object:
                error_message = "{} Not found in Humanhealth table".format(data[FIELD_VALUE])
                self.error_track(data, error_message, CRITICAL_ERROR)
                return None

            get_or_create(self.session, HumanhealthRelationship, type_id=cvterm.cvterm_id,
                          subject_id=self.humanhealth.humanhealth_id,
                          object_id=hh_object.humanhealth_id)
        return

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

        if not cvterm:  # after datalist set up as we need to pass a tuple
            self.critical_error(data_list[0],
                                'Cvterm missing "{}" for cv "{}".'.format(self.process_data[key]['cvterm'],
                                                                          self.process_data[key]['cv']))
            return

        for data in data_list:
            log.debug("Creating hhp with cvterm {}, hh {}, value {}".format(cvterm.cvterm_id,
                                                                            self.humanhealth.humanhealth_id,
                                                                            data[FIELD_VALUE]))
            hhp, _ = get_or_create(self.session, Humanhealthprop, type_id=cvterm.cvterm_id,
                                   humanhealth_id=self.humanhealth.humanhealth_id,
                                   value=data[FIELD_VALUE])
            get_or_create(self.session, HumanhealthpropPub,
                          humanhealthprop_id=hhp.humanhealthprop_id,
                          pub_id=self.pub.pub_id)
        return

    def load_synonym(self, key):
        cvterm = self.session.query(Cvterm).join(Cv).\
            filter(Cv.name == self.process_data[key]['cv'],
                   Cvterm.name == self.process_data[key]['cvterm']).\
            one_or_none()

        if type(self.process_data[key]['data']) is not list:
            data_list = []
            data_list.append(self.process_data[key]['data'])
        else:
            data_list = self.process_data[key]['data']

        if not cvterm:  # after datalist set up as we need to pass a tuple
            self.critical_error(data_list[0],
                                'Cvterm missing "{}" for cv "{}".'.format(self.process_data[key]['cvterm'],
                                                                          self.process_data[key]['cv']))
            return

        for data in data_list:
            new_syn, _ = get_or_create(self.session, Synonym, name=data[FIELD_VALUE],
                                       synonym_sgml=data[FIELD_VALUE], type_id=cvterm.cvterm_id)
            get_or_create(self.session, HumanhealthSynonym,
                          humanhealth_id=self.humanhealth.humanhealth_id,
                          synonym_id=new_syn.synonym_id,
                          pub_id=self.pub.pub_id)

    def dissociate_pub(self, key):
        """
        Remove humanhealth_pub, humanhealth_synonym and humanhealth_feature
        """
        #################
        # Humanhealth_pub
        #################
        hh_pub = self.session.query(HumanhealthPub).\
            filter(HumanhealthPub.pub_id == self.pub.pub_id,
                   HumanhealthPub.humanhealth_id == self.humanhealth.humanhealth_id).one_or_none()
        if not hh_pub:
            error_message = 'No relationship between pub and Humanhealth found in table'
            self.error_track(self.process_data[key]['data'], error_message, CRITICAL_ERROR)
            return None
        self.session.delete(hh_pub)

        self.session.query(HumanhealthSynonym).\
            filter(HumanhealthSynonym.pub_id == self.pub.pub_id,
                   HumanhealthSynonym.humanhealth_id == self.humanhealth.humanhealth_id).delete()

        self.session.query(HumanhealthFeature).\
            filter(HumanhealthFeature.pub_id == self.pub.pub_id,
                   HumanhealthFeature.humanhealth_id == self.humanhealth.humanhealth_id).delete()

        # TODO: humanhealth_cvterm, humanhealth_relationship, humanhealth_phenotype,
        #       library_humanhealth, feature_humanhealth_dbxref, humanhealth_dbxref,
        #       humanhealth_dbxrefprop

    def make_obsolete(self, key):
        pass

    def ignore(self, key):
        return

    def delete_ignore(self, key, bangc=False):
        return

    def delete_direct(self, key, bangc=True):
        try:
            new_value = self.process_data[key]['data'][FIELD_VALUE]
        except KeyError:
            new_value = None
        setattr(self.humanhealth, self.process_data[key]['name'], new_value)
        # NOTE: direct is a replacement so might aswell delete data to stop it being processed again.
        self.process_data[key]['data'] = None
