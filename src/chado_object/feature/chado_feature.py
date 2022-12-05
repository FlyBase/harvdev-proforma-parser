"""
:synopsis: The Base Feature Object.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>,
               Ian Longden <ianlongden@morgan.harvard.edu>
"""
from chado_object.chado_base import ChadoObject, FIELD_VALUE
from harvdev_utils.chado_functions import get_or_create, get_cvterm
from chado_object.utils.feature_synonym import fs_add_by_synonym_name_and_type
from harvdev_utils.chado_functions.organism import get_organism

from chado_object.utils.feature_synonym import fs_remove_current_symbol
from harvdev_utils.char_conversions import sgml_to_plain_text, sgml_to_unicode
from harvdev_utils.production import (
    Cvterm, Cvtermprop, Feature, FeatureRelationship, FeatureRelationshipPub, Featureprop,
    FeaturepropPub, FeaturePub, FeatureCvterm, FeatureCvtermprop, FeatureSynonym,
    Pub, Synonym, Library, LibraryFeature, LibraryFeatureprop
)
from harvdev_utils.chado_functions import (
    DataError, CodingError, feature_name_lookup, synonym_name_details, feature_symbol_lookup,
    get_feature_and_check_uname_symbol
)

from datetime import datetime
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from typing import List, Union
import logging
import re

log = logging.getLogger(__name__)


