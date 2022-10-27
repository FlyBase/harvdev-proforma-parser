from sqlalchemy.orm.exc import NoResultFound
from chado_object.feature.chado_feature import FIELD_VALUE
from harvdev_utils.production import Feature
from harvdev_utils.chado_functions import get_or_create, get_default_organism_id


def merge(self):
    organism_id = get_default_organism_id(self.session)
    chemical_cvterm_id = self.cvterm_query(self.process_data['CH1f']['cv'], self.process_data['CH1f']['cvterm'])
    if self.process_data['CH1f']['data'][FIELD_VALUE] == "new":

        self.feature, _ = get_or_create(self.session, Feature, organism_id=organism_id,
                                        type_id=chemical_cvterm_id,
                                        name=self.process_data['CH1a']['data'][FIELD_VALUE],
                                        uniquename='FBch:temp_0')
    else:
        self.feature = self.session.query(Feature).filter(Feature.uniquename == self.process_data['CH1f']['data'][FIELD_VALUE]).one()

    for feature_uniquename in self.process_data['CH1g']['data']:
        self.log.debug(f"Processing {feature_uniquename[FIELD_VALUE]}")
        try:
            feature = self.session.query(Feature).filter(Feature.uniquename == feature_uniquename[FIELD_VALUE]).one()
        except NoResultFound:
            self.critical_error(feature_uniquename[FIELD_VALUE], "Could not find '{}' in uniquename lookup.".format(feature_uniquename[FIELD_VALUE]))
        # log.debug("Chemical to be merged is {}".format(feature))
        feature.is_obsolete = True
        # Transfer synonyms
        self.transfer_synonyms(feature)
        # Transfer cvterms
        self.transfer_cvterms(feature)
        # Transfer dbxrefs
        self.transfer_dbxrefs(feature)
