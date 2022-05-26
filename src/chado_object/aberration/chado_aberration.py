
"""
:synopsis: The Aberration ChadoObject.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>, Ian Longden <ilongden@morgan.harvard.edu>
"""
import logging
import os
import re
from datetime import datetime

from chado_object.chado_base import FIELD_VALUE, FIELD_NAME, LINE_NUMBER
from chado_object.feature.chado_feature import ChadoFeatureObject
# from chado_object.utils.go import process_GO_line
from chado_object.utils.feature_synonym import fs_add_by_synonym_name_and_type
from harvdev_utils.chado_functions import (get_or_create, get_cvterm, feature_name_lookup, get_dbxref,
                                           DataError)
from harvdev_utils.production import (Feature, Featureprop, FeaturepropPub, FeaturePub,
                                      FeatureRelationship, FeatureRelationshipPub,
                                      FeatureGenotype, Environment, Genotype, Phendesc)
# from typing import Tuple, Union
log = logging.getLogger(__name__)


class ChadoAberration(ChadoFeatureObject):
    """ChadoAberration object."""

    from chado_object.aberration.break_point import (
        process_A90, get_breakpoint, add_featloc, add_bk_feat_relationship, add_props
    )

    def __init__(self, params):
        """Initialise the ChadoAberration Object."""
        log.debug('Initializing ChadoAberration object.')

        # Initiate the parent.
        super(ChadoAberration, self).__init__(params)
        ##########################################
        # Set up how to process each type of input
        ##########################################
        self.type_dict = {'synonym': self.load_synonym,
                          'ignore': self.ignore,
                          'cvterm': self.load_feature_cvterm,
                          'featureprop': self.load_featureprop,
                          'featurerelationship': self.load_feature_relationship,
                          'cvtermprop': self.load_feature_cvtermprop,
                          'break_of': self.breaks,
                          'libraryfeatureprop': self.load_lfp,
                          'A90': self.process_A90,
                          # 'merge': self.merge,
                          'phen_desc': self.phen_desc,
                          'dis_pub': self.dis_pub,
                          'make_obsolete': self.make_obsolete,
                          }

        self.delete_dict = {'featureprop': self.delete_featureprop,
                            'synonym': self.delete_synonym,
                            'cvterm': self.delete_feature_cvtermprop}
        self.proforma_start_line_number = params.get('proforma_start_line_number')

        ###########################################################
        # Values queried later, placed here for reference purposes.
        ############################################################
        self.pub = None
        self.type_name = 'aberration'
        ############################################################
        # Get processing info and data to be processed.
        # Please see the yml/publication.yml file for more details
        ############################################################
        yml_file = os.path.join(os.path.dirname(__file__), '../yml/aberration.yml')
        # Populated self.process_data with all possible keys.
        self.process_data = self.load_reference_yaml(yml_file, params)

        ########################################################
        # extra checks that cannit be done with cerberus.
        # Create lookup up to stop a huge if then else statement
        ########################################################
        self.checks_for_key = {'A26':  self.so_alter_check,
                               'A9': self.so_alter_check}

    def phen_desc(self, key):
        # get/create the genotype with same name as aberation
        env, _ = get_or_create(self.session, Environment, uniquename=self.process_data[key]['environment'])
        geno, _ = get_or_create(self.session, Genotype, uniquename=self.feature.name)
        desc_cvterm = get_cvterm(self.session, self.process_data[key]['desc_cv'], self.process_data[key]['desc_cvterm'])
        fg_cvterm = get_cvterm(self.session, self.process_data[key]['cv'], self.process_data[key]['cvterm'])
        chrom_cvterm = get_cvterm(self.session, self.process_data[key]['chrom_cv'], self.process_data[key]['chrom_cvterm'])
        chrom, _ = get_or_create(self.session, Feature,
                                 name=self.process_data[key]['chrom'],
                                 uniquename=self.process_data[key]['chrom'],
                                 type_id=chrom_cvterm.cvterm_id)

        # Add feature genotype
        fg, _ = get_or_create(self.session, FeatureGenotype,
                              chromosome_id=chrom.feature_id,
                              cvterm_id=fg_cvterm.cvterm_id,
                              feature_id=self.feature.feature_id,
                              cgroup=0,
                              genotype_id=geno.genotype_id)

        # Add phen desc for each line in input
        get_or_create(self.session, Phendesc,
                      genotype_id=geno.genotype_id,
                      type_id=desc_cvterm.cvterm_id,
                      environment_id=env.environment_id,
                      pub_id=self.pub.pub_id,
                      description=self.process_data[key]['data'][FIELD_VALUE])

    def so_alter_check(self, key):
        short_to_name = {
            'Df':   'chromosomal_deletion',
            'tDp':  'tandem_duplication',
            'In':   'chromosomal_inversion',
            'T':    'chromosomal_translocation',
            'R':    'ring_chromosome',
            'AS':   'autosynaptic_chromosome',
            'DS':   'dexstrosynaptic_chromosome',
            'LS':   'laevosynaptic_chromosome',
            'fDp':  'free_duplication',
            'fR':   'free_ring_duplication',
            'DfT':  'deficient_translocation',
            'DfIn': 'deficient_inversion',
            'InT':  'inversion_cum_translocation',
            'bDp':  'bipartite_duplication',
            'cT':   'cyclic_translocation',
            'cIn':  'bipartite_inversion',
            'eDp':  'uninverted_insertional_duplication',
            'iDp':  'inverted_insertional_duplication',
            'uDp':  'unoriented_insertional_duplication',
            'eTp1': 'uninverted_intrachromosomal_transposition',
            'eTp2': 'uninverted_interchromosomal_transposition',
            'iTp1': 'inverted_intrachromosomal_transposition',
            'iTp2': 'inverted_interchromosomal_transposition',
            'uTp1': 'unorientated_intrachromosomal_transposition',
            'uTp2': 'unoriented_interchromosomal_transposition'}

        okay = True

        pattern = r"""
                ^           # start of line
                \s*         # possible leading spaces
                (\S+)       # anything excluding spaces
                \s*         # possible spaces
                ;           # separator
                \s*         # possible spaces
                SO:         # dbxref DB must start be SO:
                (\d{7})  # accession 7 digit number i.e. 0000011
        """
        # can be list or single item so make it always a list.
        if type(self.process_data[key]['data']) is list:
            items = self.process_data[key]['data']
        else:
            items = [self.process_data[key]['data']]
        new_tuple_array = []
        for item in items:
            if item[FIELD_VALUE] in short_to_name:
                long_name = short_to_name[item[FIELD_VALUE]]
                new_tuple = (item[FIELD_NAME],
                             long_name,
                             item[LINE_NUMBER])
                new_tuple_array.append(new_tuple)
                continue
            fields = re.search(pattern, item[FIELD_VALUE], re.VERBOSE)
            if not fields:
                message = 'Wrong format should be "none_spaces_name ; SO:[0-9]*7"'
                self.critical_error(item, message)
                continue

            cvterm_name = fields.group(1).strip()
            db_name = 'SO'
            db_acc = fields.group(2)
            cv_name = self.process_data[key]['cv']

            cvterm = get_cvterm(self.session, cv_name, cvterm_name)
            try:
                db_xref = get_dbxref(self.session, db_name, db_acc)
            except DataError:
                message = "Could not find dbxref for db '{}' and accession '{}'".format(db_name, db_acc)
                self.critical_error(item, message)
                okay = False
                continue

            if cvterm.dbxref.dbxref_id != db_xref.dbxref_id:
                message = "'{}' Does not match '{}', lookup gave '{}'".\
                    format(cvterm_name, db_xref.accession, cvterm.dbxref.accession)
                self.critical_error(item, message)
                okay = False
                continue

            new_tuple = (item[FIELD_NAME],
                         cvterm_name,
                         item[LINE_NUMBER])
            new_tuple_array.append(new_tuple)
        if okay:
            self.process_data[key]['data'] = new_tuple_array
        return okay

    def extra_checks(self):
        """Extra checks.

        Ones that are not easy to do via the validator.
        """
        for key in self.process_data:
            if key in self.checks_for_key:
                self.checks_for_key[key](key)

        # cerburus should be dealing with this but it appears not to be.
        # so lets check manually if GA90a does not exist then none of the others should
        okay = True
        if not self.has_data('A90a'):
            for postfix in 'bc':
                postkey = 'A90{}'.format(postfix)
                if self.has_data(postkey):
                    self.critical_error(self.process_data[postkey]['data'], "Cannot set {} without A90a".format(postkey))
                    okay = False
        return okay

    def load_content(self, references: dict):
        """Process the data.

        Args:
            references: <dict> previous reference proforma
        Returns:
            <Feature object> Aberration feature object.
        """
        try:
            self.pub = references['ChadoPub']
        except KeyError:
            message = "Unable to find publication."
            self.critical_error(self.process_data['A1a']['data'], message)
            return None

        self.load_feature(feature_type='chromosome_structure_variation')
        if not self.feature:  # problem getting aberration, lets finish
            return None
        self.extra_checks()
        # feature pub if not dissociate from pub
        if not self.has_data('A27b'):
            get_or_create(self.session, FeaturePub, feature_id=self.feature.feature_id, pub_id=self.pub.pub_id)
        # bang c first as this supersedes all things
        if self.bang_c:
            self.bang_c_it()
        if self.bang_d:
            self.bang_d_it()

        for key in self.process_data:
            log.debug("Processing {}".format(self.process_data[key]['data']))
            if 'type' not in self.process_data[key]:
                self.critical_error(self.process_data[key]['data'],
                                    "No sub to deal type '{}' yet!! Report to HarvDev".format(key))
            self.type_dict[self.process_data[key]['type']](key)

        if self.has_data('A1f'):
            key = 'A1f'
            fs_add_by_synonym_name_and_type(self.session, self.feature.feature_id,
                                            self.feature.name,
                                            self.process_data[key]['cv'],
                                            self.process_data[key]['cvterm'],
                                            self.pub.pub_id
                                            )
            fs_add_by_synonym_name_and_type(self.session, self.feature.feature_id,
                                            self.feature.name,
                                            self.process_data[key]['cv'],
                                            self.process_data[key]['cvterm'],
                                            self.get_unattrib_pub().pub_id
                                            )

        timestamp = datetime.now().strftime('%c')
        curated_by_string = 'Curator: %s;Proforma: %s;timelastmodified: %s' % (self.curator_fullname, self.filename_short, timestamp)
        log.debug('Curator string assembled as:')
        log.debug('%s' % (curated_by_string))
        return self.feature

    def process_tool(self, item, key, break_point, tool_name):
        # lookup tool. Must exist aleady
        cvterm = get_cvterm(self.session, self.process_data[key]['lookup_cv'], self.process_data[key]['lookup_cvterm'])
        tool = feature_name_lookup(
            self.session,
            name=tool_name,
            organism_id=self.feature.organism.organism_id,
            type_id=cvterm.cvterm_id)
        if not tool:
            message = "Could not find name '{}' for type '{}'".format(tool_name, cvterm.name)
            self.critical_error(item, message)
            return

        # create relationship and relationship pub
        cvterm = get_cvterm(self.session, self.process_data[key]['fr_cv'], self.process_data[key]['fr_prog_cvterm'])
        fr, _ = get_or_create(self.session, FeatureRelationship,
                              subject_id=break_point.feature_id,
                              object_id=tool.feature_id,
                              type_id=cvterm.cvterm_id)
        get_or_create(self.session, FeatureRelationshipPub,
                      feature_relationship_id=fr.feature_relationship_id,
                      pub_id=self.pub.pub_id)

    def process_ends(self, item, key, break_point, left, right):
        band_cvterm = get_cvterm(self.session, self.process_data[key]['band_cv'], self.process_data[key]['band_cvterm'])

        left_band, is_new = get_or_create(self.session, Feature,
                                          type_id=band_cvterm.cvterm_id,
                                          name='band-{}'.format(left),
                                          uniquename='band-{}'.format(left),
                                          organism_id=self.feature.organism.organism_id)
        error = False
        if is_new:
            self.critical_error(item, "Could not find '{}' with name '{}'".format(band_cvterm.name, 'band-{}'.format(left)))
            error = True

        right_band, is_new = get_or_create(self.session, Feature,
                                           type_id=band_cvterm.cvterm_id,
                                           name='band-{}'.format(right),
                                           uniquename='band-{}'.format(right),
                                           organism_id=self.feature.organism.organism_id)
        if is_new:
            self.critical_error(item, "Could not find '{}' with name '{}'".format(band_cvterm.name, 'band-{}'.format(right)))
            error = True

        if error:
            return

        # left end
        fr_cvterm = get_cvterm(self.session, self.process_data[key]['end_cv'], self.process_data[key]['left_cvterm'])
        fr, _ = get_or_create(self.session, FeatureRelationship,
                              subject_id=break_point.feature_id,
                              object_id=left_band.feature_id,
                              type_id=fr_cvterm.cvterm_id)
        get_or_create(self.session, FeatureRelationshipPub,
                      feature_relationship_id=fr.feature_relationship_id,
                      pub_id=self.pub.pub_id)

        # right end
        fr_cvterm = get_cvterm(self.session, self.process_data[key]['end_cv'], self.process_data[key]['right_cvterm'])
        fr, _ = get_or_create(self.session, FeatureRelationship,
                              subject_id=break_point.feature_id,
                              object_id=right_band.feature_id,
                              type_id=fr_cvterm.cvterm_id)
        get_or_create(self.session, FeatureRelationshipPub,
                      feature_relationship_id=fr.feature_relationship_id,
                      pub_id=self.pub.pub_id)

    def breaks(self, key):
        # ## Checks: From peeves

        # - each breakpoint is given after the fields starting "1: " "2: " etc.,
        # - each breakpoint must be in the following normal cytological format (similar to G10a.):

        # CHECKS: Values should correspond to known cytological locations which
        # are listed in camgenes.xml section headed <!-- Cytological bands,
        # subdivisions, divisions, heterochromatin, telomeres, centromeres --> a
        # lookup file could be generated.  Each statement must either be a known
        # cytological location or a range between two known cytological locations
        # separated by a -.

        # NB NB NB as well as the above, a break can be given as an FBti symbol,
        # in which case it must already exists as a valid FBti symbol or it must
        # be made so in this curation record

        # NB NB NB as well as the above, a break can be given as [] NB NB NB
        # these should stay as square brackets and not be turned into
        # superscripts on parsing.
        if not self.has_data(key):
            return
        band_pattern = r"""
                ^           # start of line
                \s*         # possible leading spaces
                (\d+)       # rnak integer
                \s*         # possible spaces
                :           # separator
                \s*         # possible spaces
                (\S+)       # left band:
                \s*         # possible spaces
                -           # band separator
                \s*         # possible spaces
                (\S+)       # right band
        """
        ti_pattern = r"""
                ^           # start of line
                \s*         # possible leading spaces
                (\d+)       # rank integer
                \s*         # possible spaces
                :           # separator
                \s*         # possible spaces
                (P\S+)      # TI i.e. P{test}1
        """
        loc = ""
        for item in self.process_data[key]['data']:  # list of values here.
            fields = re.search(band_pattern, item[FIELD_VALUE], re.VERBOSE)
            rank = None
            left = None
            right = None
            tool_name = None
            if not fields:
                fields = re.search(ti_pattern, item[FIELD_VALUE], re.VERBOSE)
                if not fields:
                    message = 'Wrong format should be "\\d+: \\w+-\\w+)" or \\d+: P\\S+'
                    self.critical_error(item, message)
                    continue
                # so we have P* so lookup symbol.
                rank = fields.group(1)
                tool_name = fields.group(2)
                print("lookup {} with a rank of  {}".format(tool_name, rank))
            else:
                rank = fields.group(1)
                left = fields.group(2)
                right = fields.group(3)

            # Create new breakpoint
            new_break_name = "{}:bk{}".format(self.feature.name, rank)
            bk_cvterm = get_cvterm(self.session, self.process_data[key]['feat_cv'], self.process_data[key]['feat_cvterm'])
            break_point, is_new = get_or_create(self.session, Feature,
                                                type_id=bk_cvterm.cvterm_id,
                                                name=new_break_name,
                                                uniquename=new_break_name,
                                                organism_id=self.feature.organism.organism_id)
            get_or_create(self.session, FeaturePub,
                          feature_id=break_point.feature_id,
                          pub_id=self.pub.pub_id)

            # add relationship and feat pub to break_point
            fr_cvterm = get_cvterm(self.session, self.process_data[key]['fr_cv'], self.process_data[key]['fr_break_cvterm'])
            fr, _ = get_or_create(self.session, FeatureRelationship,
                                  subject_id=break_point.feature_id,
                                  object_id=self.feature.feature_id,
                                  type_id=fr_cvterm.cvterm_id)
            get_or_create(self.session, FeatureRelationshipPub,
                          feature_relationship_id=fr.feature_relationship_id,
                          pub_id=self.pub.pub_id)
            #   self.add_relationships(key, break_point, fr_cvterm)

            if tool_name:
                self.process_tool(item, key, break_point, tool_name)
            elif left:
                self.process_ends(item, key, break_point, left, right)
            # add left and right and loc if required.
            if left and right:
                loc += '[' + left + '-' + right + '];'

        if loc:
            loc_cvterm = get_cvterm(self.session, self.process_data[key]['loc_cv'], self.process_data[key]['loc_cvterm'])
            fp, _ = get_or_create(self.session, Featureprop,
                                  feature_id=self.feature.feature_id,
                                  type_id=loc_cvterm.cvterm_id,
                                  value=loc)
            get_or_create(self.session, FeaturepropPub, featureprop_id=fp.featureprop_id, pub_id=self.pub.pub_id)

    def ignore(self, key):
        """Ignore."""
        pass

    def ignore_bang(self, key, bangc):
        """Ignore."""
        pass


# my %a30a_type = ('experimental_result', 1 , 'member_of_reagent_collection', 1);

# my %feat_type = ('A24a','transposable_element_insertion_site',
# 		 'A30','library',
#                 );
# my %featid_type = ('A24a','ti', 'A30','lc');

# my %proptype = ( 'A9', 'aberr_class', 'A26', 'wt_class', 'A4', 'webcv' );
