# -*- coding: utf-8 -*-
"""Chado Feature/Feature main module.

.. moduleauthor:: Ian Longden <ilongden@morgan.harvard.edu>
"""

import os
import re
from chado_object.chado_base import FIELD_VALUE
from chado_object.feature.chado_feature import ChadoFeatureObject
from harvdev_utils.production import (
    Feature, FeaturePub, FeatureRelationshipPub, FeatureRelationship,
    FeatureCvterm
    # Featureprop, FeatureCvtermprop,
    # Organism, Cvterm, Cv, Synonym, Db, Dbxref, Pub
)
from harvdev_utils.chado_functions import get_or_create, get_cvterm, feature_name_lookup
from harvdev_utils.chado_functions.organism import get_organism
# from error.error_tracking import CRITICAL_ERROR
import logging
from datetime import datetime

log = logging.getLogger(__name__)


class ChadoGeneProduct(ChadoFeatureObject):
    """Class object for Chado GeneProduct/Feature.

    Main chado object is a  Feature.
    """

    def __init__(self, params):
        """Initialise the Feature object.

        type dict and delete_dict determine which methods are called
        based on the controlling yml file.
        """
        log.debug('Initializing ChadoGeneProduct object.')

        # Initiate the parent.
        super(ChadoGeneProduct, self).__init__(params)

        ##########################################
        #
        # Set up how to process each type of input
        #
        # This is set in the Feature.yml file.
        ##########################################
        self.type_dict = {# 'prop': self.load_prop,
                          'cvterm': self.load_cvterm,
                          'synonym': self.load_synonym,
                          # 'dissociate_pub': self.dissociate_pub,
                          # 'obsolete': self.make_obsolete,
                          'ignore': self.ignore
                          # 'dbxrefprop': self.load_dbxrefprop,
                          # 'featureprop': self.load_featureprop
        }

        self.delete_dict = {# 'dbxrefprop': self.delete_dbxref,
                            'ignore': self.delete_ignore,
                            # 'prop': self.delete_prop,
                            'cvterm': self.delete_cvterm
                            # 'synonym': self.delete_synonym,
                            # 'featureprop': self.delete_featureprop,
                            # 'relationship': self.delete_relationship
        }

        self.proforma_start_line_number = params.get('proforma_start_line_number')
        self.reference = params.get('reference')

        ###########################################################
        # Values queried later, placed here for reference purposes.
        ############################################################
        self.pub = None   # All other proforma need a reference to a pub

        self.type = None  # Gene products can be of many types so store that here.
        self.new = False
        self.feature = None

        ############################################################
        # Get processing info and data to be processed.
        # Please see the yml/Feature.yml file for more details
        ############################################################
        yml_file = os.path.join(os.path.dirname(__file__), '../yml/geneproduct.yml')
        # Populated self.process_data with all possible keys.
        self.process_data = self.load_reference_yaml(yml_file, params)
        self.log = log

    def ignore(self, key):
        pass

    def delete_ignore(self, key, bangc):
        pass

    def load_content(self, references):
        """Process the proforma data."""
        self.pub = references['ChadoPub']

        if self.process_data['F1f']['data'][FIELD_VALUE] == "new":
            self.new = True
        self.feature = self.get_geneproduct()

        # if self.Feature:  # Only proceed if we have a hh. Otherwise we had an error.
        #    self.extra_checks()
        # else:
        #    return

        # bang c/d first as this supersedes all things
        if self.bang_c:
            self.bang_c_it()
        if self.bang_d:
            self.bang_d_it()

        for key in self.process_data:
            self.type_dict[self.process_data[key]['type']](key)

        timestamp = datetime.now().strftime('%c')
        curated_by_string = f'Curator: {self.curator_fullname};Proforma: {self.filename_short};timelastmodified: {timestamp}'
        log.debug('Curator string assembled as:')
        log.debug(curated_by_string)

    def load_cvterm(self, key):
        if self.has_data(key):
            cvterm = get_cvterm(self.session, self.process_data[key]['cv'], self.process_data[key]['cvterm'])
            if not cvterm:
                message = 'Cvterm lookup failed for cv {} cvterm {}?'.format(self.process_data[key]['cv'],
                                                                             self.process_data[key]['cvterm'])
                self.critical_error(self.process_data[key]['data'], message)
                return
            get_or_create(self.session, FeatureCvterm,
                          feature_id=self.feature.feature_id,
                          cvterm_id=cvterm.cvterm_id,
                          pub_id=self.pub.pub_id)

    def delete_cvterm(self, key, bangc):
        pass

    def check_format(self, status):
        format_okay = False

        name = status['name']
        if name.endswith('-XP') or name.endswith('-XR'):
            if self.has_data('F2'):
                message = f"F1a {name} cannot end in -XR or -XP if F2 is defined"
                self.critical_error(self.process_data['F1a']['data'], message)
            else:
                format_okay = True
        elif name.endswith(']PA') or name.endswith(']RA'):
            if not self.has_data('F2'):
                message = f"Require F2 value if {name} is transgenic (not -XR or -XP)"
                self.critical_error(self.process_data['F1a']['data'], message)
            else:
                format_okay = True
        elif '&cap;' in name:
            if not self.has_data('F2'):
                message = f"Require F2 value if {name} is transgenic (not -XR or -XP)"
                self.critical_error(self.process_data['F1a']['data'], message)
            else:
                format_okay = True
        if not format_okay:
            message = f"F1a {name} must end with -XR, -XP, ]PA, ]RA, or, contain '&cap;' for a split system combination feature"
            self.critical_error(self.process_data['F1a']['data'], message)
            status["error"] = True

    def check_type(self, status):
        pattern = r'(.*) (\w+):(\d+)'
        s_res = re.search(pattern, self.process_data['F3']['data'][FIELD_VALUE])
        if s_res:
            type_name = s_res.group(1)
            cv_name = s_res.group(2)
            if cv_name == 'FBcv':
                cv_name = 'FlyBase miscellaneous CV'
            status["feat_type"] = get_cvterm(self.session, cv_name, type_name)
            status["type_name"] = type_name
        else:
            message = r"Does not fit format, expected the format (.*) (\w+):(\d+)"
            self.critical_error(self.process_data['F3']['data'], message)
            status["error"] = True
            return

        if type_name == 'protein':
            message = "Type can not be 'protein', should be 'polypeptide"
            self.critical_error(self.process_data['F3']['data'], message)
            status["error"] = True
        if type_name != 'split system combination':
            if 'INTERSECTION' in status['name'] or '&cap;' in status['name']:
                message = f"split system combination feature {status['name']} must have type 'split system combination FBcv:0009026' in F3."
                self.critical_error(self.process_data['F3']['data'], message)
                status["error"] = True

    def check_type_name(self, status):
        if 'type_name' not in status:
            return

        name = status['name']

        type_name = status['type_name']
        if type_name == 'split system combination':
            status['fb_prefix'] = "FBco"
            if '&cap;' not in name:
                message = f"new split system combination feature {name} must have '&cap;' in its name"
                self.critical_error(self.process_data['F1a']['data'], message)
                status["error"] = True

            pattern = "(XR|XP|R[A-Z]|P[A-Z])$"
            s_res = re.findall(pattern, name)
            if s_res:
                message = f"new split system combination feature {name} must not have any XR/XP/RA/PA suffix in its name"
                self.critical_error(self.process_data['F1a']['data'], message)
                status["error"] = True

            pattern = "DBD.*AD"
            s_res = re.findall(pattern, name)
            if not s_res:
                message = f"new split system combination feature {name} must list DBD before AD;"
                self.critical_error(self.process_data['F1a']['data'], message)
                status["error"] = True

        elif type_name == 'polypeptide':
            status['fb_prefix'] = "FBpp"
            pattern = "(-XP|P[A-Z])$"
            s_res = re.findall(pattern, name)
            if not s_res:
                message = f"polypeptide {name} should be ended with -XP or PA"
                self.critical_error(self.process_data['F1a']['data'], message)
                status["error"] = True
        elif type_name.endswith('RNA'):
            status['fb_prefix'] = "FBtr"
            pattern = "(-XR|R[A-Z])$"
            s_res = re.findall(pattern, name)
            if not s_res:
                message = f"transcript {name} should be ended with -XR or RA"
                self.critical_error(self.process_data['F1a']['data'], message)
                status["error"] = True
        else:
            message = f"unexpected F3 value: {type_name}"
            self.critical_error(self.process_data['F3']['data'], message)
            status["error"] = True

    def get_feats(self, status):
        """Lookup the features from the base name/s"""
        status['features'] = []
        feats = []
        if status['type_name'] == 'split system combination':
            feats = status['name'].split('&cap;')
        else:
            pattern = '^(.*)(-X[RP]|[RP][A-Z])$'
            res = re.match(pattern, status['name'])
            if res:
                feats.append(res.group(1))
            else:
                message = "Could not find existing feature in the name."
                self.critical_error(self.process_data['F1a']['data'], message)
                status["error"] = True
                return

        for feat in feats:
            feat = feature_name_lookup(self.session, name=feat, obsolete='f')
            if feat:
                log.debug(f"BOB: Feature lookup found: {feat}")
                status['features'].append(feat.feature_id)
            else:
                message = f"Could not find feature {feat} in the database to add the feature relationship"
                self.critical_error(self.process_data['F1a']['data'], message)
                status["error"] = True

    def get_uniquename_and_checks(self):
        # Need to return string based on F3 content.
        # return dict of :-
        #
        # error: [True/False]
        # features : [features producing this new product]  # NOTE 2 of these for splits
        # fb_prefix: string (FBxx)
        # feat_type: cvterm object

        status = {'error': False,
                  'name': self.process_data['F1a']['data'][FIELD_VALUE]}
        self.check_format(status)
        self.check_type(status)
        self.check_type_name(status)
        self.get_feats(status)

        return status

    def add_relationships(self, status):

        cvterm_name = 'associated_with'
        cv_name = 'relationship type'
        if status['type_name'] == 'split system combination':
            cvterm_name = 'partially_produced_by'
        cvterm = get_cvterm(self.session, cv_name=cv_name, cvterm_name=cvterm_name)

        pub_id = self.get_unattrib_pub().pub_id
        for feat_id in status['features']:
            fr, _ = get_or_create(self.session, FeatureRelationship,
                                  subject_id=self.feature.feature_id,
                                  object_id=feat_id,
                                  type_id=cvterm.cvterm_id)

            frp, _ = get_or_create(self.session, FeatureRelationshipPub,
                                   feature_relationship_id=fr.feature_relationship_id,
                                   pub_id=pub_id)

    def get_org(self, status):
        abbr = 'Dmel'

        if status['type_name'] == 'split system combination':
            abbr = 'Ssss'
        else:
            pattern = r'^(.{2,14}?)\\'
            s_res = re.search(pattern, self.process_data['F1a']['data'][FIELD_VALUE])
            if s_res:
                abbr = s_res[1]
        org = get_organism(self.session, short=abbr)
        return org

    def get_geneproduct(self):
        if self.new:

            # get type/uniquename from F3.
            status = self.get_uniquename_and_checks()
            if status['error']:
                return
            organism = self.get_org(status)
            gp, _ = get_or_create(self.session, Feature, name=self.process_data['F1a']['data'][FIELD_VALUE],
                                  organism_id=organism.organism_id, uniquename=f'{status["fb_prefix"]}:temp_0',
                                  type_id=status['feat_type'].cvterm_id)

            # db has correct FBhh0000000x in it but here still has 'FBhh:temp_0'. ???
            # presume triggers start after hh is returned. Maybe worth getting form db again
            log.debug(f"New gene product created {gp.uniquename} id={gp.feature_id}.")

            self.feature = gp
            self.add_relationships(status)
            self.load_synonym('F1a')  # add symbol
            # self.load_synonym('F1a')                       # add fullname HAS NONE
        else:
            not_obsolete = False
            gp = self.session.query(Feature).\
                filter(Feature.uniquename == self.process_data['F1f']['data'][FIELD_VALUE],
                       Feature.is_obsolete == not_obsolete).\
                one_or_none()
            if not gp:
                self.critical_error(self.process_data['F1f']['data'], 'Feature does not exist in the database or is obsolete.')
                return

        # Add to pub to hh if it does not already exist.
        get_or_create(self.session, FeaturePub, pub_id=self.pub.pub_id, feature_id=gp.feature_id)
        return gp
