"""
:synopsis: The seqfeat ChadoObject.

:moduleauthor: Ian Longden <ilongden@morgan.harvard.edu>
"""
import logging
import os


from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound


from chado_object.chado_base import FIELD_VALUE
from chado_object.feature.chado_feature import ChadoFeatureObject
from harvdev_utils.char_conversions import sgml_to_plain_text

from chado_object.utils.feature_synonym import fs_remove_current_symbol

from harvdev_utils.chado_functions import (
    get_feature_and_check_uname_symbol, CodingError,
    DataError, feature_symbol_lookup, get_or_create)
from harvdev_utils.production import (
    Feature,
    # FeatureCvterm,
    FeaturePub,
    FeatureRelationship)
log = logging.getLogger(__name__)


class ChadoSeqFeat(ChadoFeatureObject):
    """ChadoSeqFeat object."""

    from .seqfeat_process_sets import (
        process_sets,
        process_sf4_1,
        process_sf5,
        check_and_process_bangc_set,
        bang_alter_sf5,
        bang_remove_sf5,
        get_feat_rel_for_set
    )

    def __init__(self, params):
        """Initialise the ChadoSeqFeat Object."""
        log.debug('Initializing ChadoSeqFeat object.')

        # Initiate the parent.
        super(ChadoSeqFeat, self).__init__(params)
        ##########################################
        # Set up how to process each type of input
        ##########################################
        self.type_dict = {'synonym': self.sf_load_synonym,
                          'data_set': self.ignore,
                          'ignore': self.ignore,
                          'addprimer': self.addprimer,
                          'residues': self.add_residues,
                          'cvterm': self.load_feature_cvterm,
                          'cvtermprop': self.load_feature_cvtermprop,
                          'merge': self.merge,
                          'not_implemented': self.not_implemented,
                          'rename': self.ignore,  # done seperately
                          'dis_pub': self.dis_pub,
                          'make_obsolete': self.make_obsolete,
                          'libraryfeatureprop': self.load_lfp,
                          'featureprop': self.load_featureprop,
                          'featurerelationship': self.load_feature_relationship
                          }

        self.delete_dict = {'synonym': self.delete_synonym,
                            'cvtermprop': self.delete_feature_cvtermprop,
                            'featureprop': self.delete_featureprop,
                            'featurerelationship': self.delete_feature_relationship
                            }
        self.proforma_start_line_number = params.get('proforma_start_line_number')

        ###########################################################
        # Values queried later, placed here for reference purposes.
        ############################################################
        self.pub = None
        self.type_name = ""
        self.set_values = params.get('set_values')
        ############################################################
        # Get processing info and data to be processed.
        # Please see the yml/publication.yml file for more details
        ############################################################
        yml_file = os.path.join(os.path.dirname(__file__), '../yml/seqfeat.yml')
        # Populated self.process_data with all possible keys.
        self.process_data = self.load_reference_yaml(yml_file, params)
        self.log = log

    def load_content(self, references: dict):
        """Process the data.

        Args:
            references: <dict> previous reference proforma
        Returns:
            <Feature object> A feature object.
        """
        try:
            self.pub = references['ChadoPub']
        except KeyError:
            message = "Unable to find publication."
            self.critical_error(self.process_data['SF1a']['data'], message)
            return None

        self.get_sf()
        if not self.feature:  # problem getting seqfeat, lets finish
            return None

        # bang c first as this supersedes all things
        if self.bang_c:
            self.bang_c_it()
        if self.bang_d:
            self.bang_d_it()

        if self.set_values:
            self.process_sets()

        for key in self.process_data:
            if key not in self.set_values.keys():
                if 'type' not in self.process_data[key]:
                    self.critical_error(self.process_data[key]['data'],
                                        "No sub to deal type '{}' yet!! Report to HarvDev".format(key))
                self.type_dict[self.process_data[key]['type']](key)

    def get_sf(self):  # noqa
        """Get feature.
        Either create or retrieve and process some keys.
        """
        symbol_key = 'SF1a'
        merge_key = 'SF1g'
        id_key = 'SF1f'
        rename_key = 'SF1c'

        feature_type = None
        if self.has_data('SF2b'):
            type_name = self.process_data['SF2b']['data'][FIELD_VALUE]

        if self.has_data(rename_key):
            self.feature = feature_symbol_lookup(self.session, None, self.process_data[rename_key]['data'][FIELD_VALUE])
            self.feature.name = sgml_to_plain_text(self.process_data[symbol_key]['data'][FIELD_VALUE])
            self.is_new = False
            fs_remove_current_symbol(self.session, self.feature.feature_id,
                                     cv_name='synonym type', cvterm_name='symbol')
            # We do not want to reset synonyms etc later so mask
            self.process_data[rename_key]['data'] = None

            self.load_synonym(symbol_key, cvterm_name='symbol', overrule_removeold=True)
            self.load_synonym(symbol_key, unattrib=True)
            feature_pub, _ = get_or_create(self.session, FeaturePub, feature_id=self.feature.feature_id,
                                           pub_id=self.pub.pub_id)
            return

        if self.has_data(merge_key):  # if feature merge we want to create a new feature even if one exist already
            if self.process_data[id_key]['data'][FIELD_VALUE] != "new":
                message = f"SF1g has been specified and therefore SF1f HAS to be 'new' but is '{self.process_data[id_key]['data'][FIELD_VALUE]}'."
                self.critical_error(self.process_data[id_key]['data'], message)
                return
            self.is_new = True
            self.create_new(type_name, symbol_key, 'sf')

        if not self.feature and self.has_data(id_key) and self.process_data[id_key]['data'][FIELD_VALUE] != "new":
            self.feature = None
            try:
                self.feature = get_feature_and_check_uname_symbol(self.session,
                                                                  self.process_data[id_key]['data'][FIELD_VALUE],
                                                                  self.process_data[symbol_key]['data'][FIELD_VALUE])
                self.is_new = False
            except DataError as e:
                self.critical_error(self.process_data[id_key]['data'], e.error)

            return

        if not self.feature:
            try:
                self.feature = feature_symbol_lookup(self.session, type_name, self.process_data[symbol_key]['data'][FIELD_VALUE])
                self.is_new = False
            except MultipleResultsFound:
                message = "Multiple {}'s with symbol {}.".format(feature_type, self.process_data[symbol_key]['data'][FIELD_VALUE])
                log.info(message)
                self.critical_error(self.process_data[symbol_key]['data'], message)
                return
            except NoResultFound:
                if self.process_data[id_key]['data'][FIELD_VALUE] != 'new':
                    message = "Unable to find {} with symbol {}.".format(feature_type, self.process_data[symbol_key]['data'][FIELD_VALUE])
                    self.critical_error(self.process_data[symbol_key]['data'], message)
                    return
                try:
                    self._get_feature(type_name, symbol_key, id_key, merge_key, 'sf', organism_key='SF3b')
                    self.is_new = True
                except CodingError as e:
                    self.critical_error(self.process_data['SF3b']['data'], f"{e}")
                    return

        if self.is_new:
            # add default symbols
            self.load_synonym(symbol_key)

        feature_pub, _ = get_or_create(self.session, FeaturePub, feature_id=self.feature.feature_id,
                                       pub_id=self.pub.pub_id)

        if not self.is_new and self.process_data[id_key]['data'][FIELD_VALUE] != 'new':
            message = f"Symbol {self.process_data[symbol_key]['data'][FIELD_VALUE]} Not found {id_key}  but stated as NOT 'new'"
            self.critical_error(self.process_data[symbol_key]['data'], message)
            return

    def add_residues(self, key):
        if self.has_data(key):
            if not self.feature.residues:
                self.feature.residues = self.process_data[key]['data'][FIELD_VALUE]
            else:
                message = f"Residues already set to '{self.feature.residues}'. So can not be changed unless bangc is used."
                self.critical_error(self.process_data[key]['data'], message)

    def sf_load_synonym(self, key):
        if self.has_data(key):
            add_okay = True
            for item in self.process_data[key]['data']:
                if item[FIELD_VALUE] == self.process_data['SF1a']['data'][FIELD_VALUE]:
                    add_okay = False
            if add_okay:
                self.load_synonym(key)

    def addprimer(self, key):
        """ Add new primer and then add feature relationship.
        """
        oligo_type_id = self.cvterm_query(self.process_data[key]['new_cv'],
                                          self.process_data[key]['new_cvterm'])
        rel_type_id = self.cvterm_query(self.process_data[key]['cv'],
                                        self.process_data[key]['cvterm'])
        feat_name = f"{self.feature.name}_{self.process_data[key]['rank']}"
        feat, _ = get_or_create(
            self.session, Feature,
            name=feat_name,
            uniquename=feat_name,
            type_id=oligo_type_id,
            organism_id=self.feature.organism_id,
            residues=self.process_data[key]['data'][FIELD_VALUE],
            seqlen=len(self.process_data[key]['data'][FIELD_VALUE])
        )

        fr, _ = get_or_create(self.session, FeatureRelationship,
                              subject_id=feat.feature_id,
                              object_id=self.feature.feature_id,
                              type_id=rel_type_id)

    def ignore(self, key: str):
        """Ignore, done by initial setup.

        Args:
            key (string): Proforma field key
                NOT used, but is passed automatically.
        """
        pass

    def merge(self, key):
        """Merge seqfeat list into new seqfeat."""
        # change the pub
        self.feature.pub_id = self.pub.pub_id

        # seqfeats = self.get_merge_features(key, feat_type='seqfeat')
        for item in self.process_data[key]['data']:
            seqfeat_id = item[FIELD_VALUE]
            seqfeat = self.session.query(Feature).filter(Feature.uniquename == seqfeat_id).one()
            log.debug("seqfeat to be merged is {}".format(seqfeat))
            seqfeat.is_obsolete = True
            # Transfer synonyms
            self.transfer_synonyms(seqfeat)
            # Transfer cvterms
            self.transfer_cvterms(seqfeat)
            # Transfer dbxrefs
            self.transfer_dbxrefs(seqfeat)
            # transfer papers
            self.transfer_papers(seqfeat)
            # transfer featureprop and featureproppubs
            self.transfer_props(seqfeat)
            # transfer feature relationships
            self.transfer_feature_relationships(seqfeat)
