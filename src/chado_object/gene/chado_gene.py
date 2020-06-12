"""
:synopsis: The Gene ChadoObject.

:moduleauthor: Christopher Tabone <ctabone@morgan.harvard.edu>, Ian Longden <ilongden@morgan.harvard.edu>
"""
import logging
import os
import re
from datetime import datetime

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from chado_object.chado_base import FIELD_NAME, FIELD_VALUE, LINE_NUMBER
from chado_object.feature.chado_feature import ChadoFeatureObject
from chado_object.utils.go import process_GO_line
from harvdev_utils.chado_functions import (DataError, feature_symbol_lookup,
                                           get_cvterm, get_dbxref,
                                           get_feature_and_check_uname_symbol,
                                           get_or_create, synonym_name_details)
from harvdev_utils.production import (Feature, FeatureCvterm,
                                      FeatureCvtermprop, FeaturePub,
                                      FeatureRelationship,
                                      FeatureRelationshipprop)

log = logging.getLogger(__name__)


class ChadoGene(ChadoFeatureObject):
    """ChadoGene object."""

    from chado_object.gene.gene_merge import (
        merge, get_merge_genes, transfer_dbxrefs, transfer_synonyms, transfer_grpmembers,
        transfer_hh_dbxrefs, transfer_cvterms
    )

    from chado_object.gene.gene_chado_check import (
        g28a_check, g28b_check, g31a_check, g31b_check,
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
                          'GOcvtermprop': self.load_gocvtermprop,
                          'merge': self.merge,
                          'bandinfo': self.load_bandinfo,
                          'dis_pub': self.dis_pub,
                          'make_obsolete': self.make_obsolete,
                          'featureprop': self.load_featureprop}

        self.delete_dict = {'synonym': self.delete_synonym,
                            'cvterm': self.delete_cvterm}
        self.proforma_start_line_number = params.get('proforma_start_line_number')

        ###########################################################
        # Values queried later, placed here for reference purposes.
        ############################################################
        self.pub = None
        self.type_name = 'gene'

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
        self.checks_for_key = {'G28a': self.g28a_check,
                               'G28b': self.g28b_check,
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

    def extra_checks(self):
        """Extra checks.

        Ones that are not easy to do via the validator.
        """
        for key in self.process_data:
            if key in self.checks_for_key:
                self.checks_for_key[key](key)

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
        for item in self.process_data[key]['data']:
            go_dict = process_GO_line(self.session, item[FIELD_VALUE], self.process_data[key]['cv'])
            if go_dict['error']:
                for error in go_dict['error']:
                    self.critical_error(item, error)
                continue
            feat_cvterm, _ = get_or_create(self.session, FeatureCvterm,
                                           feature_id=self.feature.feature_id,
                                           cvterm_id=go_dict['gocvterm'].cvterm_id,
                                           pub_id=self.pub.pub_id)

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
        g10_pattern = r'(.+)--(.+)'
        prop_cvterm = None
        if 'propvalue' in self.process_data[key] and self.process_data[key]['propvalue']:
            prop_cvterm = get_cvterm(self.session, self.process_data[key]['band_cv'], self.process_data[key]['band_cvterm'])

        for item in self.process_data[key]['data']:  # list of values here.
            band_range = re.search(g10_pattern, item[FIELD_VALUE])
            bands = []
            if not band_range:
                band = self.get_band(key, item[FIELD_VALUE])
                if not band:
                    return
                bands.append(band)  # left
                bands.append(band)  # right
            else:
                band = self.get_band(key, band_range.group(1))
                if not band:
                    return
                bands.append(band)
                band = self.get_band(key, band_range.group(2))
                if not band:
                    return
                bands.append(band)

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
                                  type_id=prop_cvterm.cvterm_id,
                                  value=self.process_data[key]['propvalue'])

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

    def load_cvtermprop(self, key):
        """Ignore, done by initial setup."""
        if key == 'G30':
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
            fields = re.search(g30_pattern, self.process_data[key]['data'][FIELD_VALUE], re.VERBOSE)
            if not fields:
                message = 'Wrong format should be "none_spaces_name ; SO:[0-9]*7"'
                self.critical_error(self.process_data[key]['data'], message)
                return

            cvterm_name = fields.group(1).strip()
            db_name = 'SO'
            db_acc = fields.group(2)
            cv_name = self.process_data[key]['cv']

            cvterm = get_cvterm(self.session, cv_name, cvterm_name)
            try:
                db_xref = get_dbxref(self.session, db_name, db_acc)
            except DataError:
                message = "Could not find dbxref for db '{}' and accession '{}'".format(db_name, db_acc)
                self.critical_error(self.process_data[key]['data'], message)
                return None

            if cvterm.dbxref.dbxref_id != db_xref.dbxref_id:
                message = "'{}' Does not match '{}', lookup gave '{}'".\
                    format(cvterm_name, cvterm.dbxref.accession, db_xref.accession)
                self.critical_error(self.process_data[key]['data'], message)
                return None

            new_tuple = (self.process_data[key]['data'][FIELD_NAME],
                         cvterm_name,
                         self.process_data[key]['data'][LINE_NUMBER])
            self.process_data[key]['data'] = new_tuple

        self.load_feature_cvtermprop(key)

    def get_gene(self):
        """Get initial gene and check."""
        if self.has_data('G1f'):  # if gene merge we want to create a new gene even if one exist already
            cvterm = get_cvterm(self.session, 'SO', 'gene')
            if not cvterm:
                message = "Unable to find cvterm 'gene' for Cv 'SO'."
                self.critical_error(self.process_data['G1a']['data'], message)
                return None
            organism, plain_name, sgml = synonym_name_details(self.session, self.process_data['G1a']['data'][FIELD_VALUE])
            self.feature, _ = get_or_create(self.session, Feature, name=plain_name,
                                            type_id=cvterm.cvterm_id, uniquename='FBgn:temp_0', organism_id=organism.organism_id)
            return

        if self.has_data('G1h'):
            self.feature = None
            try:
                self.feature = get_feature_and_check_uname_symbol(self.session,
                                                                  self.process_data['G1h']['data'][FIELD_VALUE],
                                                                  self.process_data['G1a']['data'][FIELD_VALUE],
                                                                  type_name='gene')
            except DataError as e:
                self.critical_error(self.process_data['G1h']['data'], e.error)

            return self.feature
        if self.process_data['G1g']['data'][FIELD_VALUE] == 'y':  # Should exist already
            #  organism, plain_name, sgml = synonym_name_details(self.session, self.process_data['G1a']['data'][FIELD_VALUE])
            try:
                self.feature = feature_symbol_lookup(self.session, 'gene', self.process_data['G1a']['data'][FIELD_VALUE])
            except MultipleResultsFound:
                message = "Multiple Genes with symbol {}.".format(self.process_data['G1a']['data'][FIELD_VALUE])
                log.info(message)
                self.critical_error(self.process_data['G1a']['data'], message)
                return
            except NoResultFound:
                message = "Unable to find Gene with symbol {}.".format(self.process_data['G1a']['data'][FIELD_VALUE])
                self.critical_error(self.process_data['G1a']['data'], message)
                return
        else:
            cvterm = get_cvterm(self.session, 'SO', 'gene')
            if not cvterm:
                message = "Unable to find cvterm 'gene' for Cv 'SO'."
                self.critical_error(self.process_data['G1a']['data'], message)
                return None
            organism, plain_name, sgml = synonym_name_details(self.session, self.process_data['G1a']['data'][FIELD_VALUE])
            self.feature, _ = get_or_create(self.session, Feature, name=plain_name,
                                            type_id=cvterm.cvterm_id, uniquename='FBgn:temp_0',
                                            organism_id=organism.organism_id)
            # add default symbol
            self.load_synonym('G1a')

    ########################################
    # Bangc, Bangd routines.
    ########################################

    def delete_synonym(self, key):
        """Ignore, done by initial setup."""
        pass

    def delete_cvterm(self, key):
        """Ignore, done by initial setup."""
        pass
