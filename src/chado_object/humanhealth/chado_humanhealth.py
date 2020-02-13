# -*- coding: utf-8 -*-
"""Chado Humanhealth main module.

.. module:: chado_humanhealth
   :synopsis: The "humanhealth" ChadoObject.
.. class:: chado_humanhealth.ChadoHumanhealth
.. moduleauthor:: Ian Longden <ilongden@morgan.harvard.edu>
"""

import os
from chado_object.chado_base import ChadoObject, FIELD_VALUE
from harvdev_utils.production import (
    Humanhealth, HumanhealthPub, Humanhealthprop, HumanhealthpropPub,
    HumanhealthRelationship, HumanhealthSynonym, HumanhealthFeature,
    HumanhealthCvterm, HumanhealthCvtermprop, HumanhealthDbxref,
    Organism, Cvterm, Cv, Synonym, Db, Dbxref
)
from harvdev_utils.chado_functions import get_or_create
from error.error_tracking import CRITICAL_ERROR
import logging
from datetime import datetime

log = logging.getLogger(__name__)


class ChadoHumanhealth(ChadoObject):
    """Class object for Chado Humanhealth.

    Main chado object for humanhealth.
    """

    from .humanhealth_dbxrefprop import (
        process_dbxrefprop, process_set_dbxrefprop, process_data_link,
        process_dbxref, get_or_create_dbxrefprop, load_dbxrefprop,
        process_hh7, process_dbxref_link_item,
        process_hh7_c_and_d, process_hh7_e_and_f, create_set_initial_params,
        delete_dbxref, bangc_dbxref, bangd_dbxref, bang_dbxrefprop_only, bang_feature_hh_dbxref
    )
    from .humanhealth_featureprop import (
        process_feature, process_featureprop, load_featureprop,
        delete_featureprop, bangc_featureprop, bangd_featureprop,
        process_hh8, process_featurepropset, delete_featureprop_only
    )

    def __init__(self, params):
        """Initialise the humanhealth object.

        .. function:: __init__
        type dict and delete_dict determine which methods are called
        based on the conrolling yml file.
        """
        log.info('Initializing ChadoHumanhealth object.')
        ##########################################
        #
        # Set up how to process each type of input
        #
        # This is set in the humanhealth.yml file.
        ##########################################
        self.type_dict = {'direct': self.load_direct,
                          'relationship': self.load_relationship,
                          'prop': self.load_prop,
                          'cvterm': self.load_cvterm,
                          'synonym': self.load_synonym,
                          'dissociate_pub': self.dissociate_pub,
                          'obsolete': self.make_obsolete,
                          'ignore': self.ignore,
                          'data_set': self.ignore,  # Done separately
                          'dbxrefprop': self.load_dbxrefprop,
                          'featureprop': self.load_featureprop}

        self.delete_dict = {'direct': self.delete_direct,
                            'dbxrefprop': self.delete_dbxref,
                            'ignore': self.delete_ignore,
                            'prop': self.delete_prop,
                            'cvterm': self.delete_cvterm,
                            'synonym': self.delete_synonym,
                            'featureprop': self.delete_featureprop,
                            'relationship': self.delete_relationship}

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
        """Process the proforma data.

        .. function:: load_content
        """
        self.pub = super(ChadoHumanhealth, self).pub_from_fbrf(self.reference)

        if self.process_data['HH1f']['data'][FIELD_VALUE] == "new":
            self.newhumanhealth = True
        self.humanhealth = self.get_humanhealth()

        if self.humanhealth:  # Only proceed if we have a hh. Otherwise we had an error.
            self.extra_checks()
        else:
            return

        # bang c/d first as this supersedes all things
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

    def get_humanhealth(self):
        """Get the humanhealth chado object.

        Get humanhealth or create humanhealth if new.
        returns None or the humanhealth to be used.
        """
        if self.newhumanhealth:
            # triggers add dbxref and proper uniquename
            # check we have HH2a, HH1g and HH1b
            organism, _ = get_or_create(self.session, Organism, abbreviation='Hsap')
            hh, _ = get_or_create(self.session, Humanhealth, name=self.process_data['HH1b']['data'][FIELD_VALUE],
                                  organism_id=organism.organism_id, uniquename='FBhh:temp_0')
            # db has correct FBhh0000000x in it but here still has 'FBhh:temp_0'. ???
            # presume triggers start after hh is returned. Maybe worth getting form db again
            log.info("New humanhealth created with fbhh {} id={}.".format(hh.uniquename, hh.humanhealth_id))
        else:
            not_obsolete = False
            hh = self.session.query(Humanhealth).\
                filter(Humanhealth.uniquename == self.process_data['HH1f']['data'][FIELD_VALUE],
                       Humanhealth.is_obsolete == not_obsolete).\
                one_or_none()
            if not hh:
                self.critical_error(self.process_data['HH1f']['data'], 'Humanhealth does not exist in the database or is obsolete.')
                return
            # Check synonym name is the same as HH1b
            name = self.process_data['HH1b']['data'][FIELD_VALUE]
            if hh.name != name:
                self.critical_error(self.process_data['HH1b']['data'], 'HH1b field "{}" does NOT match the one in the database "{}"'.format(name, hh.name))

        # Add to pub to hh if it does not already exist.
        get_or_create(self.session, HumanhealthPub, pub_id=self.pub.pub_id, humanhealth_id=hh.humanhealth_id)
        return hh

    def extra_checks(self):
        """Extra checks.

        cerberus validator cannot do some checks very easily, do we do them here.
        """
        # If HH2b is specified then must have a category of 'parent-entity'
        # and self.humanhealth must have a category of 'sub-entity'
        if 'HH2b' in self.process_data and self.process_data['HH2b']['data'][FIELD_VALUE] != '':
            cvterm = self.session.query(Cvterm).join(Cv).\
                filter(Cv.name == 'property type',
                       Cvterm.name == 'category').one_or_none()
            if not cvterm:
                self.critical_error(self.process_data['HH2b']['data'],
                                    'Cvterm missing "category" for cv "property type".')
                return

            hhp = self.session.query(Humanhealthprop).\
                join(Humanhealth).\
                filter(Humanhealth.uniquename == self.process_data['HH2b']['data'][FIELD_VALUE],
                       Humanhealthprop.type_id == cvterm.cvterm_id).one_or_none()
            if not hhp or hhp.value != 'parent-entity':
                self.critical_error(self.process_data['HH2b']['data'],
                                    '{} must be a parent-entity but this is not the case here.'.format(self.process_data['HH2b']['data'][FIELD_VALUE]))

            if self.newhumanhealth:
                if 'HH2a' not in self.process_data or self.process_data['HH2a']['data'][FIELD_VALUE] != 'sub-entity':
                    self.critical(self.process_data['HH2b']['data'],
                                  "New humanhealth has a parent specified but its own type specified by HH2a is not sub-entity")
            else:
                hhp = self.session.query(Humanhealthprop).\
                    join(Humanhealth).\
                    filter(Humanhealth.humanhealth_id == self.humanhealth.humanhealth_id,
                           Humanhealthprop.type_id == cvterm.cvterm_id).one_or_none()
                if not hhp or hhp.value != 'sub-entity':
                    self.critical_error(self.process_data['HH2b']['data'],
                                        '{} must be a sub-entity but this is not the case here.'.format(self.humanhealth.uniquename))

    def process_sets(self):
        """Process the set data.

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
            elif key == 'HH8':
                self.process_hh8(key)
            else:
                log.critical("Unknown set {}".format(key))
                return

    def load_direct(self, key):
        """Load the direct fields."""
        if self.has_data(key):
            old_attr = getattr(self.humanhealth, self.process_data[key]['name'])
            if old_attr:
                # Is it just a check?
                if old_attr != self.process_data[key]['data'][FIELD_VALUE] and not self.newhumanhealth:
                    message = "No !c But {} does not match value of {}".format(self.process_data[key]['data'][FIELD_VALUE], old_attr)
                    self.critical_error(self.process_data[key]['data'], message)
            else:
                setattr(self.humanhealth, self.process_data[key]['name'], self.process_data[key]['data'][FIELD_VALUE])

    def load_cvterm(self, key):
        """Load the cvterms."""
        # lookup dbxref DOID:nnnnn
        # get the cvterm for this cv:'disease_ontology' (joined by dbxref)
        # lookup cvterm for doid_term
        # create humanhealth_cvterm (first cvterm and hh)
        # cretae humanhealth)cvtermprop with type_id of second cvterm

        # this needs to be done only once so do first outside of loop
        doid_cvterm = self.session.query(Cvterm).join(Cv).\
            filter(Cv.name == self.process_data[key]['cv'],
                   Cvterm.name == self.process_data[key]['cvterm']).\
            one_or_none()
        if not doid_cvterm:  # after datalist set up as we need to pass a tuple
            self.critical_error(self.process_data[key]['data'][FIELD_VALUE],
                                'Cvterm missing "{}" for cv "{}".'.format(self.process_data[key]['cvterm'],
                                                                          self.process_data[key]['cv']))
            return

        for item in self.process_data[key]['data']:
            db, acc = item[FIELD_VALUE].split(':')
            # NOTE: db is DOID as specified in the format validation
            log.debug("Looking up {} for dn DOID".format(acc))
            dbxref = self.session.query(Dbxref).\
                join(Db).\
                filter(Db.name == 'DOID',
                       Dbxref.accession == acc).one_or_none()
            if not dbxref:
                self.critical_error(item, "Accession {} Not found in database for DOID.".format(acc))
                continue
            dis_cvterm = self.session.query(Cvterm).\
                join(Cv).\
                filter(Cvterm.dbxref_id == dbxref.dbxref_id,
                       Cv.name == 'disease_ontology').one_or_none()
            if not dis_cvterm:
                self.critical_error(item, "DO Cvterm Not found for this acc and cv of 'disease_ontology'")
                continue
            # make hh_cvterm
            hh_c, _ = get_or_create(self.session, HumanhealthCvterm,
                                    humanhealth_id=self.humanhealth.humanhealth_id,
                                    cvterm_id=dis_cvterm.cvterm_id,
                                    pub_id=self.pub.pub_id)
            hhcp, _ = get_or_create(self.session, HumanhealthCvtermprop,
                                    humanhealth_cvterm_id=hh_c.humanhealth_cvterm_id,
                                    type_id=doid_cvterm.cvterm_id)

    def load_relationship(self, key):
        """Load relationships between humanhealths."""
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
        """Load the properties."""
        if not self.has_data(key):
            return

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
            hhp, _ = get_or_create(self.session, Humanhealthprop, type_id=cvterm.cvterm_id,
                                   humanhealth_id=self.humanhealth.humanhealth_id,
                                   value=data[FIELD_VALUE])
            get_or_create(self.session, HumanhealthpropPub,
                          humanhealthprop_id=hhp.humanhealthprop_id,
                          pub_id=self.pub.pub_id)
        return

    def load_synonym(self, key):
        """Load the synonyms."""
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

########################
# Deletion routines
########################

    def dissociate_pub(self, key):
        """Dissaociate pub.

        Remove humanhealth_pub, humanhealth_synonym, humanhealth_cvterm, humanhealth_relationship,
        feature_humanhealth_dbxref, humanhealth_dbxref, humanhealth_dbxrefprop and humanhealth_feature

        NOTE: humanhealth_phenotype and library_humanhealth seem to be empty are not
            : filled in by anything here.
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

        self.session.query(HumanhealthCvterm).\
            filter(HumanhealthCvterm.pub_id == self.pub.pub_id,
                   HumanhealthCvterm.humanhealth_id == self.humanhealth.humanhealth_id).delete()

        self.session.query(HumanhealthRelationship).\
            filter(HumanhealthRelationship.subject_id == self.humanhealth.humanhealth_id).delete()
        self.session.query(HumanhealthRelationship).\
            filter(HumanhealthRelationship.object_id == self.humanhealth.humanhealth_id).delete()

        # Deleting humanhealth_dbxref should remove feature_humanhealth_dbxref humanhealth_dbxrefprop
        # and by the CASCADE
        self.session.query(HumanhealthDbxref).\
            filter(HumanhealthDbxref.humanhealth_id == self.humanhealth.humanhealth_id).delete()

    def delete_synonym(self, key, bangc=False):
        """Delete synonym.

        Well actually set is_current to false for this entry.
        """
        if type(self.process_data[key]['data']) is not list:
            data_list = []
            data_list.append(self.process_data[key]['data'])
        else:
            data_list = self.process_data[key]['data']

        if bangc:
            # hh_syn has only one cvterm related to it so no need to specify.
            self.session.query(HumanhealthSynonym).\
                filter(HumanhealthSynonym.pub_id == self.pub.pub_id,
                       HumanhealthSynonym.is_current == False,  # noqa: E712
                       HumanhealthSynonym.pub_id == self.pub.pub_id,
                       HumanhealthSynonym.humanhealth_id == self.humanhealth.humanhealth_id).delete()
        else:
            for data in data_list:
                synonyms = self.session.query(Synonym).\
                    filter(Synonym.name == data[FIELD_VALUE])
                syn_count = 0
                hh_syn_count = 0
                for syn in synonyms:
                    syn_count += 1
                    hh_syns = self.session.query(HumanhealthSynonym).\
                        filter(HumanhealthSynonym.humanhealth_id == self.humanhealth.humanhealth_id,
                               HumanhealthSynonym.synonym_id == syn.synonym_id,
                               HumanhealthSynonym.is_current == False,  # noqa: E712
                               HumanhealthSynonym.pub_id == self.pub.pub_id)
                    for hh_syn in hh_syns:
                        hh_syn_count += 1
                        self.session.delete(hh_syn)

                if not syn_count:
                    self.critical_error(data, 'Synonym {} Does not exist.'.format(data[FIELD_VALUE]))
                    continue
                elif not hh_syn_count:
                    self.critical_error(data, 'Synonym {} Does not exist for this humanhealth that is not current.'.format(data[FIELD_VALUE]))
                    continue

    def delete_cvterm(self, key, bangc=False):
        """Delete the cvterm.

        .. class:: ChadoHumanhealth
        .. function:: delete_cvterm
        """
        if bangc:
            self.session.query(HumanhealthCvterm).\
                filter(HumanhealthCvterm.humanhealth_id == self.humanhealth.humanhealth_id).delete()
            return

        for item in self.process_data[key]['data']:
            db, acc = item[FIELD_VALUE].split(':')
            # NOTE: db is DOID as specified in the format validation
            log.debug("Looking up {} for dn DOID".format(acc))
            dbxref = self.session.query(Dbxref).\
                join(Db).\
                filter(Db.name == 'DOID',
                       Dbxref.accession == acc).one_or_none()
            if not dbxref:
                self.critical_error(item, "Accession {} Not found in database for DOID.".format(acc))
                continue
            dis_cvterm = self.session.query(Cvterm).\
                join(Cv).\
                filter(Cvterm.dbxref_id == dbxref.dbxref_id,
                       Cv.name == 'disease_ontology').one_or_none()
            if not dis_cvterm:
                self.critical_error(item, "DO Cvterm Not found for this acc {} and cv of 'disease_ontology'".format(acc))
                continue
            hhc = self.session.query(HumanhealthCvterm).\
                filter(HumanhealthCvterm.humanhealth_id == self.humanhealth.humanhealth_id,
                       HumanhealthCvterm.cvterm_id == dis_cvterm.cvterm_id).one_or_none()
            if not hhc:
                self.critical_error(item, "No humanhealth relationship found for {} and DOID:{}".format(self.humanhealth.uniquename, acc))
                continue
            else:
                self.session.delete(hhc)

    def delete_relationship(self, key, bangc=False):
        """Delete the relationship."""
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
            return None
        if bangc:
            self.session.query(HumanhealthRelationship).\
                filter(HumanhealthRelationship.type_id == cvterm.cvterm_id,
                       HumanhealthRelationship.subject_id == self.humanhealth.humanhealth_id).delete()
        else:
            for data in data_list:
                hh_object = self.session.query(Humanhealth).\
                    filter(Humanhealth.uniquename == data[FIELD_VALUE]).one_or_none()
                if not hh_object:
                    error_message = "{} Not found in Humanhealth table".format(data[FIELD_VALUE])
                    self.error_track(data, error_message, CRITICAL_ERROR)
                    return None
                hh_relationships = self.session.query(HumanhealthRelationship).\
                    filter(HumanhealthRelationship.subject == self.humanhealth.humanhealth_id,
                           HumanhealthRelationship.object == hh_object.humanhealth_id,
                           HumanhealthRelationship.type_id == cvterm.cvterm_id)
                relationship_count = 0
                for hh_rel in hh_relationships:
                    self.session.delete(hh_rel)
                    relationship_count += 1
                if not relationship_count:
                    error_message = "No Relationship found between {} and {} for {}".format(self.humanhealth.uniquename, hh_object.name, cvterm.name)
                    self.error_track(data, error_message, CRITICAL_ERROR)
                    return

    def make_obsolete(self, key):
        """Make the humanhealth recid obsolete."""
        self.humanhealth.is_obsolete = True

    def ignore(self, key):  # noqa D102
        return

    def delete_ignore(self, key, bangc=False):
        """Delete filler code."""
        return

    def delete_direct(self, key, bangc=True):
        """Delete the direct fileds."""
        try:
            new_value = self.process_data[key]['data'][FIELD_VALUE]
        except KeyError:
            new_value = None
        setattr(self.humanhealth, self.process_data[key]['name'], new_value)
        # NOTE: direct is a replacement so might aswell delete data to stop it being processed again.
        self.process_data[key]['data'] = None

    def delete_prop(self, key, bangc=True):
        """Delete the prop."""
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

        if not bangc:
            for data in data_list:
                hp = self.session.query(Humanhealthprop).\
                    join(HumanhealthpropPub).\
                    filter(Humanhealthprop.humanhealth_id == self.humanhealth.humanhealth_id,
                           Humanhealthprop.type_id == cvterm.cvterm_id,
                           HumanhealthpropPub.pub_id == self.pub.pub_id,
                           Humanhealthprop.value == data[FIELD_VALUE]).one_or_none()
                if not hp:
                    self.critical_error(data, 'Value "{}" Not found for Cvterm "{}".'.format(data[FIELD_VALUE], self.process_data[key]['cvterm']))
                else:
                    self.session.delete(hp)
        else:
            hp_list = self.session.query(Humanhealthprop).\
                join(HumanhealthpropPub).\
                filter(Humanhealthprop.humanhealth_id == self.humanhealth.humanhealth_id,
                       HumanhealthpropPub.pub_id == self.pub.pub_id,
                       Humanhealthprop.type_id == cvterm.cvterm_id)
            count = 0
            for hp in hp_list:
                count += 1
                self.session.delete(hp)
            if not count:
                self.critical_error(data_list[0], "No props removed so Error using bangc")
