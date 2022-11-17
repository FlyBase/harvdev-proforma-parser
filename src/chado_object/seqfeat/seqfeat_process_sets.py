import re
from typing import Dict, List
from sqlalchemy.orm.exc import NoResultFound

from chado_object.chado_base import FIELD_VALUE
from harvdev_utils.chado_functions import (
    get_or_create,
    feature_symbol_lookup
)
from harvdev_utils.production import (
    Feature,
    Featureloc,
    Featureprop,
    FeaturepropPub,
    FeatureRelationship,
    FeatureRelationshipprop
)


def process_sets(self):
    """Process the set data.

    Sets have a specific key, normally the shortened version of the fields
    that it uses. i.e. For SF4a, SF4bb etc this becomes SF4.
    self.set_values is a dictionary of these and points to an list of the
    actual values the curators have added i.e. SF4a, SF4b
    This is an example of what the set_values will look like.

    .. code-block:: JSON

        {
          SF4: [{'SF4a': ('SF4a', '2L:123..345', 16),
                 'SF4b': ('SF4b', '6', 17)}],
          SF5: [{'SF5a': ('SF5a', 'symbol-2', 22, None),
                 'SF5f': ('SF5f', "The 'associated gene' call is based solely on genomic location.", 23, None)},
                {'SF5a': ('SF5a', 'symbol-3', 24, None)}]
        }
    """
    for key in self.set_values.keys():
        self.log.debug("SV: {}: {}".format(key, self.set_values[key]))
        if key == 'SF4_1':
            self.process_sf4_1(self.set_values[key])
        elif key == 'SF4_2':
            self.log.critical("SF4[def] are not implemented. Please see HarvDev if you would like it.")
        elif key == 'SF5':
            self.log.debug("process SF5")
            self.process_sf5(self.set_values[key])
        else:
            self.log.critical("Unknown set {}".format(key))
            return


def process_sf4_1(self, sets: List[Dict]):
    self.log.debug(f"{sets}")
    prop_cv_id = self.cvterm_query(self.process_data['SF4_1']['cv'],
                                   self.process_data['SF4_1']['cvterm'])

    for sf4_set in sets:
        release = sf4_set['SF4b'][FIELD_VALUE]
        loc = sf4_set['SF4a'][FIELD_VALUE]
        pattern = r"""
        ^\s*          # possible spaces
        (\S+)         # arm
        :             # chrom separator
        (\d+)         # start pos
        [.]{2}        # double dots
        (\d+)         # end pos
        (\S*)         # possible stand info ':-1', '-1', '--1' ? siilare for +ve strand
        $
        """
        s_res = re.search(pattern, loc, re.VERBOSE)
        if s_res:  # matches the pattern above
            arm_name = s_res.group(1)
            start = int(s_res.group(2))
            end = int(s_res.group(3))
        else:
            message = r'Incorrect format should be chrom:\d+..\d+'
            self.critical_error(sf4_set, message)
            return
        new_value = f"{arm_name}_r{release}:{start-1}..{end}"

        fp, is_new = get_or_create(self.session, Featureprop, feature_id=self.feature.feature_id,
                                   type_id=prop_cv_id, value=new_value)
        get_or_create(self.session, FeaturepropPub, featureprop_id=fp.featureprop_id, pub_id=self.pub.pub_id)

        # Now create the featureloc
        key = 'SF4_1'
        arm_type_id = self.cvterm_query(self.process_data[key]['arm_cv'], self.process_data[key]['arm_cvterm'])
        featuresrc, is_new = get_or_create(self.session, Feature, name=arm_name, type_id=arm_type_id)
        if is_new or not featuresrc:
            message = "Could not get {} feature with cvterm {} and cv {}".\
                format(arm_name, self.process_data[key]['arm_cvterm'], self.process_data[key]['arm_cv'])
            self.critical_error(sf4_set['SF4a']['data'], message)

        fl, is_new = get_or_create(self.session, Featureloc,
                                   srcfeature_id=featuresrc.feature_id,
                                   feature_id=self.feature.feature_id,
                                   locgroup=0)
        fl.fmin = start - 1  # interbase in chado
        fl.fmax = end


def process_sf4_2(self, sets: List[Dict]):
    self.log.debug(f"{sets}")
    pass


def process_sf5(self, sets: Dict):
    """
    sets comprise only of a ,e ,f
    a is the gene symbol,
    e is the confidence rating,
    f is the comment.
    """
    self.log.debug(f"{sets}")

    symbol_key = 'SF5a'
    conf_key = 'SF5e'
    comment_key = 'SF5f'
    rel_type_id = self.cvterm_query(self.process_data['SF5']['cv'],
                                    self.process_data['SF5']['cvterm'])

    for sf5_set in sets:
        self.log.debug(f"{sf5_set}")
        gene_symbol = sf5_set[symbol_key][FIELD_VALUE]
        try:
            feature = feature_symbol_lookup(self.session, 'gene', gene_symbol)
        except NoResultFound:
            message = f"Could not find gene with symbol {gene_symbol}"
            self.critical_error(sf5_set[symbol_key]['data'], message)
            return
        # create the feature_relationship
        fr, _ = get_or_create(self.session, FeatureRelationship,
                              object_id=feature.feature_id,
                              subject_id=self.feature.feature_id,
                              type_id=rel_type_id)

        # add props for this if specified.
        if conf_key in sf5_set and sf5_set[conf_key][FIELD_VALUE]:
            # add feature_relationshipprop
            conf_prop_id = self.cvterm_query(self.process_data['SF5']['conf_cv'],
                                             self.process_data['SF5']['conf_cvterm'])
            frp, _ = get_or_create(
                self.session,
                FeatureRelationshipprop,
                feature_relationship_id=fr.feature_relationship_id,
                type_id=conf_prop_id,
                value=sf5_set[conf_key][FIELD_VALUE])
        if comment_key in sf5_set and sf5_set[comment_key][FIELD_VALUE]:
            # add feature_relationshipprop
            comm_prop_id = self.cvterm_query(self.process_data['SF5']['comment_cv'],
                                             self.process_data['SF5']['comment_cvterm'])
            frp, _ = get_or_create(
                self.session,
                FeatureRelationshipprop,
                feature_relationship_id=fr.feature_relationship_id,
                type_id=comm_prop_id,
                value=sf5_set[comment_key][FIELD_VALUE])
