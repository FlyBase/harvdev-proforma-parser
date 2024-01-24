# -*- coding: utf-8 -*-
"""Chado Feature/Feature main module.

.. moduleauthor:: Ian Longden <ilongden@morgan.harvard.edu>
"""

import os
import re
import logging
from datetime import datetime
from typing import Union

from chado_object.geneproduct.abbreviation import assays, stages
from chado_object.chado_base import FIELD_VALUE
from chado_object.feature.chado_feature import ChadoFeatureObject
from harvdev_utils.production import (
    Feature, FeaturePub, FeatureRelationshipPub, FeatureRelationship, FeatureRelationshipprop,
    FeatureCvterm, FeatureCvtermprop, Organism, Pub,
    Expression, ExpressionCvterm, FeatureExpression,
    FeatureExpressionprop, FeatureSynonym,
    # Featureprop, FeatureCvtermprop,
    Cvterm, Cv, Synonym  # , Db, Dbxref
)
from harvdev_utils.chado_functions import (
    get_or_create, get_cvterm,
    feature_name_lookup, feature_symbol_lookup
)
from harvdev_utils.chado_functions.organism import get_organism
# from error.error_tracking import CRITICAL_ERROR


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
        self.type_dict = {'cvterm': self.load_cvterm,
                          'synonym': self.load_synonym,
                          'ignore': self.ignore,
                          'prop': self.load_featureprop,
                          'feat_relationship': self.load_feat_relationship,
                          'expression': self.expression,
                          'gene': self.todo,
                          'relationship': self.todo,  # diff from feat_relationship
                          'merge': self.todo,
                          'rename': self.rename,
                          'disspub': self.dissociate_from_pub,
                          'obsolete': self.make_obsolete,
                          'no_idea_yet': self.todo,  # do not know what it does yet
                          'size': self.todo}

        self.delete_dict = {'ignore': self.delete_ignore,
                            'cvterm': self.delete_cvterm,
                            'prop': self.delete_featureprop,
                            'gene': self.delete_ignore,
                            'expression': self.delete_ignore}

        self.proforma_start_line_number = params.get('proforma_start_line_number')
        self.reference = params.get('reference')

        ###########################################################
        # Values queried later, placed here for reference purposes.
        ############################################################
        self.pub: Union[Pub, None] = None   # All other proforma need a reference to a pub

        self.new: bool = False
        self.feature: Union[Feature, None] = None

        ############################################################
        # Get processing info and data to be processed.
        # Please see the yml/Feature.yml file for more details
        ############################################################
        yml_file = os.path.join(os.path.dirname(__file__), '../yml/geneproduct.yml')
        # Populated self.process_data with all possible keys.
        self.process_data = self.load_reference_yaml(yml_file, params)
        self.log = log

    def todo(self, key):
        print(f"{key}: not programmed yet")
        pass

    def rename(self, key):
        # set current synonym is_current to False
        cvterm = get_cvterm(self.session, self.process_data[key]['cv'], self.process_data[key]['cvterm'])
        fss = self.session.query(FeatureSynonym).join(Synonym).\
            filter(FeatureSynonym.feature_id == self.feature.feature_id,
                   FeatureSynonym.is_current == 't',
                   Synonym.type_id == cvterm.cvterm_id).all()
        for fs in fss:
            fs.is_current = False

        synonym, _ = get_or_create(self.session, Synonym,
                                   name=self.process_data['F1a']['data'][FIELD_VALUE],
                                   synonym_sgml=self.process_data['F1a']['data'][FIELD_VALUE],
                                   type_id=cvterm.cvterm_id)
        get_or_create(self.session, FeatureSynonym,
                      feature_id=self.feature.feature_id,
                      synonym_id=synonym.synonym_id,
                      pub_id=self.pub.pub_id)

    def load_feat_relationship(self, key):
        # lookup symbol
        feat2 = feature_symbol_lookup(self.session, 'gene', self.process_data[key]['data'][FIELD_VALUE], ignore_org=True)
        # get cvterm
        cvterm = get_cvterm(self.session, self.process_data[key]['cv'], self.process_data[key]['cvterm'])
        fr, _ = get_or_create(self.session, FeatureRelationship,
                              subject_id=self.feature.feature_id,
                              object_id=feat2.feature_id,
                              type_id=cvterm.cvterm_id)

        frp, _ = get_or_create(self.session, FeatureRelationshipPub,
                               feature_relationship_id=fr.feature_relationship_id,
                               pub_id=self.pub.pub_id)
        for postfix in ('a', 'b'):
            new_key = f'{key}{postfix}'
            if self.has_data(new_key) and self.process_data[new_key]['data'][FIELD_VALUE] == 'y':
                cvterm = get_cvterm(self.session, self.process_data[new_key]['cv'],
                                    self.process_data[new_key]['cvterm'])
                p, _ = get_or_create(self.session, FeatureRelationshipprop,
                                     feature_relationship_id=frp.feature_relationship_id,
                                     type_id=cvterm.cvterm_id)
                p.value = 'y'

    def add_exp_cvterm(self, exp, exp_id, cv1, cvt1, cv2, cvt2):
        cvterm = get_cvterm(self.session, cv1, cvt1)
        if not cvterm:
            message = f'Cvterm lookup failed for cv {cv1} cvterm {cvt1}?'
            self.critical_error(exp, message)
            return
        cvterm_type = get_cvterm(self.session, cv2, cvt2)
        if not cvterm_type:
            message = f'Cvterm lookup failed for cv {cv2} cvterm {cvt2}?'
            self.critical_error(exp, message)
            return
        get_or_create(self.session, ExpressionCvterm,
                      expression_id=exp_id,
                      cvterm_id=cvterm.cvterm_id,
                      cvterm_type_id=cvterm_type.cvterm_id)

    def create_exp(self):
        exp, _ = get_or_create(self.session, Expression, uniquename='FBex:temp')
        return exp.expression_id

    def create_feat_exp(self, exp_id):
        feat_exp, _ = get_or_create(self.session, FeatureExpression,
                                    feature_id=self.feature.feature_id,
                                    expression_id=exp_id,
                                    pub_id=self.pub.pub_id)
        return feat_exp.feature_expression_id

    def expression(self, key):
        group_to_key = {1: '<e>',
                        2: '<t>',
                        3: '<a>',
                        4: '<s>',
                        5: '<note>'}
        pattern = r"<e>(.*)<t>(.*)<a>(.*)<s>(.*)<note>(.*)"
        curated_prop = get_cvterm(self.session, 'feature_expression property type', 'curated_as')
        comment_prop = get_cvterm(self.session, 'feature_expression property type', 'comment')
        for exp in self.process_data[key]['data']:
            self.log.debug(exp[FIELD_VALUE])
            s_res = re.search(pattern, exp[FIELD_VALUE])
            if not s_res:
                self.log.critical(f"Could not breakup line using regex {pattern}")
                continue
            exp_id = self.create_exp()
            feat_exp_id = self.create_feat_exp(exp_id)
            for group in (1, 2, 3, 4):  # Notes are different do after
                value = s_res.group(group).strip()
                if value:
                    if group_to_key[group] == '<e>':  # Do look up of abbr to cvterm
                        value = assays[value]
                    elif group_to_key[group] == '<t>':  # Do look up of abbr to cvterm
                        try:
                            value = stages[value]
                        except KeyError:
                            pass
                    cv1 = self.process_data[key]['cv_mappings'][group_to_key[group]]['cv1']
                    cv2 = self.process_data[key]['cv_mappings'][group_to_key[group]]['cv2']
                    cvt2 = self.process_data[key]['cv_mappings'][group_to_key[group]]['cvt2']
                    if group_to_key[group] == '<a>':  # can be split with '|'
                        values = value.split('|')
                        if len(values) >= 2:
                            self.add_exp_cvterm(exp, exp_id, cv1, values[0].strip(), cv2, cvt2)
                            cv1 = self.process_data[key]['cv_mappings'][group_to_key[group]]['pipe_cv']
                            self.add_exp_cvterm(exp, exp_id, cv1, values[1].strip(), cv2, cvt2)
                        else:
                            self.add_exp_cvterm(exp, exp_id, cv1, value, cv2, cvt2)
                    else:
                        self.add_exp_cvterm(exp, exp_id, cv1, value, cv2, cvt2)

            # NOW DO the 'curated as' and 'comment' props
            get_or_create(self.session, FeatureExpressionprop, feature_expression_id=feat_exp_id,
                          type_id=comment_prop.cvterm_id, value=s_res.group(5).strip(), rank=0)
            get_or_create(self.session, FeatureExpressionprop, feature_expression_id=feat_exp_id,
                          type_id=curated_prop.cvterm_id, value=exp[FIELD_VALUE], rank=0)

    def prop(self, key: str) -> None:
        print(f"{key}: prop not programmed yet")

    def delete_prop(self, key: str, bangc: str) -> None:
        print(f"{key}: delete prop not programmed yet")

    def ignore(self, key: str) -> None:
        pass

    def delete_ignore(self, key: str, bangc: str) -> None:
        pass

    def load_content(self, references: dict) -> None:
        """Process the proforma data."""
        self.pub = references['ChadoPub']

        if self.process_data['F1f']['data'][FIELD_VALUE] == "new":
            self.new = True
        self.feature: Union[Feature, None] = self.get_geneproduct()

        if not self.feature:
            self.log.critical("Unable to get geneproduct")
            return
        # if self.Feature:  # Only proceed if we have a gp, Otherwise we had an error.
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

    def load_cvterm(self, key: str) -> None:
        """
        Load the cvterm.
        """
        if self.has_data(key):
            cvterm_name = self.process_data[key]['cvterm']
            name = None
            if cvterm_name == 'in_field':
                cvterm_name, name = self.process_data[key]['data'][FIELD_VALUE].split(';')
                cvterm_name = cvterm_name.strip()
            cvterm = get_cvterm(self.session, self.process_data[key]['cv'], cvterm_name)
            if not cvterm:
                message = 'Cvterm lookup failed for cv {} cvterm {}?'.format(self.process_data[key]['cv'],
                                                                             cvterm_name)
                self.critical_error(self.process_data[key]['data'], message)
                return
            feat_cvterm, _ = get_or_create(self.session, FeatureCvterm,
                                           feature_id=self.feature.feature_id,
                                           cvterm_id=cvterm.cvterm_id,
                                           pub_id=self.pub.pub_id)
            if 'prop_cvterm' in self.process_data[key]:
                prop_cvterm = get_cvterm(self.session, self.process_data[key]['prop_cv'],
                                         self.process_data[key]['prop_cvterm'])
                if not prop_cvterm:
                    message = 'Cvterm lookup failed for cv {} cvterm {}?'.format(self.process_data[key]['prop_cv'],
                                                                                 self.process_data[key]['prop_cvterm'])
                    self.critical_error(self.process_data[key]['data'], message)
                    return
                get_or_create(self.session, FeatureCvtermprop, feature_cvterm_id=feat_cvterm.feature_cvterm_id,
                              type_id=prop_cvterm.cvterm_id)

    def delete_cvterm(self, key: str, bangc: str) -> None:
        cvterm_name = self.process_data[key]['cvterm']
        cv_name = self.process_data[key]['cv']
        if cvterm_name == 'in_field':
            # need to delete all with that cv
            fcvs = self.session.query(FeatureCvterm).join(Cvterm).join(Cv).\
                filter(FeatureCvterm.feature_id == self.feature.feature_id,
                       Cv.name == cv_name,
                       FeatureCvterm.pub_id == self.pub.pub_id).all()
            for fcv in fcvs:
                self.session.delete(fcv)
            return
        # Delete those with cv and cvterm stated.
        cvterm = get_cvterm(self.session, cv_name, cvterm_name)

        fcvs = self.session.query(FeatureCvterm).join(Cvterm). \
            filter(FeatureCvterm.feature_id == self.feature.feature_id,
                   FeatureCvterm.cvterm_id == cvterm.cvterm_id,
                   FeatureCvterm.pub_id == self.pub.pub_id).all()
        for fcv in fcvs:
            self.session.delete(fcv)

    def check_for_existing_geneproduct(self, status: dict) -> None:
        """For a new gene product, confirm there is not already a feature by that name."""
        gp_rgx = r'^FB[a-z][a-z][0-9]+$'
        fbog_rgx = r'^FBog[0-9]+$'
        filters = (
            Feature.is_obsolete.is_(False),
            Feature.uniquename.op('~')(gp_rgx),
            Feature.uniquename.op('!~')(fbog_rgx),
            Feature.name == status['name'],
        )
        existing_feature = self.session.query(Feature).filter(*filters).one_or_none()
        if existing_feature:
            message = f"F1f says that {status['name']} is new, but a feature by this name already exists with ID {existing_feature.uniquename}"
            self.critical_error(self.process_data['F1f']['data'], message)
            status['error'] = True

    def check_format(self, status: dict) -> None:
        """
        Check the format of the new geneproduct name.
        Create critical error message on error and set the dict status['error'] to True.
        Code should check this at the end.
        """
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

    def check_type(self, status: dict) -> None:
        """
        Check the type given by F3 of the new geneproduct name.
        Create critical error  message on error and set the dict status['error'] to True.
        Code should check this at the end.
        """
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

    def check_type_name(self, status: dict) -> None:
        """
        Check the type name of the new geneproduct name.
        Create critical error  message on error and set the dict status['error'] to True.
        Code should check this at the end.
        """
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

    def get_feats(self, status: dict) -> None:
        r"""
        Lookup the features from the base name/s and store the feature_id's in the array
        status['features'].

        example 1) for gpt1[Clk1]RA
            gpt1[Clk1] is looked up in the database and status['features'] will have a one element array
            with its feature_id in it.

        example 2) for Scer\GAL4[DBD.hb2]&cap;Hsap\RELA[AD.pxn2]
            Scer\GAL4[DBD.hb2] and Hsap\RELA[AD.pxn2] are looked up in the database and both feature_id's
            will be stored in the status['features'].

        Create critical error  message on error and set the dict status['error'] to True.
        Code should check this at the end.
        """
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
            feature = feature_name_lookup(self.session, name=feat, obsolete='f')
            if feature:
                log.debug(f"Feature lookup found: {feat}")
                status['features'].append(feature.feature_id)
            else:
                message = f"Could not find feature {feat} in the database to add the feature relationship"
                self.critical_error(self.process_data['F1a']['data'], message)
                status["error"] = True

    def get_uniquename_and_checks(self) -> dict:
        """ Lots of checks
          return dict of :-

          error: [True/False]
          features : [features producing this new product]  # NOTE 2 of these for splits
          fb_prefix: string (FBxx)
          feat_type: cvterm object
          type_name: string (type of geneproduct)
        """
        status = {'error': False,
                  'name': self.process_data['F1a']['data'][FIELD_VALUE]}
        self.check_for_existing_geneproduct(status)
        self.check_format(status)
        self.check_type(status)
        self.check_type_name(status)
        self.get_feats(status)

        return status

    def add_feat_relationships(self, status: dict) -> None:
        """
        Add the feature relationship(s) between the new geneproduct and its component(s)
        status['features'] has the list of feature_id's for this.
        """
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

    def get_org(self: ChadoFeatureObject, status: dict) -> Organism:
        """
        Find the organism for the new geneproduct.
        NOTE: For 'split system combination' this is always 'Ssss'
        """
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

    def get_geneproduct(self) -> Union[Feature, None]:
        """
        Lookup or create the gene product.
        On error give critical error message and return None.
        On success return the Feature object.
        """
        if self.new:

            # get type/uniquename from F3.
            status = self.get_uniquename_and_checks()
            if status['error']:
                self.log.critical(f"Error get gene product {status['error']}")
                return
            organism = self.get_org(status)
            gp, _ = get_or_create(self.session, Feature, name=self.process_data['F1a']['data'][FIELD_VALUE],
                                  organism_id=organism.organism_id, uniquename=f'{status["fb_prefix"]}:temp_0',
                                  type_id=status['feat_type'].cvterm_id)

            # db has correct FBhh0000000x in it but here still has 'FBhh:temp_0'. ???
            # presume triggers start after hh is returned. Maybe worth getting form db again
            log.debug(f"New gene product created {gp.uniquename} id={gp.feature_id}.")

            self.feature = gp
            self.add_feat_relationships(status)
            self.load_synonym('F1a')  # add symbol
            # self.load_synonym('F1a')                       # add fullname HAS NONE
        else:
            not_obsolete = False
            gp = self.session.query(Feature).\
                filter(Feature.uniquename == self.process_data['F1f']['data'][FIELD_VALUE],
                       Feature.is_obsolete == not_obsolete).\
                one_or_none()
            if not gp:
                self.critical_error(self.process_data['F1f']['data'],
                                    'Feature does not exist in the database or is obsolete.')
                return

        # Add to pub to hh if it does not already exist.
        get_or_create(self.session, FeaturePub, pub_id=self.pub.pub_id, feature_id=gp.feature_id)
        return gp
