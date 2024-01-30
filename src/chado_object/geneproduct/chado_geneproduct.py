# -*- coding: utf-8 -*-
"""Chado Feature/Feature main module.

.. moduleauthor:: Ian Longden <ilongden@morgan.harvard.edu>
                  Gil dos Santos <dossantos@morgan.harvard.edu>
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
from harvdev_utils.char_conversions import (
    sgml_to_plain_text, sgml_to_unicode, sub_sup_to_sgml
)
from sqlalchemy.orm.exc import MultipleResultsFound
# from error.error_tracking import CRITICAL_ERROR


log = logging.getLogger(__name__)


class ChadoGeneProduct(ChadoFeatureObject):
    """Class object for Chado GeneProduct/Feature.

    Main chado object is a Feature.
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
        # Set up how to process each type of input
        # This is set in the geneproduct.yml file.
        ##########################################
        self.type_dict = {'cvterm': self.load_cvterm,
                          'marker_cvterms': self.load_marker_cvterms,
                          'synonym': self.load_synonym,
                          'ignore': self.ignore,
                          'prop': self.load_featureprop,
                          'feat_relationship': self.load_feat_relationship,
                          'expression': self.expression,
                          'relationship': self.todo,    # diff from feat_relationship
                          'merge': self.todo,
                          'rename': self.rename,
                          'disspub': self.dissociate_from_pub,
                          'obsolete': self.make_obsolete,
                          'no_idea': self.todo,    # do not know what it does yet
                          'size': self.todo}

        self.delete_dict = {'ignore': self.delete_ignore,
                            'marker_cvterms': self.delete_marker_cvterms,
                            'synonym': self.delete_synonym,
                            'prop': self.delete_featureprop,
                            'gene': self.delete_ignore,
                            'expression': self.delete_ignore}

        self.proforma_start_line_number = params.get('proforma_start_line_number')

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
        message = f"{key}: not programmed yet"
        print(message)
        self.critical_error(self.process_data[key]['data'], message)
        pass

    def rename(self, key):
        """Rename the geneproduct."""
        # Determine the ASCII and Unicode versions of the symbol to use for the rename.
        ascii_name = sgml_to_plain_text(self.process_data['F1a']['data'][FIELD_VALUE])
        unicode_name = sgml_to_unicode(sub_sup_to_sgml(self.process_data['F1a']['data'][FIELD_VALUE]))
        # Check that the new symbol specified is available for use.
        status = {
            'name': ascii_name,
            'error': False,
        }
        self.check_for_existing_geneproduct(status)
        if status['error'] is True:
            return
        # Set all current feature_synonym entries to be non-current.
        symbol_cvterm = get_cvterm(self.session, self.process_data[key]['cv'], self.process_data[key]['cvterm'])
        filters = (
            FeatureSynonym.feature_id == self.feature.feature_id,
            FeatureSynonym.is_current.is_(True),
            Synonym.type_id == symbol_cvterm.cvterm_id
        )
        fss = self.session.query(FeatureSynonym).\
            join(Synonym).\
            filter(*filters).all()
        for fs in fss:
            fs.is_current = False
        # Update the Feature itself.
        self.feature.name = ascii_name
        # Get/create the new symbol synonym.
        synonym, _ = get_or_create(self.session, Synonym, type_id=symbol_cvterm.cvterm_id,
                                   name=ascii_name, synonym_sgml=unicode_name)
        # Update the feature_synonym table.
        pub_ids = [self.pub.pub_id]
        pub_ids.append(self.get_unattrib_pub().pub_id)
        for pub_id in pub_ids:
            feat_syno, created = get_or_create(self.session, FeatureSynonym, feature_id=self.feature.feature_id,
                synonym_id=synonym.synonym_id, pub_id=pub_id)
        # Catch cases where the geneproduct is renamed to a previously existing symbol.
        if created is False:
            feat_syno.is_current = True
        return

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
        self.feature = self.get_geneproduct()

        if not self.feature:
            self.log.critical("Unable to get geneproduct")
            return

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
        return self.feature

    def load_cvterm(self, key: str) -> None:
        """
        Load a single cvterm by name (ignoring the curated ID): e.g., fields F2 and F3.
        """
        if self.has_data(key):
            cvterm_name = self.process_data[key]['cvterm']
            cvterm = get_cvterm(self.session, self.process_data[key]['cv'], cvterm_name)
            if not cvterm:
                message = f'Cvterm lookup failed for cv {self.process_data[key]["cv"]} cvterm {cvterm_name}.'
                self.critical_error(self.process_data[key]['data'], message)
                return
            _, _ = get_or_create(self.session, FeatureCvterm,
                                 feature_id=self.feature.feature_id,
                                 cvterm_id=cvterm.cvterm_id,
                                 pub_id=self.pub.pub_id)

    def load_marker_cvterms(self, key: str) -> None:
        """
        Load the marker cvterms, ensuring for each curated CV term name and ID pair that the values match up.
        """
        if self.has_data(key) is False:
            return
        # Support for various possible CVs.
        cvs_to_use = self.process_data[key]['cv']
        if type(cvs_to_use) == str:
            cvs_to_use = [cvs_to_use]
        db_cv_lookup = {
            'FBbt': 'FlyBase anatomy CV',
            'GO': 'cellular_component'
        }
        # Process CV term entries as a list of tuples (CVTERM_NAME, CVTERM_CURIE).
        CVTERM_NAME = 0
        CVTERM_CURIE = 1
        cvterm_entry_list = []
        cvterm_curie_regex = r'^(\w+):(\d+)$'
        for curated_entry in self.process_data[key]['data']:
            try:
                cvterm_name, cvterm_curie = curated_entry[FIELD_VALUE].split(';')
                cvterm_entry_list.append((cvterm_name.strip(), cvterm_curie.strip()))
            except ValueError:
                message = f'Curated entry "{curated_entry[FIELD_VALUE]}" did not meet expected format of CV term name ; CV term ID'
                self.critical_error(curated_entry, message)
        for cvterm_entry in cvterm_entry_list:
            cvterm_name = cvterm_entry[CVTERM_NAME]
            curated_cvterm_curie = cvterm_entry[CVTERM_CURIE]
            # Check that the CV term ID (curie) is of the expected format.
            if not re.search(cvterm_curie_regex, curated_cvterm_curie):
                message = f'CV term curie "{curated_cvterm_curie}" does not match expected format of DB:ACCESSION'
                self.critical_error(curated_entry, message)
                continue
            cvterm_db = re.search(cvterm_curie_regex, curated_cvterm_curie).group(1)
            # Check that the CV term ID (curie) is for an allowed ID/curie set.
            try:
                cvterm_cv = db_cv_lookup[cvterm_db]
            except KeyError:
                message = f'CV term curie "{curated_cvterm_curie}" given is not from the allowed list: {list(db_cv_lookup.keys())}'
                self.critical_error(curated_entry, message)
                continue
            cvterm = get_cvterm(self.session, cvterm_cv, cvterm_name)
            # Check that a CV term was found in chado.
            if not cvterm:
                message = f'CV term lookup failed for cv="{cvterm_cv}", cvterm="{cvterm_name}".'
                self.critical_error(curated_entry, message)
                continue
            # Check that the CV term curie/ID in chado matches the ID/curie that was curated.
            chado_cvterm_curie = f'{cvterm.dbxref.db.name}:{cvterm.dbxref.accession}'
            if chado_cvterm_curie != curated_cvterm_curie:
                message = f'For "{cvterm_name}", the curated ID "{curated_cvterm_curie}" does not match the chado ID "{chado_cvterm_curie}".'
                self.critical_error(curated_entry, message)
                continue
            # Create the feature_cvterm entry.
            feat_cvterm, _ = get_or_create(self.session, FeatureCvterm,
                                           feature_id=self.feature.feature_id,
                                           cvterm_id=cvterm.cvterm_id,
                                           pub_id=self.pub.pub_id)
            prop_cvterm = get_cvterm(self.session, self.process_data[key]['prop_cv'], self.process_data[key]['prop_cvterm'])
            if not prop_cvterm:
                message = f'CV term lookup failed for cv="{self.process_data[key]["prop_cv"]}", '
                message += f'cvterm="{self.process_data[key]["prop_cvterm"]}.'
                self.critical_error(curated_entry, message)
                continue
            get_or_create(self.session, FeatureCvtermprop, feature_cvterm_id=feat_cvterm.feature_cvterm_id,
                          type_id=prop_cvterm.cvterm_id)
        return

    def delete_marker_cvterms(self, key: str, bangc: str) -> None:
        """Delete marker CV terms for a given pub."""
        filters = (
            Cvterm.name == 'bodypart_expression_marker',
            Pub.pub_id == self.pub.pub_id,
        )
        fcvs = self.session.query(FeatureCvterm).\
            select_from(FeatureCvterm).\
            join(Pub, (Pub.pub_id == FeatureCvterm.pub_id)).\
            join(FeatureCvtermprop, (FeatureCvtermprop.feature_cvterm_id == FeatureCvterm.feature_cvterm_id)).\
            join(Cvterm, (Cvterm.cvterm_id == FeatureCvtermprop.type_id)).\
            filter(*filters).\
            all()
        if not fcvs:
            gp_name = self.process_data['F1a']['data'][FIELD_VALUE]
            gp_id = self.process_data['F1f']['data'][FIELD_VALUE]
            message = f'No bodypart expression markers curated for {gp_name} ({gp_id}) in {self.pub.uniquename}.'
            self.critical_error(self.process_data[key]['data'], message)
            return
        for fcv in fcvs:
            self.session.delete(fcv)
        return

    def check_for_existing_geneproduct(self, status: dict) -> None:
        """For a new or renamed gene product, confirm there is not already a feature by that name."""
        gp_rgx = r'^FB[a-z][a-z][0-9]+$'
        fbog_rgx = r'^FBog[0-9]+$'
        feature_name = sgml_to_plain_text(status['name'])
        filters = (
            Feature.is_obsolete.is_(False),
            Feature.uniquename.op('~')(gp_rgx),
            Feature.uniquename.op('!~')(fbog_rgx),
            Feature.name == feature_name,
        )
        # Determine if a merge is involved, and the features being merged, as this affects the check.
        merge = self.has_data('F1c')
        features_to_merge = []
        gene_product_regex = r'^FB(tr|pp|co)[0-9]{7}$'
        if merge is True:
            for datum in self.process_data['F1c']['data']:
                if re.match(gene_product_regex, datum[FIELD_VALUE]):
                    features_to_merge.append(datum[FIELD_VALUE])
                else:
                    message = f'{datum[FIELD_VALUE]} is not an FB ID.'
                    self.critical_error(datum, message)
                    status['error'] = True
        try:
            existing_feature = self.session.query(Feature).filter(*filters).one_or_none()
            if existing_feature:
                message = f"Name {status['name']} has been used in the database for {existing_feature.uniquename}; "
                # For merges, where a new feature is given the name of a feature involved in the merge.
                if self.new is True and merge is True and existing_feature.uniquename in features_to_merge:
                    message += "existing feature is involved in the merge."
                    self.warning_error(self.process_data['F1a']['data'], message)
                # For merges, where a new feature is given the name of a feature not involved in the merge.
                elif self.new is True and merge is True and existing_feature.uniquename not in features_to_merge:
                    message += "existing feature is NOT involved in the merge."
                    self.critical_error(self.process_data['F1a']['data'], message)
                    status['error'] = True
                # For new geneproducts (not merges).
                elif self.new is True and merge is False:
                    message += "Cannot re-use a symbol of an existing feature for a new feature."
                    self.critical_error(self.process_data['F1a']['data'], message)
                    status['error'] = True
                # For renamed geneproducts.
                elif self.new is False and 'data' in self.process_data['F1b'] and self.process_data['F1b']['data']:
                    message += "Cannot rename to the symbol of an existing feature."
                    self.critical_error(self.process_data['F1a']['data'], message)
                    status['error'] = True
        except MultipleResultsFound:
            message = f"Name {status['name']} has been used in the database multiple times."
            self.critical_error(self.process_data['F1a']['data'], message)
            status['error'] = True

    def check_format(self, status: dict) -> None:
        """
        Check the format of the new geneproduct name.
        Create critical error  message on error and set the dict status['error'] to True.
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
        Create critical error message on error and set the dict status['error'] to True.
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
                message = f"new split system combination feature {name} typically lists a DBD before an AD;"
                self.warning_error(self.process_data['F1a']['data'], message)

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

    def get_parental_feats(self, status: dict) -> None:
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
            ascii_name = sgml_to_plain_text(feat)
            feature = feature_name_lookup(self.session, name=ascii_name, obsolete='f')
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
          feat_type: Cvterm object
          type_name: string (type of geneproduct)
        """
        status = {'error': False,
                  'name': self.process_data['F1a']['data'][FIELD_VALUE]}
        self.check_for_existing_geneproduct(status)
        self.check_format(status)
        self.check_type(status)
        self.check_type_name(status)
        self.get_parental_feats(status)

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
            get_or_create(self.session, FeatureRelationshipPub, pub_id=pub_id,
                          feature_relationship_id=fr.feature_relationship_id)

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
        Or error give critical error message and return None.
        On success return the Feature object.
        """
        if self.new:
            # get uniquename type from F3.
            status = self.get_uniquename_and_checks()
            if status['error']:
                self.log.critical(f"Error get gene product {status['error']}")
                return
            organism = self.get_org(status)
            gp, _ = get_or_create(self.session, Feature, name=self.process_data['F1a']['data'][FIELD_VALUE],
                                  organism_id=organism.organism_id, uniquename=f'{status["fb_prefix"]}:temp_0',
                                  type_id=status['feat_type'].cvterm_id)
            log.debug(f"New gene product created {gp.uniquename} id={gp.feature_id}.")
            self.feature = gp
            self.add_feat_relationships(status)
            self.load_synonym('F1a')  # add symbol
        else:
            not_obsolete = False
            f1a_name = self.process_data['F1a']['data'][FIELD_VALUE]
            f1a_name_plain_text = sgml_to_plain_text(f1a_name)
            try:
                f1b_name = self.process_data['F1b']['data'][FIELD_VALUE]
                f1b_name_plain_text = sgml_to_plain_text(f1b_name)
            except KeyError:
                f1b_name = None
                f1b_name_plain_text = None
            gp = self.session.query(Feature).\
                filter(Feature.uniquename == self.process_data['F1f']['data'][FIELD_VALUE],
                       Feature.is_obsolete == not_obsolete).\
                one_or_none()
            if not gp:
                self.critical_error(self.process_data['F1f']['data'],
                                    'Feature does not exist in the database or is obsolete.')
                return
            # If not renaming, compare feature.name to F1a entry.
            elif f1b_name_plain_text is None and gp.name != f1a_name_plain_text:
                message = f'Symbol-ID mismatch: the ID given in F1f ({gp.uniquename}) exists'
                message += f' as {gp.name} in Chado, but the name given in F1a is {f1a_name}.'
                self.critical_error(self.process_data['F1f']['data'], message)
                return
            # If renaming, compare feature.name to F1b entry.
            elif f1b_name_plain_text is not None and gp.name != f1b_name_plain_text:
                message = f'Symbol-ID mismatch: the ID given in F1f ({gp.uniquename}) exists'
                message += f' as {gp.name} in Chado, but the name given in F1b is {f1b_name}.'
                self.critical_error(self.process_data['F1f']['data'], message)
                return
        get_or_create(self.session, FeaturePub, pub_id=self.pub.pub_id, feature_id=gp.feature_id)
        return gp
