import re
from typing import Dict, List
from sqlalchemy.orm.exc import NoResultFound

from chado_object.chado_base import FIELD_VALUE, SET_BANG
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
    FeatureRelationshipPub,
    FeatureRelationshipprop,
    FeatureRelationshippropPub
)


def process_sets(self):
    """Process the set data.

    Sets have a specific key, normally the shortened version of the fields
    that it uses. i.e. For SF4a, SF4bb etc this becomes SF4_1.
    self.set_values is a dictionary of these and points to an list of the
    actual values the curators have added i.e. SF4a, SF4b
    This is an example of what the set_values will look like.

    .. code-block:: JSON

        {
          SF4_1: [{'SF4a': ('SF4a', '2L:123..345', 16),
                   'SF4b': ('SF4b', '6', 17)}],
          SF5: [{'SF5a': ('SF5a', 'symbol-2', 22, None),
                 'SF5f': ('SF5f', "The 'associated gene' call is based solely on genomic location.", 23, None)},
                {'SF5a': ('SF5a', 'symbol-3', 24, None)}]
        }
    """
    for key in self.set_values.keys():
        if key == 'SF4_1':
            self.process_sf4_1(self.set_values[key])
        elif key == 'SF4_2':
            self.log.critical("SF4[def] are not implemented. Please see HarvDev if you would like it.")
        elif key == 'SF5':
            self.process_sf5(self.set_values[key])
        else:
            self.log.critical("Unknown set {}".format(key))
            return


def process_sf4_1(self, sets: List[Dict]):
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
        featuresrc, is_new = get_or_create(self.session, Feature, name=arm_name, type_id=arm_type_id, organism_id=self.feature.organism_id)
        if is_new or not featuresrc:
            message = "Could not get {} feature with cvterm {} and cv {}".\
                format(arm_name, self.process_data[key]['arm_cvterm'], self.process_data[key]['arm_cv'])
            self.critical_error(sf4_set['SF4a']['data'], message)

        strand = None
        if 'SF4h' in sf4_set:
            if sf4_set['SF4h'][FIELD_VALUE] == '+':
                strand = 1
            elif sf4_set['SF4h'][FIELD_VALUE] == '-':
                strand = -1
        fl, is_new = get_or_create(self.session, Featureloc,
                                   srcfeature_id=featuresrc.feature_id,
                                   feature_id=self.feature.feature_id,
                                   strand=strand,
                                   locgroup=0)
        fl.fmin = start - 1  # interbase in chado
        fl.fmax = end


def get_feat_rel_for_set(self, sf5_set):
    # look up feature first
    try:
        feature = feature_symbol_lookup(self.session, 'gene', sf5_set['SF5a'][FIELD_VALUE])
    except NoResultFound:
        message = f"Lookup of symbol {sf5_set['SF5a'][FIELD_VALUE]} failed."
        self.critical_error(sf5_set['SF5a'], message)
        return None
    # get feature relationship
    try:
        fr = self.session.query(FeatureRelationship).join(FeatureRelationshipPub).\
            filter(FeatureRelationshipPub.pub_id == self.pub.pub_id,
                   FeatureRelationship.subject_id == self.feature.feature_id,
                   FeatureRelationship.object_id == feature.feature_id).one()
    except NoResultFound:
        message = f"Lookup of relationship between {self.feature.name} and {sf5_set['SF5a'][FIELD_VALUE]} for pub {self.pub.uniquename} failed."
        self.critical_error(sf5_set['SF5a'], message)
        return None
    return fr


def bang_remove_sf5(self, sets):
    """ props props for a specific feat_rel defined in set """
    for sf5_set in sets:
        # get feature relationships
        frs = self.session.query(FeatureRelationshipPub).join(FeatureRelationship).\
            filter(FeatureRelationshipPub.pub_id == self.pub.pub_id,
                   FeatureRelationship.subject_id == self.feature.feature_id)
        okay = False
        key = 'SF5a'
        for fr in frs:
            if not self.check_types(key, fr, ['FBgn']):
                continue
            else:
                okay = True
                self.session.delete(fr)
        if not okay:
            message = f"Lookup of relationship between {self.feature.name} and pub {self.pub.uniquename} failed."
            self.critical_error(sf5_set['SF5a'], message)


def bang_alter_sf5(self, sets):
    """ Alter props for a specific feat_rel defined in set """
    for sf5_set in sets:
        fr = self.get_feat_rel_for_set(sf5_set)
        if not fr:
            return
        set_key = 'SF5'
        for key_name in ['SF5e', 'SF5f']:
            if key_name == 'SF5e':
                prop_cv = 'conf_cv'
                prop_cvterm = 'conf_cvterm'
            else:
                prop_cv = 'comment_cv'
                prop_cvterm = 'comment_cvterm'
            if key_name in sf5_set and sf5_set[key_name][SET_BANG]:
                # get the type for the prop
                rel_type_id = self.cvterm_query(self.process_data[set_key][prop_cv],
                                                self.process_data[set_key][prop_cvterm])

                # get feat rel prop
                frs = self.session.query(FeatureRelationshipprop).join(FeatureRelationshippropPub).\
                    filter(FeatureRelationshippropPub.pub_id == self.pub.pub_id,
                           FeatureRelationshipprop.type_id == rel_type_id,
                           FeatureRelationshipprop.feature_relationship_id == fr.feature_relationship_id).all()
                found = False
                for fr in frs:
                    found = True
                    self.session.delete(fr)
                if not found:
                    message = f"No feature relationship prop found for {self.feature.name} and {sf5_set[key_name][FIELD_VALUE]} "
                    message += f"with type {self.process_data[set_key][prop_cvterm]}"
                    self.critical_error(sf5_set['SF5a'], message)


def check_and_process_bangc_set(self, sets: Dict) -> bool:
    """ Check if we have bang operations and if so process them
        and return True to indicate it is done.
        If no bang operations then return False. """
    bang = False
    remove = False  # remove the relationship
    alter = False   # alter prop for relationship
    for sf5_set in sets:
        if sf5_set['SF5a'][SET_BANG]:
            bang = True
            remove = True
        if 'SF5e' in sf5_set and sf5_set['SF5e'][SET_BANG]:
            bang = True
            alter = True
        if 'SF5f' in sf5_set and sf5_set['SF5f'][SET_BANG]:
            bang = True
            alter = True
    if not bang:
        return False
    if remove and alter:
        message = "Cannot bang SF5a and SF5e or SF5f at the same time."
        self.critical_error(sets[0]['SF5a'], message)
        return True
    if alter:
        self.bang_alter_sf5(sets)
        return True
    self.bang_remove_sf5(sets)
    return True


def process_sf5(self, sets: Dict):
    """
    sets comprise only of a ,e ,f
    a is the gene symbol,
    e is the confidence rating,
    f is the comment.
    """

    symbol_key = 'SF5a'
    conf_key = 'SF5e'
    comment_key = 'SF5f'
    rel_type_id = self.cvterm_query(self.process_data['SF5']['cv'],
                                    self.process_data['SF5']['cvterm'])

    self.log.debug(f"BOB: {sets}")
    self.check_and_process_bangc_set(sets)

    for sf5_set in sets:
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
        # add the fr pub
        frp, _ = get_or_create(self.session, FeatureRelationshipPub,
                               feature_relationship_id=fr.feature_relationship_id,
                               pub_id=self.pub.pub_id)

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
            # Add feature_relationshippropPub ????

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
