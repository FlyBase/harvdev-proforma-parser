import logging
import os

from chado_object.feature.chado_feature import FIELD_VALUE, ChadoFeatureObject
from harvdev_utils.chado_functions import (
    get_default_organism_id,
    get_organism,
    get_or_create)
from harvdev_utils.production import FeaturePub

log = logging.getLogger(__name__)


class ChadoExpTool(ChadoFeatureObject):
    from chado_object.exptool.get_exp_tool import (
        get_exp_tool,
        fetch_by_FBto_and_check,
        check_existing_already,
        exptool_feature_lookup)

    def __init__(self, params):
        """Initialise the chado object."""

        # Initiate the parent.
        super(ChadoExpTool, self).__init__(params)

        self.type_dict = {'synonym': self.load_synonym,
                          'ignore': self.ignore,
                          'featureprop': self.load_featureprop,
                          'cvtermprop': self.load_feature_cvtermprop,
                          'featurerelationship': self.load_feature_relationship,
                          'rename': self.rename}

        self.delete_dict = {'ignore': self.ignore,
                            'synonym': self.delete_synonym}

        # Populated self.process_data with all possible keys.
        yml_file = os.path.join(os.path.dirname(__file__), '../yml/exptool.yml')
        self.process_data = self.load_reference_yaml(yml_file, params)

        self.proforma_start_line_number = params.get('proforma_start_line_number')

        self.pub = None
        self.feature = None
        self.type_name = 'engineered_region'
        #####################################################
        # Checking whether we're working with a new exp tool.
        #####################################################
        if self.process_data['TO1f']['data'][FIELD_VALUE] == "new":
            self.new = True
        else:
            self.new = False
        self.log = log

    def load_content(self, references):
        """Process the data.

        Args:
            references: <dict> previous reference proforma objects
        return:
            <Feature object> Experimental Tool feature object.
        """
        if not self.has_data('TO10'):
            self.organism_id = get_default_organism_id(self.session)
        else:
            self.organism_id = get_organism(self.session, short=self.process_data['TO10']['data'][FIELD_VALUE]).organism_id

        try:
            self.pub = references['ChadoPub']
        except KeyError:
            message = "Unable to find publication."
            self.critical_error(self.process_data['TO1a']['data'], message)
            return None

        # merging is a whole different thing so lets do that seperately.
        # and then exit.
        if self.has_data('TO1g'):
            self.merge()
            return

        self.get_exp_tool()

        if not self.feature:
            log.info("Exp Tool NO FEATURE???")
            return
        # Dissociate pub ONLY
        if self.has_data('TO1i'):
            self.dissociate_pub()
            return
        feature_pub, _ = get_or_create(self.session, FeaturePub,
                                       feature_id=self.feature.feature_id,
                                       pub_id=self.pub.pub_id)
        # bang c first as this supersedes all things
        if self.bang_c:
            self.bang_c_it()
        if self.bang_d:
            self.bang_d_it()

        for key in self.process_data:
            if self.process_data[key]['data']:
                log.debug("Processing {}".format(self.process_data[key]['data']))
                self.type_dict[self.process_data[key]['type']](key)

        return self.feature

    def dissociate_pub(self):
        if self.has_data('TO1f') and self.process_data['TO1f']['data'][FIELD_VALUE] == 'new':
            message = "Cannot dissociate pub with TO1f as 'new'."
            self.critical_error(self.process_data['TO1f']['data'], message)
            return None
        self.dissociate_from_pub('TO1i')

    def ignore(self, key):
        """Ignore."""
        pass

    def ignore_bang(self, key, bangc):
        """Ignore."""
        pass

    def rename(self, key):
        pass
