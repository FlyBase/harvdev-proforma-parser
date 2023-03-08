from harvdev_utils.production import Feature, FeaturePub
from chado_object.feature.chado_feature import FIELD_VALUE, ChadoFeatureObject
from harvdev_utils.char_conversions import sgml_to_plain_text
from harvdev_utils.chado_functions import (
    feature_name_lookup,
    get_or_create)


def get_exp_tool(self):
    """Get initial Exp Tool and check."""
    # NOTE: new 'SO' will be 'engineered_region' when it come in
    exptool_cvterm_id = self.cvterm_query(self.process_data['TO1f']['cv'], self.process_data['TO1f']['cvterm'])

    if not self.new:  # Fetch by FBTO and check TO1a ONLY
        self.fetch_by_FBto_and_check(exptool_cvterm_id)
        if not self.has_data('TO1i'):
            feature_pub, _ = get_or_create(self.session, FeaturePub,
                                           feature_id=self.feature.feature_id,
                                           pub_id=self.pub.pub_id)
        return
    else:  # new check it does not exists already
        exists = self.check_existing_already()
        if exists:
            return
    exists_already = self.check_existing_already()
    if exists_already:
        self.feature = exists_already
        if not self.has_data('TO1i'):
            feature_pub, _ = get_or_create(self.session, FeaturePub, feature_id=self.feature.feature_id,
                                           pub_id=self.pub.pub_id)
        return

    name = sgml_to_plain_text(self.process_data['TO1a']['data'][FIELD_VALUE])

    self.feature, _ = get_or_create(self.session, Feature, organism_id=self.organism_id,
                                    name=name,
                                    type_id=exptool_cvterm_id,
                                    uniquename='FBto:temp_0')

    self.log.debug("New Exp Tool entry created: {}".format(self.feature.name))


def fetch_by_FBto_and_check(self: ChadoFeatureObject, cvterm_id: int) -> None:
    """Fetch by the FBto (TO1f) and check the name is the same if it is given (TO1a).

    Args:
        cvterm_id (int): cvterm_id to be used as type in getting feature.

    Raises:
        critical error if TO1f and TO1a are specified and do not match.
    """

    self.feature, is_new = get_or_create(self.session, Feature, type_id=cvterm_id,
                                         organism_id=self.organism_id,
                                         uniquename=self.process_data['TO1f']['data'][FIELD_VALUE])
    if self.feature.is_obsolete:
        message = "{} is obsolete set TO1a to 'new' to re-add it.".format(self.process_data['TO1f']['data'][FIELD_VALUE])
        self.critical_error(self.process_data['TO1f']['data'], message)
        return

    if is_new:
        message = "Could not find {} in the database. Please check it exists and you have the correct organism.".\
            format(self.process_data['TO1f']['data'][FIELD_VALUE])
        self.critical_error(self.process_data['TO1f']['data'], message)
    if self.has_data('TO1a'):
        if sgml_to_plain_text(self.process_data['TO1a']['data'][FIELD_VALUE]) != self.feature.name:
            message = "Name given does not match that in database. {} does not equal {}".\
                format(self.process_data['TO1f']['data'][FIELD_VALUE],
                       self.feature.name)
            self.critical_error(self.process_data['TO1a']['data'], message)


def check_existing_already(self):
    """Check if we already have an existing entry.
    """
    entry_already_exists = None

    #
    # check Flybase name if given
    #
    if self.has_data('TO1a'):
        entry_already_exists = self.exptool_feature_lookup(self.organism_id, 'TO1a', self.process_data['TO1a']['data'][FIELD_VALUE], current=True)
        if entry_already_exists and self.new:
            self.critical_error(self.process_data['TO1a']['data'], "Already exists but specified as new.")
            return True
        if entry_already_exists:
            return True


def exptool_feature_lookup(self, organism_id, key_name, name, current=True):
    """Lookup the exp tool feature."""
    entry = None
    name = sgml_to_plain_text(name)
    if current:
        entry = feature_name_lookup(self.session, name,
                                    organism_id=self.organism_id, type_name=self.type_name)
    # else:
    #     try:
    #         features = feature_synonym_lookup(self.session, self.type_name,
    #                                           name.lower(),
    #                                           organism_id=self.organism_id)
    #     except DataError:
    #         return entry
        # if features:
        #     message = "Synonym found for this already: Therefore not reloading Exp Tool but using existing one {}.".format(features[0].name)
        #     self.log.debug(message)
        #     return features[0]
    return entry