class ChadoFeatureObject(ChadoObject):
    """ChadoFeature object."""

    from chado_object.feature.feature_chado_check import (
        check_only_certain_fields_allowed,
        check_at_symbols_exist, check_bad_starts
    )
    from chado_object.feature.feature_merge import (
        get_merge_features, multiple_check, transfer_cvterms, transfer_dbxrefs, transfer_synonyms,
        transfer_feature_relationships, process_feat_relation_dependents, transfer_papers, transfer_props
    )

    def __init__(self, params):
        """Initialise the ChadoFeature Object."""
        log.debug('Initializing ChadoFeatureObject.')

        # Initiate the parent.
        super(ChadoFeatureObject, self).__init__(params)
        self.feature: Union[Feature, None] = None
        self.unattrib_pub = None
        self.new = None
        self.current_release = '6'

    def load_lfp(self, key: str):
        """Load LibraryFeatureprop.

        Args:
            key (string): Proforma field key
        """
        organism_id = self.feature.organism_id
        if 'prop' in self.process_data[key]:
            prop_key = self.process_data[key]['prop']
        else:
            prop_key = key
            key = prop_key[:-1]  # GA91a -> GA91, G91a -> G91

        if (not self.has_data(key)) and (not self.has_data(prop_key)):
            return

        # belts and braces check. Should be caught by validation but...
        if not self.has_data(key) or not self.has_data(prop_key):
            if self.has_data(key):
                data_key = key
            else:
                data_key = prop_key
            message = "{} cannot exist with out {} and vice versa".format(key, prop_key)
            self.critical_error(self.process_data[data_key]['data'], message)
            return

        # Look up library given in GA91 or G91
        # May need to do a library synonym lookup at some point.
        try:
            library: Library = self.session.query(Library).\
                filter(Library.name == self.process_data[key]['data'][FIELD_VALUE],
                       Library.organism_id == organism_id).one()
        except NoResultFound:
            message = "No Library exists with the name {}".format(self.process_data[key]['data'][FIELD_VALUE])
            self.critical_error(self.process_data[key]['data'], message)
            return

        # create LibraryFeature
        lib_feat, _ = get_or_create(self.session, LibraryFeature,
                                    feature_id=self.feature.feature_id,
                                    library_id=library.library_id)
        # get cvterm for LibraryFeatureprop
        try:
            cvterm = get_cvterm(self.session, self.process_data[prop_key]['cv'], self.process_data[prop_key]['data'][FIELD_VALUE])
        except CodingError:
            message = "Could not find cv '{}' cvterm '{}'".format(self.process_data[prop_key]['cv'], self.process_data[prop_key]['data'][FIELD_VALUE])
            self.critical_error(self.process_data[key]['data'], message)
            return

        get_or_create(self.session, LibraryFeatureprop,
                      library_feature_id=lib_feat.library_feature_id,
                      type_id=cvterm.cvterm_id)

    def at_symbol_check_all(self):
        """Check symbols in all fields"""
        for key in self.process_data:
            if key == 'GENE' or key == 'DRIVERS':
                continue
            if self.has_data(key) and 'at_symbol_required' in self.process_data[key]:
                self.at_symbol_check(key)

    def at_symbol_check(self, key: str):
        """
        Throw warning if it has symbol that cannot be found (and is not of a specific
        type if self.process_data[key]['at_symbol_required'] is not ['ANY'])

        Args:
            key (string): Proforma field key
        """
        if not self.has_data(key) or 'at_symbol_required' not in self.process_data[key]:
            return
        if type(self.process_data[key]['data']) is list:
            # cerberus can pass a list
            list_of_vals = self.process_data[key]['data']
        else:
            list_of_vals = [self.process_data[key]['data']]
        pattern = re.compile(r"@([^@]+)@")
        for item in list_of_vals:
            for symbol in pattern.findall(item[FIELD_VALUE]):
                try:
                    feat = feature_symbol_lookup(self.session, None, symbol)
                except NoResultFound:
                    self.critical_error(item, "symbol '{}' lookup failed".format(symbol))
                    continue
                if self.process_data[key]['at_symbol_required'][0] == 'ANY':
                    return
                if feat.cvterm.name not in self.process_data[key]['at_symbol_required']:
                    message = "{} is of type {} and not one of those listed {}".\
                        format(symbol, feat.cvterm.name, self.process_data[key]['at_symbol_required'])
                    self.critical_error(item, message)

    def make_obsolete(self, key: str):
        """Make feature obsolete.

        Args:
            key (string): Proforma field key (Not used)
        """
        self.feature.is_obsolete = True

    def not_implemented(self, key, bangc=False):
        """ Give critical error if called """
        if type(self.process_data[key]['data']) is list:
            # cerberus can pass a list
            item = self.process_data[key]['data'][0]
        else:
            item = self.process_data[key]['data']

        message = f"{key} Not implemented please see Harvdev if you think you need it"
        self.critical_error(item, message)

    def dis_pub(self, key: str):
        """Dissociate pub from feature.

        Args:
            key (string): Proforma field key
        """
        feat_pub, is_new = get_or_create(self.session, FeaturePub,
                                         feature_id=self.feature.feature_id,
                                         pub_id=self.pub.pub_id)
        if is_new:
            message = "Cannot dissociate {} to {} as relationship does not exist".\
                format(self.feature.uniquename, self.pub.uniquename)
            self.critical_error(self.process_data[key]['data'], message)
        else:
            log.info("Deleting relationship between {} and {}".format(self.feature.uniquename, self.pub.uniquename))
            self.session.delete(feat_pub)

    def get_unattrib_pub(self):
        """Get the unattributed pub."""
        if not self.unattrib_pub:
            self.unattrib_pub, _ = get_or_create(self.session, Pub, uniquename='unattributed')
        return self.unattrib_pub

    def create_new(self, cvterm_name, symbol_key, unique_bit):
        cvterm = get_cvterm(self.session, 'SO', cvterm_name)
        organism, plain_name, sgml = synonym_name_details(self.session, self.process_data[symbol_key]['data'][FIELD_VALUE])
        self.feature, self.is_new = get_or_create(self.session, Feature, name=plain_name,
                                                  type_id=cvterm.cvterm_id,
                                                  uniquename='FB{}:temp_0'.format(unique_bit),
                                                  organism_id=organism.organism_id)

    def _get_feature(self, cvterm_name: str, symbol_key: str, current_key: str, merge_key: str, unique_bit: str, cv_name: str = 'SO', organism_key: str = ""):
        """Get the feature.

        Assigns this to self.feature.

        Args:
            cvterm_name (string): cvterm name of the feature
            symbol_key (string): name of the field/key (i.e. 'GA10a')
            unique_bit (string): Unique two letter code for this feature (i.e. 'gn')
            cv_name (string, optional): cv name of the feature ('SO' is the default)

        Returns:
            Bool: True if found/created, False if not.
        """
        cvterm = get_cvterm(self.session, cv_name, cvterm_name)
        if not cvterm:
            message = "Unable to find cvterm '{}' for Cv '{}'.".format(cvterm_name, cv_name)
            self.critical_error(self.process_data[symbol_key]['data'], message)
            return None

        organism, plain_name, sgml = synonym_name_details(self.session, self.process_data[symbol_key]['data'][FIELD_VALUE])
        if organism_key:  # if organism in seperate field get from there
            if self.has_data(organism_key):
                org_abbr = self.process_data[organism_key]['data'][FIELD_VALUE]
                try:
                    organism = get_organism(self.session, short=org_abbr)
                except NoResultFound:
                    message = f'Species abbreviation "{org_abbr}" NOT found.'
                    self.critical_error(self.process_data[organism_key]['data'], message)

        if self.process_data[current_key]['data'][FIELD_VALUE] == 'y':
            self.feature, is_new = get_or_create(self.session, Feature, name=plain_name,
                                                 type_id=cvterm.cvterm_id,
                                                 organism_id=organism.organism_id)
            if is_new:
                message = f'{symbol_key} NOT found BUT is current {current_key} is set to y'
                self.critical_error(self.process_data[current_key]['data'], message)
        else:
            self.feature, is_new = get_or_create(self.session, Feature, name=plain_name,
                                                 type_id=cvterm.cvterm_id, uniquename='FB{}:temp_0'.format(unique_bit),
                                                 organism_id=organism.organism_id)
        if is_new:
            self.is_new = True
        else:
            self.is_new = False

    def load_feature(self, feature_type: str = 'gene') -> None:  # noqa
        """Get feature.

        from feature type get to the key i.e. 'G' for gene, 'GA' for allele, 'A' for aberration.
        So many proforma use similar keys but just differ in the start bit.
        i.e. G1b, GA1b, A1b.

        So for now lets have a general routine for processing the loading of the feature.
        NOTE: this will only work for those that have the same end field key bits matching
        If we get too many that do not work this way then we may have to pass each key separately.

        Args:
            feature_type (string): feature type to load. (defauts to 'gene')
        """
        CODE = 0
        UNIQUE = 1
        SO = 2
        supported_features = {'gene': ['G', 'gn', 'gene'],
                              'allele': ['GA', 'al', 'allele'],
                              'chromosome_structure_variation': ['A', 'ab', 'chromosome_structure_variation']}

        if feature_type not in supported_features:
            message = "Unsupported feature type '{}' used in load_feature call. Coding error.".format(feature_type)
            self.critical_error(self.process_data['{}1a'.format(feature_type)]['data'], message)

        symbol_key = '{}1a'.format(supported_features[feature_type][CODE])
        merge_key = '{}1f'.format(supported_features[feature_type][CODE])
        id_key = '{}1h'.format(supported_features[feature_type][CODE])
        current_key = '{}1g'.format(supported_features[feature_type][CODE])
        rename_key = '{}1e'.format(supported_features[feature_type][CODE])

        if self.has_data(rename_key):
            self.feature = feature_symbol_lookup(self.session, supported_features[feature_type][SO], self.process_data[rename_key]['data'][FIELD_VALUE])
            self.feature.name = sgml_to_plain_text(self.process_data[symbol_key]['data'][FIELD_VALUE])
            self.is_new = False
            fs_remove_current_symbol(self.session, self.feature.feature_id,
                                     cv_name='synonym type', cvterm_name='symbol')
            # We do not want to reset synonyms etc later so mask
            self.process_data[rename_key]['data'] = None

            self.load_synonym(symbol_key, cvterm_name='fullname', overrule_removeold=True)
            self.load_synonym(symbol_key, unattrib=True)
            return

        if self.has_data(merge_key):  # if feature merge we want to create a new feature even if one exist already
            # self._get_feature(supported_features[feature_type][SO], symbol_key, current_key, supported_features[feature_type][UNIQUE])
            self.create_new(supported_features[feature_type][SO], symbol_key, supported_features[feature_type][UNIQUE])
            self.load_synonym(symbol_key, cvterm_name='fullname')
            self.load_synonym(symbol_key)
            return

        if self.has_data(id_key):
            self.feature = None
            try:
                self.feature = get_feature_and_check_uname_symbol(self.session,
                                                                  self.process_data[id_key]['data'][FIELD_VALUE],
                                                                  self.process_data[symbol_key]['data'][FIELD_VALUE],
                                                                  type_name=supported_features[feature_type][SO])
                self.is_new = False
            except DataError as e:
                self.critical_error(self.process_data[id_key]['data'], e.error)

            return

        try:
            self.feature = feature_symbol_lookup(self.session, supported_features[feature_type][SO], self.process_data[symbol_key]['data'][FIELD_VALUE])
            self.is_new = False
        except MultipleResultsFound:
            message = "Multiple {}'s with symbol {}.".format(feature_type, self.process_data[symbol_key]['data'][FIELD_VALUE])
            log.info(message)
            self.critical_error(self.process_data[symbol_key]['data'], message)
            return
        except NoResultFound:
            if self.process_data[current_key]['data'][FIELD_VALUE] == 'y':
                message = "Unable to find {} with symbol {}.".format(feature_type, self.process_data[symbol_key]['data'][FIELD_VALUE])
                self.critical_error(self.process_data[symbol_key]['data'], message)
                return
            self._get_feature(supported_features[feature_type][SO], symbol_key, current_key, merge_key, supported_features[feature_type][UNIQUE])
            # add default symbol
            self.load_synonym(symbol_key)

        if not self.is_new and self.process_data[current_key]['data'][FIELD_VALUE] == 'n':
            message = f"Symbol {self.process_data[symbol_key]['data'][FIELD_VALUE]} Found but {current_key} set to 'n'"
            self.critical_error(self.process_data[symbol_key]['data'], message)
            return

    def get_pub_id_for_synonym(self, key: str):
        """Get pub_id for a synonym.

        Args:
            key (string): key/field of proforma to get pub for.

        Returns:
            int: The pub_id for the pub to be used here.
        """
        if self.has_data('G1f'):
            pub, _ = get_or_create(self.session, Pub, uniquename='unattributed')
            return pub.pub_id
        if self.has_data('CH1f'):
            if 'pub' in self.process_data[key] and self.process_data[key]['pub'] == 'current':
                pub_id = self.pub.pub_id
            else:
                # is this chebi or pubchem
                pub_id = self.get_external_chemical_pub_id()
            if pub_id:
                return pub_id
        return self.pub.pub_id

    def load_synonym(self, key: str, unattrib: bool = True, cvterm_name: str = None, overrule_removeold: bool = False) -> None:  # noqa
        """Load Synonym.

        yml options:
           cv:
           cvterm:
           is_current:
           remove_old: <optional> defaults to False
        NOTE:
          If is_current set to True and cvterm is symbol thensgml to plaintext is done.

        Args:
            key (string): key/field of proforma to add synonym for.
            unattrib (Bool): Add another unattributed synonym pub .
            cvterm_name (string, optional): cv synonym name, obtained from
                                            if not passed.
            overrule_removeold (Bool): wether to overrule the yml remove_old and do not do it.
        """
        if not self.has_data(key):
            return
        cv_name = self.process_data[key]['cv']
        if not cvterm_name:
            cvterm_name = self.process_data[key]['cvterm']
        is_current = self.process_data[key]['is_current']
        pub_id = self.get_pub_id_for_synonym(key)
        pubs = [pub_id]
        if unattrib:
            unattrib_pub_id = self.get_unattrib_pub().pub_id
            if pub_id != unattrib_pub_id:
                pubs.append(unattrib_pub_id)

        # remove the current symbol if is_current is set and yaml says remove old is_current
        # ecxcept if over rule is passed.
        if not overrule_removeold:
            if 'remove_old' in self.process_data[key] and self.process_data[key]['remove_old']:
                fs_remove_current_symbol(self.session, self.feature.feature_id, cv_name, cvterm_name)

        # add the new synonym
        if type(self.process_data[key]['data']) is list:
            items = self.process_data[key]['data']
        else:
            items = [self.process_data[key]['data']]

        for item in items:
            synonym_sgml = None
            if 'subscript' in self.process_data[key] and not self.process_data[key]['subscript']:
                synonym_sgml = sgml_to_unicode(item[FIELD_VALUE])
            for pub_id in pubs:
                fs = fs_add_by_synonym_name_and_type(self.session, self.feature.feature_id,
                                                     item[FIELD_VALUE], cv_name, cvterm_name, pub_id,
                                                     synonym_sgml=synonym_sgml, is_current=is_current, is_internal=False)
                if is_current and cvterm_name == 'symbol':
                    self.feature.name = sgml_to_plain_text(item[FIELD_VALUE])
                    fs.current = is_current

    def load_feature_cvterm(self, key: str):
        """Add feature cvterm.

        Args:
            key (string): key/field of proforma to load feature from.
        """
        if type(self.process_data[key]['data']) is list:
            items = self.process_data[key]['data']
        else:
            items = [self.process_data[key]['data']]

        cv_name = self.process_data[key]['cv']
        for item in items:
            cvterm_name = item[FIELD_VALUE]
            try:
                cvterm = get_cvterm(self.session, cv_name, cvterm_name)
            except CodingError:
                message = "Unable to find cvterm {} for Cv {}.".format(cvterm_name, cv_name)
                self.critical_error(item, message)
                return None

            if 'cvterm_namespace' in self.process_data[key]:
                try:
                    self.session.query(Cvtermprop).\
                        filter(Cvtermprop.cvterm_id == cvterm.cvterm_id,
                               Cvtermprop.value == self.process_data[key]['cvterm_namespace']).one()
                except NoResultFound:
                    message = "Cvterm '{}' Not in the required namespace of '{}'".\
                        format(cvterm.name, self.process_data[key]['cvterm_namespace'])
                    self.critical_error(item, message)

            # create feature_cvterm
            pub_id = self.pub.pub_id
            if 'unattrib_only' in self.process_data[key]:
                pub_id = self.get_unattrib_pub().pub_id
            feat_cvt, _ = get_or_create(self.session, FeatureCvterm,
                                        feature_id=self.feature.feature_id,
                                        cvterm_id=cvterm.cvterm_id,
                                        pub_id=pub_id)

    def load_feature_cvtermprop(self, key: str):
        """Add feature_cvtermprop.

        If prop_value is False then the value is used as the
        cvterm else it presumes the value is prop value and
        the cvterm is given.
        Could have gone for if cvterm is not defined etc but
        this way is more explicit.
        """
        if type(self.process_data[key]['data']) is list:
            items = self.process_data[key]['data']
        else:
            items = [self.process_data[key]['data']]

        cv_name = self.process_data[key]['prop_cv']
        cvterm_name = self.process_data[key]['prop_cvterm']
        props_cvterm = get_cvterm(self.session, cv_name, cvterm_name)
        if not props_cvterm:
            message = "Unable to find cvterm {} for Cv {}.".format(cvterm_name, cv_name)
            self.critical_error(items[0], message)
            return None

        for item in items:
            cvterm, prop_value = self.get_cvterm_propvalue(key, item)
            if not cvterm:
                continue
            # create feature_cvterm
            feat_cvt, _ = get_or_create(self.session, FeatureCvterm,
                                        feature_id=self.feature.feature_id,
                                        cvterm_id=cvterm.cvterm_id,
                                        pub_id=self.pub.pub_id)

            # create feature_cvtermprop
            get_or_create(self.session, FeatureCvtermprop,
                          feature_cvterm_id=feat_cvt.feature_cvterm_id,
                          value=prop_value,
                          type_id=props_cvterm.cvterm_id)

    def get_cvterm_propvalue(self, key: str, item: List):
        """Get cvterm and prop value.

        Also check that if namespace is defined (in the yml) the cvterm belongs to that.

        Args:
            key (string): key/field of proforma to get data from.
            item (tuple): Field tuple (field/key, value, line, bang)

        Returns:
            cvtermObj: cvterm object or None if failed.
            string: prop value
        """
        cvterm = None
        prop_value = None
        cv_name = self.process_data[key]['cv']
        if self.process_data[key]['prop_value']:
            cvterm_name = self.process_data[key]['cvterm']
            prop_value = item[FIELD_VALUE]
        else:
            # for new ones they are seperated by ';'  x ; y
            # i.e.
            cvterm_name = item[FIELD_VALUE]
        try:
            cvterm = get_cvterm(self.session, cv_name, cvterm_name)
        except CodingError:
            # may not be a coding error if cvterm name given on proforma
            if prop_value:
                message = "Coding error NO cvterm '{}' for Cv '{}'.".format(cvterm_name, cv_name)
                self.critical_error(item, message)
                return None, None

        if not cvterm:
            message = "Unable to find cvterm '{}' for Cv '{}'.".format(cvterm_name, cv_name)
            self.critical_error(item, message)
            return None, None

        if 'cvterm_namespace' in self.process_data[key]:
            try:
                self.session.query(Cvtermprop).\
                    filter(Cvtermprop.cvterm_id == cvterm.cvterm_id,
                           Cvtermprop.value == self.process_data[key]['cvterm_namespace']).one()
            except NoResultFound:
                message = "Cvterm '{}' Not in the required namespace of '{}'".\
                    format(cvterm.name, self.process_data[key]['cvterm_namespace'])
                self.critical_error(item, message)
                return None, None
        return cvterm, prop_value

    def get_feat_type_cvterm(self, key: str) -> Cvterm:
        """Get feature type cvterm.

        Args:
            key (string): key/field of proforma to get data from.
        Returns:
            cvtermObj: cvterm object or None if failed.
        """
        feat_type_name = None
        if 'feat_type' in self.process_data[key]:
            feat_type_name = self.process_data[key]['feat_type']
        elif 'type_field_in' in self.process_data[key]:
            type_key = self.process_data[key]['type_field_in']
            feat_type_name = self.process_data[type_key]['data'][FIELD_VALUE]
        if not feat_type_name:
            self.critical_error(self.process_data[key]['data'], "Neither feat_type or type_field_in is defined")
            return None
        return get_cvterm(self.session, 'SO', feat_type_name)

    def load_feature_relationship(self, key):  # noqa
        """Add Feature Relationship.

        yml options:
           cv:
           cvterm:

        Args:
            key (string): key/field of proforma to get data from.

        """
        if not self.has_data(key):
            return
        if type(self.process_data[key]['data']) is list:
            items = self.process_data[key]['data']
        else:
            items = [self.process_data[key]['data']]

        cvterm = get_cvterm(self.session, self.process_data[key]['cv'], self.process_data[key]['cvterm'])
        if not cvterm:
            message = "Unable to find cvterm {} for Cv {}.".format(self.process_data[key]['cvterm'], self.process_data[key]['cv'])
            self.critical_error(self.process_data[key]['data'], message)
            return None

        feat_type = None
        if 'feat_type' in self.process_data[key]:
            feat_type = self.process_data[key]['feat_type']
        if key == 'GENE':
            feat_type = 'gene'
        subscript = True
        if 'subscript' in self.process_data[key]:
            if not self.process_data[key]['subscript']:
                subscript = False
        # there may be a specified pattern that surrounds the symbol
        # this is specified in the yml file.
        pattern = None
        if 'pattern' in self.process_data[key]:
            pattern = self.process_data[key]['pattern']

        for item in items:
            if key == 'GENE':
                other_feat = self.gene
            else:
                other_feat = self.get_other_feature(item, feat_type, subscript, pattern=pattern)
            if not other_feat:
                continue
            if 'allowed_types' in self.process_data[key] and self.process_data[key]['allowed_types'][0].startswith("FB"):
                good = False
                for allowed_type in self.process_data[key]['allowed_types']:
                    if other_feat.uniquename.startswith(allowed_type):
                        good = True
                if not good:
                    message = f"{other_feat.type.name} not one of the allowed types {self.process_data[key]['allowed_types']}."
                    self.critical_error(self.process_data[key]['data'], message)
            self.add_relationships(key, other_feat, cvterm)

    def get_other_feature(self, item, feat_type, subscript, pattern=None):
        """Get the other feature.

        Args:
            item (tuple): Field tuple (field/key, value, line, bang)
            feat_type (list, string): Listor string of allowed feature type(s).
            subscript (bool): translate name to subscript.

        Returns:
           feature: FeatureObj or None if error occured.

        """
        name = item[FIELD_VALUE]
        if pattern:
            fields = re.search(pattern, name)
            if fields:
                name = fields.group(1)
            else:
                message = "Does not fit pattern '{}' specified in the yml file".format(pattern)
                self.critical_error(item, message)
                return
        if type(feat_type) is list:
            return self.multi_type_lookup(item, feat_type, subscript, pattern)
        try:
            other_feat = feature_symbol_lookup(self.session, feat_type, name, convert=subscript)
        except MultipleResultsFound:
            message = "Multiple results found for type: '{}' name: '{}'".format(feat_type, name)
            features = feature_symbol_lookup(self.session, feat_type, name, check_unique=False, convert=subscript)
            for feature in features:
                message += "\n\tfound: {}".format(feature)
            self.critical_error(item, message)
            return
        except NoResultFound:
            self.critical_error(item, "No Result found for {} {} subscript={}".format(feat_type, name, subscript))
            return
        return other_feat

    def multi_type_lookup(self, item, feat_type_list, subscript, pattern=None):
        """Get the other feature.

        Some lookups can have multiple types that are allowed.
        This should deal with those cases.

        Args:
            item (tuple): Field tuple (field/key, value, line, bang)
            feat_type_list (list): List of allowed feature types.
            subscript (bool): translate name to subscript.

        Returns:
            feature: FeatureObj or None if error occured.

        """
        name = item[FIELD_VALUE]
        if pattern:
            fields = re.search(pattern, name)
            if fields:
                name = fields.group(1)
            else:
                message = "Does not fit pattern '{}' specified in the yml file".format(pattern)
                self.critical_error(item, message)
                return
        try:
            other_feat = feature_symbol_lookup(self.session, None, name, convert=subscript)
        except MultipleResultsFound:
            message = "Multiple results found for type: '{}' name: '{}'".format(feat_type_list, name)
            features = feature_symbol_lookup(self.session, None, name, check_unique=False, convert=subscript)
            feat_found = None
            type_found_count = 0
            for feature in features:
                message += "\n\tfound: {} of type {}".format(feature, feature.type_id.name)
                if feature.type_id.name in feat_type_list:
                    feat_found = feature
                    type_found_count += 1
            if type_found_count == 1:
                return feat_found
            self.critical_error(item, message)
            return
        except NoResultFound:
            self.critical_error(item, "No Result found for {} {} subscript={}".format(feat_type_list, name, subscript))
            return
        return other_feat

    def add_relationships(self, key, obj_feat, cvterm):
        """Add relationships.

        Args:
            key (string): key/field of proforma to get data from.
            obj_feat (FeatureObject): feature to be linked to the self.feature object
            cvterm (CvtermObject):  create relationship with this cvterm.
        """
        sub_id = self.feature.feature_id
        obj_id = obj_feat.feature_id
        # Sometimes we want to link the relationship the other way around.
        if 'feature_is_object' in self.process_data[key]:
            if self.process_data[key]['feature_is_object']:
                obj_id = self.feature.feature_id
                sub_id = obj_feat.feature_id

        fr, _ = get_or_create(self.session, FeatureRelationship,
                              subject_id=sub_id,
                              object_id=obj_id,
                              type_id=cvterm.cvterm_id)

        frp, _ = get_or_create(self.session, FeatureRelationshipPub,
                               feature_relationship_id=fr.feature_relationship_id,
                               pub_id=self.pub.pub_id)

        if 'add_unattributed_paper' in self.process_data[key] and self.process_data[key]['add_unattributed_paper']:
            unattrib_pub_id = self.get_unattrib_pub().pub_id
            frp, _ = get_or_create(self.session, FeatureRelationshipPub,
                                   feature_relationship_id=fr.feature_relationship_id,
                                   pub_id=unattrib_pub_id)

    def load_featureproplist(self, key, prop_cv_id):
        """Load a feature props that are in a list.

        Args:
            key (string): key/field of proforma to get data from.
            prop_cv_id (int): id of the prop cvterm
        """
        for item in self.process_data[key]['data']:
            fp, is_new = get_or_create(self.session, Featureprop, feature_id=self.feature.feature_id,
                                       type_id=prop_cv_id, value=item[FIELD_VALUE])
            get_or_create(self.session, FeaturepropPub, featureprop_id=fp.featureprop_id, pub_id=self.pub.pub_id)

    def load_featureprop(self, key):  # noqa C901
        """Store the feature prop.

        If there is a value then it will have a 'value' in the yaml
        pointing to the field that is holding the value.

        yml options:
           cv:
           cvterm:
           value:    <optional>, key to value field.
           only_one: <optional>, defaults to False.

        Args:
            key (string): key/field of proforma to get data from.
        """
        if not self.has_data(key):
            return
        value = None
        prop_cv_id = self.cvterm_query(self.process_data[key]['cv'], self.process_data[key]['cvterm'])
        if type(self.process_data[key]['data']) is list:
            self.load_featureproplist(key, prop_cv_id)
            return
        if 'only_one' in self.process_data[key] and self.process_data[key]['only_one']:
            fp, is_new = get_or_create(self.session, Featureprop, feature_id=self.feature.feature_id,
                                       type_id=prop_cv_id)
            if 'value' in self.process_data[key] and self.process_data[key]['value'] != 'YYYYMMDD':
                value = self.process_data[self.process_data[key]['value']]['data'][FIELD_VALUE]
            elif 'value' in self.process_data[key]:
                value = datetime.today().strftime('%Y%m%d')
        elif ('value' in self.process_data[key]):
            val_key = self.process_data[key]['value']
            if self.has_data(val_key):
                value = self.process_data[val_key]['data'][FIELD_VALUE]
                fp, is_new = get_or_create(self.session, Featureprop, feature_id=self.feature.feature_id,
                                           type_id=prop_cv_id, value=value)
            elif 'value_nullable' not in self.process_data[key] and self.process_data[key]['value_nullable']:
                message = "Coding error. value is specified 'nullable' not set so data is required."
                self.critical_error(self.process_data[val_key]['data'], message)
                return
            else:
                return
        else:
            #  ('nullable' not in self.process_data[self.process_data[key]['value']] or
            #  not self.process_data[self.process_data[key]['value']]['nullable'])):
            message = "Coding error. only_one or value must be specified if not a list."
            self.critical_error(self.process_data[self.process_data[key]['value']]['data'], message)
            return

        if is_new:
            fp.value = value
        elif fp.value:
            message = "Already has a value. Use bangc to change it"
            self.critical_error(self.process_data[self.process_data[key]['value']]['data'], message)

        # create feature prop pub
        get_or_create(self.session, FeaturepropPub, featureprop_id=fp.featureprop_id, pub_id=self.pub.pub_id)

    def check_strand(self, strand_string, position, strand_key, key_prefix, pos_key):
        if strand_key:
            self.critical_error(
                self.process_data['{}{}'.format(key_prefix, pos_key)]['data'],
                "'{}' found after valid location NOT allowed please use the field {} to define the strand.".format(strand_string, strand_key)
            )
        else:
            if strand_string[0] != ':' and strand_string[0] != '-':
                self.critical_error(
                    self.process_data['{}{}'.format(key_prefix, pos_key)]['data'],
                    "'{}' found after valid location but does not start with  a ':' or a --'?".format(strand_string[0])
                )
                return
            if strand_string[1:] == '-1' or strand_string[1:] == '1':
                position['strand'] = strand_string[1:]
            else:
                message = "'{}' found after valid location but only '1' or '-1' accepted after '{}' Not '{}'.".\
                    format(strand_string, strand_string[0], strand_string[1:])
                self.critical_error(
                    self.process_data['{}{}'.format(key_prefix, pos_key)]['data'],
                    message
                )

    def get_position(self, key_prefix='GA90', name_key='a', pos_key='b', rel_key='c', strand_key='i', create=True):  # noqa
        """Get position data."""
        position = {'arm': None,
                    'strand': None,
                    'addfeatureloc': True,
                    'release': None}
        # check with BEV can we have GA90a without a position?

        key = '{}{}'.format(key_prefix, pos_key)

        if key in self.process_data and 'default_strand' in self.process_data[key]:
            position['strand'] = int(self.process_data[key]['default_strand'])

        if not self.has_data(key):
            # posible error message if not allowed without this.
            message = r'MUST have a position {} {} and {}'.format(key_prefix, pos_key, rel_key)
            self.critical_error(self.process_data['{}{}'.format(key_prefix, name_key)]['data'], message)
            return position

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
        s_res = re.search(pattern, self.process_data[key]['data'][FIELD_VALUE], re.VERBOSE)

        if s_res:  # matches the pattern above
            arm_name = s_res.group(1)
            position['start'] = int(s_res.group(2))
            position['end'] = int(s_res.group(3))
            if s_res.group(4):
                self.check_strand(s_res.group(4), position, strand_key, key_prefix, pos_key)
        else:
            pattern = r"""
            ^\s*          # possible spaces
            (\S+)         # arm
            :             # chrom separator
            (\d+)         # start pos
            /s+           # possible spaces
            $             # end
            """
            s_res = re.search(pattern, self.process_data[key]['data'][FIELD_VALUE], re.VERBOSE)
            if s_res:  # matches the pattern above
                arm_name = s_res.group(1)
                position['start'] = int(s_res.group(2))
                position['end'] = position['start']
            else:
                message = r'Incorrect format should be chrom:\d+..\d+'
                self.critical_error(self.process_data[key]['data'], message)
                return position

        # get rel data
        # If release specified and not equal to current assembly then
        # flag for the featurelovc to not be created.
        release_key = "{}{}".format(key_prefix, rel_key)
        if release_key in self.process_data:
            position['release'] = self.process_data[release_key]['data'][FIELD_VALUE]
            if position['release'] != self.current_release:
                self.warning_error(
                    self.process_data['{}'.format(release_key)]['data'],
                    "{} Not the current release. No featureLoc will be created.".format(position['release'])
                )
                position['addfeatureloc'] = False
        else:
            self.critical_error(self.process_data['{}{}'.format(key_prefix, name_key)]['data'], "Release {} is required".format(release_key))
            position['addfeatureloc'] = False

        # get the strand
        s_key = "{}{}".format(key_prefix, strand_key)
        if self.has_data(s_key):
            if self.process_data[s_key]['data'][FIELD_VALUE] == '-':
                position['strand'] = -1
            else:
                position['strand'] = 1

        # convert arm name to feature
        if create:
            arm_type_id = self.cvterm_query(self.process_data[key]['arm_cv'], self.process_data[key]['arm_cvterm'])
            position['arm'], is_new = get_or_create(self.session, Feature, name=arm_name, type_id=arm_type_id)
            if is_new or not position['arm']:
                message = "Could not get {} feature with cvterm {} and cv {}".\
                    format(arm_name, self.process_data[key]['arm_cvterm'], self.process_data[key]['arm_cv'])
                self.critical_error(self.process_data[key]['data'], message)
        return position

    def delete_featureprop(self, key, bangc=False):
        """Delete the feature prop and fp pubs.

        If there is a value then it will have a 'value' in the yaml
        pointing to the field that is holding the value.

        yml options:
           cv:
           cvterm:

        Args:
            key (string): key/field of proforma to get data from.
            bangc (Bool): True if bangc operation.
                          False if a bangd operation.
                          Default is False.
        """
        if not bangc:
            self.delete_specific_fp(key)
            return
        prop_cv_id = self.cvterm_query(self.process_data[key]['cv'], self.process_data[key]['cvterm'])

        # get featureprop pubs
        fpps = self.session.query(FeaturepropPub).join(Featureprop).\
            filter(FeaturepropPub.pub_id == self.pub.pub_id,
                   Featureprop.feature_id == self.feature.feature_id,
                   Featureprop.type_id == prop_cv_id)
        for fpp in fpps:
            fp = fpp.featureprop
            self.session.delete(fp)
            # self.session.delete(fpp)

    def delete_specific_fp(self, key, bangc=False):
        """Delete specific featureprop.

        Args:
            key (string): key/field of proforma to get data from.
            bangc (Bool): True if bangc operation.
                          False if a bangd operation.
                          Default is False.
        """
        prop_cv_id = self.cvterm_query(self.process_data[key]['cv'], self.process_data[key]['cvterm'])

        # can be list or single item so make it always a list.
        if type(self.process_data[key]['data']) is list:
            items = self.process_data[key]['data']
        else:
            items = [self.process_data[key]['data']]

        for item in items:
            # get featureprop pubs and delete them
            value = item[FIELD_VALUE]
            fpps = self.session.query(FeaturepropPub).join(Featureprop).\
                filter(FeaturepropPub.pub_id == self.pub.pub_id,
                       Featureprop.feature_id == self.feature.feature_id,
                       Featureprop.type_id == prop_cv_id,
                       Featureprop.value == value)
            count = 0
            for fpp in fpps:
                fp = fpp.featureprop
                self.session.delete(fp)
                self.session.delete(fpp)
                count += 1
            if not count:
                message = "Bangd failed no feature prop pub with value {}".format(value)
                self.critical_error(item, message)
        self.process_data[key]['data'] = None

    def delete_specific_fcp(self, key):
        """Delete feature cvterm based ob feature and cvterm prop.

        Args:
            key (string): key/field of proforma to get data from.
        """
        if key == 'G30':
            if not self.alter_check_g30(key):
                return
        if type(self.process_data[key]['data']) is list:
            items = self.process_data[key]['data']
        else:
            items = [self.process_data[key]['data']]
        # Use cvtermprop to get those to delete.
        pcvterm = get_cvterm(self.session, self.process_data[key]['prop_cv'], self.process_data[key]['prop_cvterm'])

        if not pcvterm:
            message = "Unable to find cvterm {} for Cv {}.".format(self.process_data[key]['prop_cv'], self.process_data[key]['prop_cvterm'])
            self.critical_error(items[0], message)
            return

        for item in items:
            try:
                cvterm = get_cvterm(self.session, self.process_data[key]['cv'], item[FIELD_VALUE])
                if not cvterm:
                    message = "Unable to find cvterm {} for Cv {}.".format(self.process_data[key]['prop_cv'], self.process_data[key]['prop_cvterm'])
                    self.critical_error(items[0], message)
                    return
                fcp = self.session.query(FeatureCvtermprop).join(FeatureCvterm).\
                    filter(FeatureCvtermprop.type_id == pcvterm.cvterm_id,
                           FeatureCvterm.feature_id == self.feature.feature_id,
                           FeatureCvterm.pub_id == self.pub.pub_id,
                           FeatureCvterm.cvterm_id == cvterm.cvterm_id).one()
            except NoResultFound:
                self.critical_error(item, "Unable to find value '{}'.".format(item[FIELD_VALUE]))
                continue
            self.session.delete(fcp.feature_cvterm)
        self.process_data[key]['data'] = None

    def delete_feature_cvtermprop(self, key, bangc=False):
        """Delete all feature_cvtermprop for a specific prop.

        If prop_value is False then the value is used as the
        cvterm else it presumes the value is prop value and
        the cvterm is given.
        Could have gone for if cvterm is not defined etc but
        this way is more explicit.

        Args:
            key (string): key/field of proforma to get data from.
            bangc (Bool): True if bangc operation.
                          False if a bangd operation.
                          Default is False.
        """
        if not bangc:
            self.delete_specific_fcp(key)
            return

        # Use cvtermprop to get those to delete.
        cvterm = get_cvterm(self.session, self.process_data[key]['prop_cv'], self.process_data[key]['prop_cvterm'])

        if not cvterm:
            message = "Unable to find cvterm {} for Cv {}.".format(self.process_data[key]['prop_cv'], self.process_data[key]['prop_cvterm'])
            self.critical_error(self.process_data[key]['data'][0], message)
            return None

        fcps = self.session.query(FeatureCvtermprop).join(FeatureCvterm).\
            filter(FeatureCvtermprop.type_id == cvterm.cvterm_id,
                   FeatureCvterm.feature_id == self.feature.feature_id,
                   FeatureCvterm.pub_id == self.pub.pub_id)
        count = 0
        # NOTE: NEED TO test old proforma to see what happens exactly.
        for fcp in fcps:
            fc = fcp.feature_cvterm
            self.session.delete(fc)
            count += 1
        if not count:
            message = "Bangc failed no feature cvterm props for this pub"
            self.critical_error(self.process_data[key]['data'][0], message)

    def delete_specific_fr(self, key, items):
        """Delete specific feature relationships.

        Args:
            key (string): key/field of proforma to get data from.
            items (list of tuples): tuples are (key, value, line_number, bangc)
        """
        cv_name = self.process_data[key]['cv']
        cvterm_name = self.process_data[key]['cvterm']
        feat_type = None
        if 'feat_type' in self.process_data[key]:
            feat_type = self.process_data[key]['feat_type']
        cvterm = get_cvterm(self.session, cv_name, cvterm_name)
        if not cvterm:
            message = "Unable to find cvterm {} for Cv {}.".format(cvterm_name, cv_name)
            self.critical_error(self.process_data[key]['data'], message)
            return None
        log.debug("LOOKUP {}: cvterm".format(cvterm))
        for item in items:
            name = item[FIELD_VALUE]
            obj_feat = feature_name_lookup(self.session, name, type_name=feat_type)
            log.debug("LOOKUP {}: obj feat = {}".format(name, obj_feat))
            try:
                log.debug("LOOKUP si {}, oi {}, pi {}, ti {}".format(self.feature.feature_id, obj_feat.feature_id, self.pub.pub_id, cvterm.cvterm_id))
                frp = self.session.query(FeatureRelationshipPub).join(FeatureRelationship).\
                    filter(FeatureRelationship.subject_id == self.feature.feature_id,
                           FeatureRelationship.object_id == obj_feat.feature_id,
                           FeatureRelationshipPub.pub_id == self.pub.pub_id,
                           FeatureRelationship.type_id == cvterm.cvterm_id).one()
                self.session.delete(frp.feature_relationship)
            except NoResultFound:
                message = "No relationship found. So cannot delete it"
                self.critical_error(item, message)
        self.process_data[key]['data'] = None

    def check_types(self, key: str, fcp: FeatureRelationshipPub, allowed_types=None) -> bool:
        """ Check if the Feature Relationship object is one of the allowed types """
        if not allowed_types:
            allowed_types = self.process_data[key]['allowed_types']
        okay = False
        fc = self.session.query(FeatureRelationship).filter(FeatureRelationship.feature_relationship_id == fcp.feature_relationship_id).one()
        obj_feat = self.session.query(Feature).filter(Feature.feature_id == fc.object_id).one()
        for allowed_type in allowed_types:
            if obj_feat.uniquename.startswith(allowed_type):
                okay = True
        return okay

    def delete_feature_relationship(self, key, bangc=False):
        """Delete the feature relationship.

        Args:
            key (string): key/field of proforma to get data from.
            bangc (Bool): True if bangc operation.
                          False if a bangd operation.
                          Default is False.
        """
        if type(self.process_data[key]['data']) is list:
            items = self.process_data[key]['data']
        else:
            items = [self.process_data[key]['data']]
        if not bangc:
            self.delete_specific_fr(key, items)
            return
        cv_name = self.process_data[key]['cv']
        cvterm_name = self.process_data[key]['cvterm']
        cvterm = get_cvterm(self.session, cv_name, cvterm_name)
        if not cvterm:
            message = "Unable to find cvterm {} for Cv {}.".format(cvterm_name, cv_name)
            self.critical_error(self.process_data[key]['data'], message)
            return None
        log.debug("LOOKUP: deleting FR for all {} in pub {} cvterm {}".format(self.feature, self.pub.uniquename, cvterm))
        fcps = self.session.query(FeatureRelationshipPub).join(FeatureRelationship).\
            filter(FeatureRelationship.subject_id == self.feature.feature_id,
                   FeatureRelationshipPub.pub_id == self.pub.pub_id,
                   FeatureRelationship.type_id == cvterm.cvterm_id)
        count = 0
        del_frs = set()
        for fcp in fcps:
            if 'allowed_types' in self.process_data[key] and self.process_data[key]['allowed_types'][0].startswith("FB"):
                okay = self.check_types(key, fcp)
                if not okay:
                    continue
            count += 1
            # check type if specified in
            log.debug("LOOKUP: deleting feat rel pub {}".format(fcp.feature_relationship))
            # self.session.delete(fcp.feature_relationship)
            del_frs.add(fcp.feature_relationship)
            self.session.delete(fcp)
        if not count:
            message = "Bangc failed no feature relationships for this pub and cvterm"
            if 'allowed_types' in self.process_data[key] and self.process_data[key]['allowed_types'][0].startswith("FB"):
                for allowed_type in self.process_data[key]['allowed_types']:
                    message += f" and does not match allowed type of {allowed_type}"
            self.critical_error(items[0], message)
            return

        # now search for any pub
        # If none found delete the feat relationship
        # For each relationship pub removed check if that object feature
        # has other links. If not delete
        for del_fr in del_frs:
            count = self.session.query(FeatureRelationshipPub).join(FeatureRelationship).\
                filter(FeatureRelationship.subject_id == self.feature.feature_id,
                       FeatureRelationship.object_id == del_fr.object_id,
                       FeatureRelationship.type_id == cvterm.cvterm_id).count()
            if not count:
                self.session.delete(del_fr)

    def delete_synonym(self, key, bangc=False):
        """Delete synonym.

        Args:
            key (string): key/field of proforma to get data from.
            bangc (Bool): True if bangc operation.
                          False if a bangd operation.
                          Default is False.
        """
        if type(self.process_data[key]['data']) is not list:
            data_list = []
            data_list.append(self.process_data[key]['data'])
        else:
            data_list = self.process_data[key]['data']

        cv_name = self.process_data[key]['cv']
        cvterm_name = self.process_data[key]['cvterm']
        cvterm = get_cvterm(self.session, cv_name, cvterm_name)
        if not cvterm:
            message = "Unable to find cvterm {} for Cv {}.".format(cvterm_name, cv_name)
            self.critical_error(self.process_data[key]['data'], message)
            return None

        if bangc:
            fss = self.session.query(FeatureSynonym).join(Synonym).\
                filter(FeatureSynonym.pub_id == self.pub.pub_id,
                       Synonym.type_id == cvterm.cvterm_id,
                       FeatureSynonym.feature_id == self.feature.feature_id)
            for fs in fss:
                self.session.delete(fs)
        else:
            for data in data_list:
                synonyms = self.session.query(Synonym).\
                    filter(Synonym.name == sgml_to_plain_text(data[FIELD_VALUE]),
                           FeatureSynonym.type_id == cvterm.cvterm_id)
                syn_count = 0
                f_syn_count = 0
                for syn in synonyms:
                    syn_count += 1
                    f_syns = self.session.query(FeatureSynonym).\
                        filter(FeatureSynonym.feature_id == self.feature.feature_id,
                               FeatureSynonym.synonym_id == syn.synonym_id,
                               FeatureSynonym.pub_id == self.pub.pub_id)
                    for f_syn in f_syns:
                        f_syn_count += 1
                        self.session.delete(f_syn)

                if not syn_count:
                    self.critical_error(data, 'Synonym {} Does not exist.'.format(data[FIELD_VALUE]))
                    continue
                elif not f_syn_count:
                    self.critical_error(data, 'Synonym {} Does not exist for this Feature that is not current.'.format(data[FIELD_VALUE]))
                    continue

    def delete_lfp(self, key: str):
        pass

    def dissociate_from_pub(self, key):
        """Dissociate feature from pub"""
        if not self.has_data(key):
            return
        if 'obsolete_feature_on_last_ref' in self.process_data[key]:
            obsolete_if_last = self.process_data[key]['obsolete_feature_on_last_ref']
        else:
            message = "Dissociate feature from pub called BUT 'obsolete_feature_on_last_ref' not specified in yml file?"
            self.critical_error(self.process_data[key]['data'], message)
            return

        # remove the association
        fp, is_new = get_or_create(self.session, FeaturePub, feature_id=self.feature.feature_id,
                                   pub_id=self.pub.pub_id)
        if is_new:
            message = "Cannot dissociate feature and pub as there is no association"
            self.critical_error(self.process_data[key]['data'], message)
        else:
            self.session.delete(fp)

        # If remove_if_last and it is the last then we set feature is_obsolete to true
        if obsolete_if_last:
            count = self.session.query(FeaturePub).filter(FeaturePub.feature_id == self.feature.feature_id).count()
            if not count:
                self.feature.is_obsolete = True
