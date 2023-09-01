import logging
from chado_object.feature.chado_feature import ChadoFeatureObject

log = logging.getLogger(__name__)


class ChadoExpression(ChadoFeatureObject):

    def __init__(self, params):
        """Initialise the chado object."""
        log.error('No Expression coded yet object.')

        # Initiate the parent.
        super(ChadoExpression, self).__init__(params)

    def load_content(self, references):
        log.critical("Expression NOT coded yet")
        return None

