import logging
from chado_object.feature.chado_feature import ChadoFeatureObject

log = logging.getLogger(__name__)


class ChadoGeneproduct(ChadoFeatureObject):

    def __init__(self, params):
        """Initialise the chado object."""
        log.debug('No Gene product coded yet object.')

        # Initiate the parent.
        super(ChadoGeneproduct, self).__init__(params)

    def load_content(self, references):
        log.critical("Geneproduct NOT coded yet")
        return None
