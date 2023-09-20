# -*- coding: utf-8 -*-
"""Chado Feature/Feature main module.

.. moduleauthor:: Ian Longden <ilongden@morgan.harvard.edu>
"""

import os
import re
from chado_object.chado_base import FIELD_VALUE, ChadoFeatureObject
from harvdev_utils.production import (
    Feature, FeaturePub, Featureprop, FeatureCvterm, FeatureCvtermprop,
    Organism, Cvterm, Cv, Synonym, Db, Dbxref, Pub
)
from harvdev_utils.chado_functions import get_or_create
from error.error_tracking import CRITICAL_ERROR
import logging
from datetime import datetime

log = logging.getLogger(__name__)


class ChadoGeneProduct(ChadoFeatureObject):
    """Class object for Chado GeneProduct/Feature.

    Main chado object is a  Feature.
    """

    def __init__(self, params):
        """Initialise the Feature object.

        type dict and delete_dict determine which methods are called
        based on the controlling yml file.
        """
        log.debug('Initializing ChadoGeneProduct object.')

        # Initiate the parent.
        super(ChadoGeneProduct, self).__init__(params)

        ##########################################
        #
        # Set up how to process each type of input
        #
        # This is set in the Feature.yml file.
        ##########################################
        self.type_dict = {'direct': self.load_direct,
                          'relationship': self.load_relationship,
                          'prop': self.load_prop,
                          'cvterm': self.load_cvterm,
                          'synonym': self.load_synonym,
                          'dissociate_pub': self.dissociate_pub,
                          'obsolete': self.make_obsolete,
                          'ignore': self.ignore,
                          'data_set': self.ignore,  # Done separately
                          'dbxrefprop': self.load_dbxrefprop,
                          'featureprop': self.load_featureprop}

        self.delete_dict = {'direct': self.delete_direct,
                            'dbxrefprop': self.delete_dbxref,
                            'ignore': self.delete_ignore,
                            'prop': self.delete_prop,
                            'cvterm': self.delete_cvterm,
                            'synonym': self.delete_synonym,
                            'featureprop': self.delete_featureprop,
                            'relationship': self.delete_relationship}

        self.proforma_start_line_number = params.get('proforma_start_line_number')
        self.reference = params.get('reference')

        ###########################################################
        # Values queried later, placed here for reference purposes.
        ############################################################
        self.pub = None   # All other proforma need a reference to a pub

        self.type = None  # Gene products can be of many types so store that here.
        self.new = False
        self.feature = None

        ############################################################
        # Get processing info and data to be processed.
        # Please see the yml/Feature.yml file for more details
        ############################################################
        yml_file = os.path.join(os.path.dirname(__file__), '../yml/geneproduct.yml')
        # Populated self.process_data with all possible keys.
        self.process_data = self.load_reference_yaml(yml_file, params)
        self.log = log

    def load_content(self, references):
        """Process the proforma data."""
        self.pub = references['ChadoPub']

        if self.process_data['F1f']['data'][FIELD_VALUE] == "new":
            self.new = True
        self.feature = self.get_geneproduct()

        # if self.Feature:  # Only proceed if we have a hh. Otherwise we had an error.
        #    self.extra_checks()
        # else:
        #    return

        # bang c/d first as this supersedes all things
        if self.bang_c:
            self.bang_c_it()
        if self.bang_d:
            self.bang_d_it()

        for key in self.process_data:
            self.type_dict[self.process_data[key]['type']](key)

        timestamp = datetime.now().strftime('%c')
        curated_by_string = f'Curator: {self.curator_fullname};Proforma: {self.filename_short};timelastmodified: {timestamp}'
        log.debug('Curator string assembled as:')
        log.debug(curated_by_string)

    def get_uniquename_and_checks(self):
        # Need to return string based on F3 content.

        name = self.process_data['F1a']['data'][FIELD_VALUE]

        format_okay = False
        if name.endswith('-XP') or name.endswith('-XR'):
            if self.has_data('F2'):
                message = f"F1a {name} cannot end in -XR or -XP if F2 is defined"
                self.critical_error(self.process_data['F1a']['data'], message)
                return
            format_okay = True
        elif name.endswith(']PA') or name.endswith(']RA'):
            if not self.has_data('F2'):
                message = f"Require F2 value if {name} is transgenic (not -XR or -XP)"
                self.critical_error(self.process_data['F1a']['data'], message)
            format_okay = True
        elif name.contains('&cap;'):
            if not self.has_data('F2'):
                message = f"Require F2 value if {name} is transgenic (not -XR or -XP)"
                self.critical_error(self.process_data['F1a']['data'], message)
            format_okay = True
        if not format_okay:
            message = f"F1a {name} must end with -XR, -XP, ]PA, ]RA, or, contain '&cap;' for a split system combination feature"
            self.critical_error(self.process_data['F1a']['data'], message)
            return

        pattern = r'(.*) (\w+):(\d+)'
        s_res = re.search(pattern, self.process_data['F3']['data'][FIELD_VALUE])
        type_name = ""
        if s_res:
            type_name = s_res.group(1)
            cv_name = s_res.group(2)
            end_name = s_res.group(3)
        else:
            message = "Does not fit format, expected the format (.*) (\w+):(\d+)"
            self.critical_error(self.process_data['F3']['data'], message)
            return

        if type_name == 'protein':
            message = "Type can not be 'protein', should be 'polypeptide"
            self.critical_error(self.process_data['F3']['data'], message)
            return
        if type_name != 'split system combination':
            if name.contains('INTERSECTION') or name.contains('&cap;'):
                message = f"split system combination feature {name} must have type 'split system combination FBcv:0009026' in F3."
                self.critical_error(self.process_data['F3']['data'], message)
                return

        fb_prefix = "FB"
        if type_name == 'split system combination':
            fb_prefix += "co"
            if not name.contains('&cap;'):
                message = f"new split system combination feature {name} must have '&cap;' in its name"
                self.critical_error(self.process_data['F1a']['data'], message)
                return

            pattern = "(XR|XP|R[A-Z]|P[A-Z])$"
            s_res = re.findall(pattern, name)
            if s_res:
                message = f"new split system combination feature {name} must not have any XR/XP/RA/PA suffix in its name"
                self.critical_error(self.process_data['F1a']['data'], message)
                return

            pattern = "DBD.*AD"
            s_res = re.findall(pattern, name)
            if not s_res:
                message = f"new split system combination feature {name} must list DBD before AD;"
                self.critical_error(self.process_data['F1a']['data'], message)
                return
        elif type_name == 'polypeptide':
            fb_prefix += "pp"
            pattern = "(-XP|P[A-Z])$"
            s_res = re.findall(pattern, name)
            if not s_res:
                message = f"polypeptide {name} should be ended with -XP or PA"
                self.critical_error(self.process_data['F1a']['data'], message)
                return
        elif type_name.endswith('RNA'):
            fb_prefix += "tr"
            pattern = "(-XR|R[A-Z])$"
            s_res = re.findall(pattern, name)
            if not s_res:
                message = f"transcript {name} should be ended with -XR or RA"
                self.critical_error(self.process_data['F1a']['data'], message)
                return
        else:
            message = f"unexpected F3 value: {type_name}"
            self.critical_error(self.process_data['F3']['data'], message)
            return
        return fb_prefix

