#
# Help utility for Organisms
#
from harvdev_utils.production import Organism
# This may be looked up a lot so lets keep this hanging around.
default_organism_id = None


def get_default_organism_id(session):
    """
    Get the default organism that is Drosophila
    """
    global default_organism_id

    if not default_organism_id:
        default_organism_id = session.query(Organism). \
            filter(Organism.genus == 'Drosophila',
                   Organism.species == 'melanogaster').one().organism_id
    return default_organism_id
