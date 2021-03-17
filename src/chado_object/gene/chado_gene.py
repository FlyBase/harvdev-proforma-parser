"""
:synopsis: The Gene ChadoObject.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>, Ian Longden <ilongden@morgan.harvard.edu>
"""
import logging
import os
import re
from datetime import datetime

from sqlalchemy.orm.exc import NoResultFound

from chado_object.chado_base import FIELD_NAME, FIELD_VALUE, LINE_NUMBER
from chado_object.feature.chado_feature import ChadoFeatureObject
from chado_object.utils.go import process_GO_line
from harvdev_utils.chado_functions import (DataError, CodingError, feature_symbol_lookup,
                                           get_cvterm, get_dbxref, get_or_create)
from harvdev_utils.production import (Feature, FeatureCvterm,
                                      FeatureCvtermprop, FeatureDbxref, FeaturePub,
                                      FeatureRelationship, FeatureRelationshipPub,
                                      FeatureRelationshipprop,
                                      FeatureGrpmember,
                                      Grp, Grpmember,
                                      Library, LibraryFeature, LibraryFeatureprop)

log = logging.getLogger(__name__)


class ChadoGene(ChadoFeatureObject):
    """ChadoGene object."""

    from chado_object.gene.gene_merge import (
        merge, get_merge_genes, transfer_dbxrefs, transfer_synonyms, transfer_grpmembers,
        transfer_hh_dbxrefs, transfer_cvterms
    )

    from chado_object.gene.gene_chado_check import (
        g26_format_error, g26_species_check, g26_gene_symbol_check, g26_dbxref_check,
        g26_check, g28a_check, g28b_check, g30_check, g31a_check, g31b_check,
        g39a_check
    )

    def __init__(self, params):
        """Initialise the ChadoGene Object."""
        log.debug('Initializing ChadoGene object.')

        # Initiate the parent.
        super(ChadoGene, self).__init__(params)
        ##########################################
        # Set up how to process each type of input
        ##########################################
        self.type_dict = {'synonym': self.load_synonym,
                          'ignore': self.ignore,
                          'cvtermprop': self.load_cvtermprop,
                          'g26_prop': self.load_prop_g26,
                          'GOcvtermprop': self.load_gocvtermprop,
                          'merge': self.merge,
                          'bandinfo': self.load_bandinfo,
                          'dis_pub': self.dis_pub,
                          'make_obsolete': self.make_obsolete,
                          'libraryfeatureprop': self.load_lfp,
                          'grpmember': self.load_grpmember,
                          'grpfeaturerelationship': self.load_gfr,
                          'featureprop': self.load_featureprop,
                          'featurerelationship': self.load_feature_relationship}

        self.delete_dict = {'synonym': self.delete_synonym,
                            'cvtermprop': self.delete_feature_cvtermprop,
                            'featureprop': self.delete_featureprop,
                            'featurerelationship': self.delete_feature_relationship,
                            'bandinfo': self.delete_bandinfo}
        self.proforma_start_line_number = params.get('proforma_start_line_number')

        ###########################################################
        # Values queried later, placed here for reference purposes.
        ############################################################
        self.pub = None
        self.type_name = 'gene'
        self.g26_dbxref = None
        ############################################################
        # Get processing info and data to be processed.
        # Please see the yml/publication.yml file for more details
        ############################################################
        yml_file = os.path.join(os.path.dirname(__file__), '../yml/gene.yml')
        # Populated self.process_data with all possible keys.
        self.process_data = self.load_reference_yaml(yml_file, params)

        ########################################################
        # extra checks that cannit be done with cerberus.
        # Create lookup up to stop a huge if then else statement
        ########################################################
        self.checks_for_key = {'G26':  self.g26_check,
                               'G28a': self.g28a_check,
                               'G28b': self.g28b_check,
                               'G30':  self.g30_check,
                               'G31a': self.g31a_check,
                               'G31b': self.g31b_check,
                               'G39a': self.g39a_check}

    def load_content(self, references):
        """Process the data."""
        try:
            self.pub = references['ChadoPub']
        except KeyError:
            message = "Unable to find publication."
            self.critical_error(self.process_data['G1a']['data'], message)
            return None

        self.get_gene()
        if not self.feature:  # problem getting gene, lets finish
            return None
        self.extra_checks()
        # feature pub if not dissociate from pub
        if not self.has_data('G31b'):
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

        timestamp = datetime.now().strftime('%c')
        curated_by_string = 'Curator: %s;Proforma: %s;timelastmodified: %s' % (self.curator_fullname, self.filename_short, timestamp)
        log.debug('Curator string assembled as:')
        log.debug('%s' % (curated_by_string))
        return self.feature

    def load_grpmember(self, key):
        """Load grp member."""
        if not self.has_data(key):
            return
        grp_cvt = get_cvterm(self.session, self.process_data[key]['grp_cv'], self.process_data[key]['grp_cvterm'])
        try:
            grp = self.session.query(Grp).\
                filter(Grp.name == self.process_data[key]['data'][FIELD_VALUE],
                       Grp.type_id == grp_cvt.cvterm_id).one()
        except NoResultFound:
            message = "grp '{}' of type {} not found in the database"\
                .format(self.process_data[key]['data'][FIELD_VALUE], grp_cvt)
            self.critical_error(self.process_data[key]['data'], message)
            return

        gm_cvterm = get_cvterm(self.session, self.process_data[key]['gm_cv'], self.process_data[key]['gm_cvterm'])
        grpmem, _ = get_or_create(self.session, Grpmember,
                                  type_id=gm_cvterm.cvterm_id,
                                  grp_id=grp.grp_id)

        get_or_create(self.session, FeatureGrpmember,
                      feature_id=self.feature.feature_id,
                      grpmember_id=grpmem.grpmember_id)

    def load_gfr(self, key):
        """Load grp feature relationship."""
        if not self.has_data(key):
            return
        try:
            feature = feature_symbol_lookup(self.session, 'gene', self.process_data[key]['data'][FIELD_VALUE])
        except NoResultFound:
            message = "Unable to find gene symbol '{}' in the db.".format(self.process_data[key]['data'][FIELD_VALUE])
            self.critical_error(self.process_data[key]['data'], message)
            return
        if 'generic_types' in self.process_data[key]:
            found = False
            fcs = self.session.query(FeatureCvterm).filter(FeatureCvterm.feature_id == feature.feature_id)
            for cvt in fcs:
                if cvt.cvterm.name in self.process_data[key]['generic_types']:
                    found = True
            if not found:
                message = "Not of a generic gene type. Only {} are allowed".format(self.process_data[key]['generic_types'])
                self.critical_error(self.process_data[key]['data'], message)
                return
        cvterm = get_cvterm(self.session, self.process_data[key]['cv'], self.process_data[key]['cvterm'])

        # create feature relationship
        get_or_create(self.session, FeatureRelationship,
                      subject_id=self.feature.feature_id,
                      object_id=feature.feature_id,
                      type_id=cvterm.cvterm_id)

    def load_lfp(self, key):
        """Load LibraryFeatureprop."""
        if (not self.has_data('G91')) and (not self.has_data('G91a')):
            return

        # belts and braces check. Should be caught by validation but...
        if not self.has_data('G91') or not self.has_data('G91a'):
            message = "G91 cannot exist with out G91a and vice versa"
            self.critical_error(self.process_data[key]['data'], message)
            return

        # Look up library given in GA91
        # May need to do a library synonym lookup at some point.
        try:
            library = self.session.query(Library).\
                filter(Library.name == self.process_data['G91']['data'][FIELD_VALUE],
                       Library.organism_id == self.feature.organism_id).one()
        except NoResultFound:
            message = "No Library exists with the name {}".format(self.process_data['G91']['data'][FIELD_VALUE])
            self.critical_error(self.process_data[key]['data'], message)
            return

        # create LibraryFeature
        lib_feat, _ = get_or_create(self.session, LibraryFeature,
                                    feature_id=self.feature.feature_id,
                                    library_id=library.library_id)
        # get cvterm for LibraryFeatureprop
        try:
            cvterm = get_cvterm(self.session, self.process_data[key]['cv'], self.process_data['G91a']['data'][FIELD_VALUE])
        except CodingError:
            message = "Could not find cv '{}' cvterm '{}'".format(self.process_data[key]['cv'], self.process_data['G91a']['data'][FIELD_VALUE])
            self.critical_error(self.process_data[key]['data'], message)
            return

        get_or_create(self.session, LibraryFeatureprop,
                      library_feature_id=lib_feat.library_feature_id,
                      type_id=cvterm.cvterm_id)

    def extra_checks(self):
        """Extra checks.

        Ones that are not easy to do via the validator.
        """
        for key in self.process_data:
            if key in self.checks_for_key:
                self.checks_for_key[key](key)
        self.g30_check('G30')

    def dis_pub(self, key):
        """Dissociate pub from feature."""
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

    def ignore(self, key):
        """Ignore, done by initial setup."""
        pass

    def make_obsolete(self, key):
        """Make gene obsolete."""
        self.feature.is_obsolete = True

    def load_gocvtermprop(self, key):
        """Load the cvterm props for GO lines."""
        if not self.has_data(key):
            return
        values = {'date': datetime.today().strftime('%Y%m%d'),
                  'provenance': None,
                  'evidence_code': None}
        allowed_qualifiers = self.process_data[key]['qualifiers']

        # If a qualifier which is a cvterm is not linked to a cv of type 'FlyBase miscellaneous CV'
        # Then the cv name will be given in the yaml file.
        quali_cvs = {}
        for quali in allowed_qualifiers:
            if quali in self.process_data[key]:
                quali_cvs[quali] = self.process_data[key][quali]

        for item in self.process_data[key]['data']:
            go_dict = None
            try:
                go_dict = process_GO_line(self.session, item[FIELD_VALUE], self.process_data[key]['cv'], allowed_qualifiers, quali_cvs)
            except CodingError as error:
                log.debug("BOB: eeror is  {}".format(error))
                self.critical_error(item, error)
                continue
            if go_dict['error']:
                for error in go_dict['error']:
                    self.critical_error(item, error)
                continue
            feat_cvterm, _ = get_or_create(self.session, FeatureCvterm,
                                           feature_id=self.feature.feature_id,
                                           cvterm_id=go_dict['gocvterm'].cvterm_id,
                                           pub_id=self.pub.pub_id,
                                           is_not=go_dict['is_not'])

            values['evidence_code'] = go_dict['value']
            values['provenance'] = go_dict['provenance']
            for idx, cvname in enumerate(self.process_data[key]['prop_cvs']):
                prop_cvterm_name = self.process_data[key]['prop_cvterms'][idx]
                propcvterm = get_cvterm(self.session, cvname, prop_cvterm_name)

                get_or_create(self.session, FeatureCvtermprop,
                              feature_cvterm_id=feat_cvterm.feature_cvterm_id,
                              type_id=propcvterm.cvterm_id,
                              value=values[prop_cvterm_name])
            if 'prov_term' in go_dict and go_dict['prov_term']:  # Extra prop for cvterm from quali stuff
                get_or_create(self.session, FeatureCvtermprop,
                              feature_cvterm_id=feat_cvterm.feature_cvterm_id,
                              type_id=go_dict['prov_term'].cvterm_id,
                              value=None)

    def load_bandinfo(self, key):
        """Load the band info."""
        # If format is xyz--abc then xyy is the start and abc is the end band.
        # If not above format then whole thing is the start and end band.
        if not self.has_data(key):
            return
        prop_cvterm = None
        if 'propvalue' in self.process_data[key] and self.process_data[key]['propvalue']:
            prop_cvterm = get_cvterm(self.session, self.process_data[key]['band_cv'], self.process_data[key]['band_cvterm'])

        for item in self.process_data[key]['data']:  # list of values here.
            bands = self.get_bands(key, item)
            for idx, cvterm_name in enumerate(self.process_data[key]['cvterms']):
                cvterm = get_cvterm(self.session, self.process_data[key]['cv'], cvterm_name)

                if not cvterm:
                    message = "Unable to find cvterm {} for Cv '{}'.".format(self.process_data[key]['cv'], cvterm_name)
                    self.critical_error(self.process_data[key]['data'], message)
                    return None
                # so create feature relationship
                fr, new = get_or_create(self.session, FeatureRelationship,
                                        subject_id=self.feature.feature_id,
                                        object_id=bands[idx].feature_id,
                                        type_id=cvterm.cvterm_id)
                if prop_cvterm:  # if we have a propcvterm we need to create a fr prop.
                    get_or_create(self.session, FeatureRelationshipprop,
                                  feature_relationship_id=fr.feature_relationship_id,
                                  type_id=cvterm.cvterm_id,
                                  value=self.process_data[key]['propvalue'])
                # create feature relationship pub
                get_or_create(self.session, FeatureRelationshipPub,
                              feature_relationship_id=fr.feature_relationship_id,
                              pub_id=self.pub.pub_id)

    def get_bands(self, key, item):
        """Get bands form fields."""
        bands = []
        g10_pattern = r'(.+)--(.+)'
        band_range = re.search(g10_pattern, item[FIELD_VALUE])
        if not band_range:
            band = self.get_band(key, item[FIELD_VALUE])
            if not band:
                return None
            bands.append(band)  # left
            bands.append(band)  # right
        else:
            band = self.get_band(key, band_range.group(1))
            if not band:
                return None
            bands.append(band)
            band = self.get_band(key, band_range.group(2))
            if not band:
                return None
            bands.append(band)
        return bands

    def get_band(self, key, name):
        """Look up the band from the name."""
        cvterm = get_cvterm(self.session, self.process_data[key]['band_cv'], self.process_data[key]['band_cvterm'])
        if not cvterm:
            message = "Unable to find cvterm {} for Cv '{}'.".format(self.process_data[key]['band_cv'],
                                                                     self.process_data[key]['band_cvterm'])
            self.critical_error(self.process_data[key]['data'], message)
            return None

        band_name = "band-{}".format(name)
        band, new = get_or_create(self.session, Feature, name=band_name,
                                  type_id=cvterm.cvterm_id, organism_id=self.feature.organism_id)
        if new:
            message = "Could not find band with name '{}'".format(band_name)
            self.critical_error(self.process_data[key]['data'], message)
            return None
        return band

    def load_prop_g26(self, key):
        """G26 special."""
        self.load_featureprop(key)
        if self.g26_dbxref:
            get_or_create(self.session, FeatureDbxref,
                          dbxref_id=self.g26_dbxref.dbxref_id,
                          feature_id=self.feature.feature_id)

    def alter_check_g30(self, key):
        """G10 Special processing to correct format.

        Return True if successful, False if fails.
        """
        okay = True
        if not self.has_data(key):
            message = "Cannot bangc G30 with no values"
            self.critical_error(self.process_data[key]['data'], message)
            return False

        g30_pattern = r"""
                ^           # start of line
                \s*         # possible leading spaces
                (\S+)       # anything excluding spaces
                \s*         # possible spaces
                ;           # separator
                \s*         # possible spaces
                SO:         # dbxref DB must start be SO:
                (\d{7})  # accession 7 digit number i.e. 0000011
        """
        new_tuple_array = []
        for item in self.process_data[key]['data']:
            fields = re.search(g30_pattern, item[FIELD_VALUE], re.VERBOSE)
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

    def load_cvtermprop(self, key):
        """Ignore, done by initial setup."""
        if key == 'G30':
            if not self.alter_check_g30(key):
                return
        try:
            self.load_feature_cvtermprop(key)
        except CodingError as e:
            self.critical_error(self.process_data[key]['data'][0], e.error)

    def get_gene(self):
        """Get initial gene and check."""
        self.load_feature(feature_type='gene')

    ########################################
    # Bangc, Bangd routines.
    ########################################

    def delete_synonym(self, key):
        """Ignore, done by initial setup."""
        pass

    def delete_cvterm(self, key):
        """Ignore, done by initial setup."""
        pass

    def delete_bandinfo(self, key, bangc=False):
        """Delete the band info.

        The only difference between 10a and 10b is that 10a has a prop.
        So if a prop is defined we only want to delete those and if not
        only delete those that do NOT have a prop.

        Deleting the feature relationship cascade deletes the featyrerelationshipprop if
        there is one.
        """
        has_prop = False
        if 'propvalue' in self.process_data[key] and self.process_data[key]['propvalue']:
            has_prop = True
        if not bangc:
            self.bangd_bandinfo(key, has_prop)
            return
        for idx, cvterm_name in enumerate(self.process_data[key]['cvterms']):
            cvterm = get_cvterm(self.session, self.process_data[key]['cv'], cvterm_name)
            if not cvterm:
                message = "Unable to find cvterm {} for Cv '{}'.".format(self.process_data[key]['cv'], cvterm_name)
                self.critical_error(self.process_data[key]['data'], message)
                return None
            frs = self.session.query(FeatureRelationship).\
                filter(FeatureRelationship.subject_id == self.feature.feature_id,
                       FeatureRelationship.type_id == cvterm.cvterm_id)
            for fr in frs:
                try:
                    self.session.query(FeatureRelationshipprop).\
                        filter(FeatureRelationshipprop.feature_relationship_id == fr.feature_relationship_id).one()
                    if has_prop:
                        log.debug("LOOKUP: deleting fr {}".format(fr))
                        self.session.delete(fr)
                except NoResultFound:
                    if not has_prop:
                        log.debug("LOOKUP: deleting fr {}".format(fr))
                        self.session.delete(fr)

    def bangd_bandinfo(self, key, has_prop):
        """Delete the specific band info."""
        for item in self.process_data[key]['data']:  # list of values here.
            bands = self.get_bands(key, item)
            for idx, cvterm_name in enumerate(self.process_data[key]['cvterms']):
                cvterm = get_cvterm(self.session, self.process_data[key]['cv'], cvterm_name)
                if not cvterm:
                    message = "Unable to find cvterm {} for Cv '{}'.".format(self.process_data[key]['cv'], cvterm_name)
                    self.critical_error(self.process_data[key]['data'], message)
                    return None
                frps = self.session.query(FeatureRelationshipPub).join(FeatureRelationship).\
                    filter(FeatureRelationship.subject_id == self.feature.feature_id,
                           FeatureRelationship.object_id == bands[idx].feature_id,
                           FeatureRelationship.type_id == cvterm.cvterm_id,
                           FeatureRelationshipPub.pub_id == self.pub.pub_id)
                count = 0
                for frp in frps:
                    count += 1
                    log.debug("LOOKUP band deltion: deleting fr {}".format(frp.feature_relationship))
                    self.session.delete(frp.feature_relationship)

                if not count:
                    message = "Cannot bangd as it does not exist"
                    self.critical_error(item, message)
                    continue
        self.process_data[key]['data'] = None
