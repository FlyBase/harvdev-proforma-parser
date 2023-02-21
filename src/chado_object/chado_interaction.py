import logging
from chado_object.feature.chado_feature import ChadoFeatureObject

log = logging.getLogger(__name__)


class ChadoInteraction(ChadoFeatureObject):

    def __init__(self, params):
        """Initialise the chado object."""
        log.debug('No Interaction coded yet object.')

        # Initiate the parent.
        super(ChadoInteraction, self).__init__(params)

    def load_content(self, references):
        log.critical("Interaction NOT coded yet")
        return None
