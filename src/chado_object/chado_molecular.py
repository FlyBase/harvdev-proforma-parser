import logging
from chado_object.feature.chado_feature import ChadoFeatureObject

log = logging.getLogger(__name__)


class ChadoMolecular(ChadoFeatureObject):

    def __init__(self, params):
        """Initialise the chado object."""
        log.debug('No Transposon coded yet object.')

        # Initiate the parent.
        super(ChadoMolecular, self).__init__(params)

    def load_content(self, references):
        log.warning("Molecular NOT coded yet")
        return None
