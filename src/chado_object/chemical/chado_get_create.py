from chado_object.feature.chado_feature import FIELD_VALUE, ChadoFeatureObject
from harvdev_utils.chado_functions import (
    DataError,
    feature_name_lookup,
    feature_synonym_lookup,
    get_default_organism_id,
    get_or_create)
from harvdev_utils.char_conversions import sgml_to_plain_text
from harvdev_utils.production import (
    Db,
    Dbxref,
    Feature,
    FeaturePub)


def get_or_create_chemical(self):
    """Validate the identifier in an external database.

    Also looks for conflicts between the external name and
    the name specified for FlyBase. It also returns data that we use
    to populate fields in Chado.

    Look up the ChEBI / PubChem reference pub_id's.
    Assigns a value to 'self.chebi_pub_id' and 'self.pubchem_pub_id'
    """
    self.look_up_static_references()

    # Look up chemical cv term id. Ch1f yaml data for cv and cvterms
    chemical_cvterm_id = self.cvterm_query(self.process_data['CH1f']['cv'], self.process_data['CH1f']['cvterm'])

    if not self.new_chemical_entry:  # Fetch by FBch and check CH1a ONLY
        self.fetch_by_FBch_and_check(chemical_cvterm_id)
        if not self.has_data('CH3g'):
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
        if not self.has_data('CH3g'):
            feature_pub, _ = get_or_create(self.session, FeaturePub, feature_id=self.feature.feature_id,
                                           pub_id=self.pub.pub_id)
        return

    # Look up organism id.
    organism_id = get_default_organism_id(self.session)
    name = sgml_to_plain_text(self.process_data['CH1a']['data'][FIELD_VALUE])

    self.feature, _ = get_or_create(self.session, Feature, organism_id=organism_id,
                                    name=name,
                                    type_id=chemical_cvterm_id,
                                    uniquename='FBch:temp_0')

    self.log.debug("New chemical entry created: {}".format(self.feature.name))


def check_for_dbxref(self, key):
    if self.has_data(key):
        identifier, name = self.split_identifier_and_name(self.process_data[key]['data'][FIELD_VALUE], key)
        feat = self.session.query(Feature).\
            join(Dbxref).\
            join(Db).filter(Db.name == identifier,
                            Dbxref.accession == name).one_or_none()
        if feat:
            self.critical_error(self.process_data[key]['data'], f"Feature {feat.uniquename} Already has {identifier}:{name}")
            return True


def check_existing_already(self):
    """Check if we already have an existing entry.
    Check via name, and also the CH3a (CHEBI, PUBCHEM entry)
    """
    #
    # Look up organism id.
    #
    organism_id = get_default_organism_id(self.session)

    entry_already_exists = None

    #
    # check Flybase name if given
    #
    if self.has_data('CH1a'):

        entry_already_exists = self.chemical_feature_lookup(organism_id, 'CH1a', self.process_data['CH1a']['data'][FIELD_VALUE], current=True)
        if entry_already_exists and self.new_chemical_entry:
            message = f"CH1a claims '{self.process_data['CH1a']['data'][FIELD_VALUE]}' is new"
            message += f" but '{self.process_data['CH1a']['data'][FIELD_VALUE]}' is already known to Chado as {entry_already_exists.uniquename}"
            self.critical_error(self.process_data['CH1a']['data'], message)
            return True
        if entry_already_exists:
            return True

    # Check for chebi/pubchem entry already in db. If set.
    for key in ('CH3a', 'CH3d'):
        if self.has_data(key):
            entry_already_exists = self.check_for_dbxref(key)
            if entry_already_exists and self.new_chemical_entry:
                self.critical_error(self.process_data[key]['data'], f"Already exists (via {key} lookup but specified as new.")
                return True
            if entry_already_exists:
                return True

    return False


def fetch_by_FBch_and_check(self: ChadoFeatureObject, chemical_cvterm_id: int) -> None:
    """Fetch by the FBch (CH1f) and check the name is the same if it is given (CH1a).

    Args:
        chemical_cvterm_id (int): cvterm_id to be used as type in getting feature.

    Raises:
        critical error if CH1f and CH1a are specified and do not match.
    """
    organism_id = get_default_organism_id(self.session)
    self.feature, is_new = get_or_create(self.session, Feature, type_id=chemical_cvterm_id,
                                         organism_id=organism_id,
                                         uniquename=self.process_data['CH1f']['data'][FIELD_VALUE])
    if self.feature and self.feature.is_obsolete:
        message = "{} is obsolete set CH1a to 'new' to re-add it.".format(self.process_data['CH1f']['data'][FIELD_VALUE])
        self.critical_error(self.process_data['CH1f']['data'], message)
        return

    if is_new:
        message = "Could not find {} in the database. Please check it exists.".format(self.process_data['CH1f']['data'][FIELD_VALUE])
        self.critical_error(self.process_data['CH1f']['data'], message)
    if self.feature and self.has_data('CH1a'):
        if sgml_to_plain_text(self.process_data['CH1a']['data'][FIELD_VALUE]) != self.feature.name:
            message = f"Name given does not match that in database. {self.process_data['CH1f']['data'][FIELD_VALUE]} "
            message += f"is {self.feature.name} in chado, but the CH1a value given in the proforma "
            message += f"is {self.process_data['CH1f']['data'][FIELD_VALUE]}"
            self.critical_error(self.process_data['CH1a']['data'], message)


def chemical_feature_lookup(self, organism_id, key_name, name, current=True):
    """Lookup the chemical feature."""
    entry = None
    name = sgml_to_plain_text(name)
    if current:
        entry = feature_name_lookup(self.session, name,
                                    organism_id=organism_id, type_name='chemical entity')
    else:
        try:
            features = feature_synonym_lookup(self.session, 'chemical entity',
                                              name.lower(),
                                              organism_id=organism_id)
        except DataError:
            return entry
        if features:
            message = "Synonym found for this already: Therefore not reloading Chemical Entity but using existing one {}.".format(features[0].name)
            self.log.debug(message)
            return features[0]
    return entry
