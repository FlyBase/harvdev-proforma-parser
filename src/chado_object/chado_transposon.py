import logging
from chado_object.feature.chado_feature import ChadoFeatureObject

log = logging.getLogger(__name__)


class ChadoTransposon(ChadoFeatureObject):

    def __init__(self, params):
        """Initialise the chado object."""
        log.error('No Transposon coded yet object.')

        # Initiate the parent.
        super(ChadoTransposon, self).__init__(params)

    def load_content(self, references):
        log.critical("Transposon NOT coded yet")
        return None