"""
    $type
    eq
    'polypeptide' ) {
      if (!($ph{F1a}=~ / -XP$ /) & & !($ph{F1a}=~ /]P[A-Z]$ /)){
        print
      STDERR
      "ERROR: polypeptide $ph{F1a} should be ended with -XP or PA\n";
      }
      ($unique, $flag) = get_tempid('pp', $ph{F1a} );
    }
    elsif( $type = ~ / RNA$ / ) {
      if (!($ph{F1a}=~ / -XR$ /) & & !($ph{F1a}=~ /]R[A-Z]$ / )){
      print
      STDERR
       "ERROR: transcript $ph{F1a} should be ended with -XR or RA\n";

      }
      ($unique, $flag) = get_tempid('tr', $ph{F1a} );
    }
else {
    print
STDERR
"ERROR: unexpected F3 value: $type\n";
}
if (exists($ph{F1c}) & & $ph{F1f} eq 'new' & & $unique !~ / temp / ){
print STDERR "ERROR: merge feature should have a FB..:temp id not $unique\n";
}

#      $fbids{convers($ph{F1a})}=$unique;
#      $fbids{$ph{F1a}}=$unique;
# print STDERR "get temp id for $ph{F1a} $unique\n";
if ( $ph{F1a} =~ / ^ (.{2, 14}?)\\(.* ) / ) {
my $org=$1;
( $genus, $species ) = get_organism_by_abbrev( $self->{db}, $org);
}
if ( $ph{F1a} =~ / ^ T:(.{2, 14}?)\\(.*) / ) {
    my $org =$1;
($genus, $species) = get_organism_by_abbrev( $self->{db}, $org);
}
if ($genus eq '0'){
$genus='Drosophila';
$species='melanogaster';

}"""

    def get_org(self):
        pattern = r'^(.{2,14}?)\\'
        s_res = re.search(pattern, self.process_data['F1a']['data'][FIELD_VALUE])
        abbr = 'Dmel'
        if s_res:
            abbr = s_res[1]
        org = self.get_organism(abbr)
        return org

    def get_geneproduct(self):
        if self.new:

            # get type/uniquename from F3.
            uniquename_prefix = self.get_uniquename_and_checks()
            organism = self.get_organism()
            gp, _ = get_or_create(self.session, Feature, name=self.process_data['F1a']['data'][FIELD_VALUE],
                                  organism_id=organism.organism_id, uniquename=f'{uniquename_prefix}:temp_0')

            # db has correct FBhh0000000x in it but here still has 'FBhh:temp_0'. ???
            # presume triggers start after hh is returned. Maybe worth getting form db again
            log.debug(f"New expression created {gp.uniquename} id={gp.feature_id}.")
            self.feature = gp
            self.load_synonym('HH1b', cvterm_name='symbol')  # add symbol
            self.load_synonym('HH1b')                       # add fullname
        else:
            not_obsolete = False
            hh = self.session.query(Feature).\
                filter(Feature.uniquename == self.process_data['F1f']['data'][FIELD_VALUE],
                       Feature.is_obsolete == not_obsolete).\
                one_or_none()
            if not hh:
                self.critical_error(self.process_data['F1f']['data'], 'Feature does not exist in the database or is obsolete.')
                return
            # Check synonym name is the same as HH1b
            name = self.process_data['HH1b']['data'][FIELD_VALUE]
            if hh.name != name:
                self.critical_error(self.process_data['HH1b']['data'], 'HH1b field "{}" does NOT match the one in the database "{}"'.format(name, hh.name))

        # Add to pub to hh if it does not already exist.
        get_or_create(self.session, HumanhealthPub, pub_id=self.pub.pub_id, humanhealth_id=hh.humanhealth_id)
        return hh