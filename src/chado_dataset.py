import logging
from chado_object.feature.chado_feature import ChadoFeatureObject

log = logging.getLogger(__name__)


class ChadoDataset(ChadoFeatureObject):

    def __init__(self, params):
        """Initialise the chado object."""
        log.error('No Dataset coded yet object.')

        # Initiate the parent.
        super(ChadoDataset, self).__init__(params)

    def load_content(self, references):
        log.critical("Dataset NOT coded yet")
        return None
