"""Organism, general routines.

.. module:: Organism
   :synopsis: Lookup and general organism functions.

.. moduleauthor:: Ian Longden <ilongden@morgan.harvard.edu>
"""

from harvdev_utils.production import Organism
from harvdev_utils.chado_functions import CodingError
from sqlalchemy.orm.exc import NoResultFound
# This may be looked up a lot so lets keep this hanging around.

# store as the abbreviation i.e ['Dmel']
#                           and ['Drosphila']['melanogastor']
# to enable more flexibility. No much memory used, so should be fine.
organism_dict = {}


def get_default_organism_id(session):
    """Get the default organism_id for Dmel.

    Args:
        session (sqlalchemy.orm.session.Session object): db connection to use.

    Returns:
        organism_id (internal chado id).
    """
    global organism_dict

    if 'Dmel' not in organism_dict:
        get_default_organism(session)
    return organism_dict['Dmel'].organism_id


def get_default_organism(session):
    """Get the default sqlalchemy organism object for Dmel (default).

    Args:
        session (sqlalchemy.orm.session.Session object): db connection to use.

    Returns:
        organism object.
    """
    global organism_dict

    if 'Dmel' not in organism_dict:
        get_organism(session, short='Dmel')

    return organism_dict['Dmel']


def get_organism(session, short=None, genus=None, species=None):
    """Get the organism based on short (abbreviation) or genus and species.

    Args:
        session (sqlalchemy.orm.session.Session object): db connection to use.

        short (str): organisms abbreviation. i.e. 'Dmel'

        genus (str): organisms genus

        species (str): organisms species

    NOTE:
        Either short name or genus and species must be specified.

    Returns:
        the sql alchemy object for the organism.

    Raises:
       CodingError: if note above failed or could not find organism.


    """
    global organism_dict
    if not short and not (genus and species):
        raise CodingError("HarvdevError: get organism called with no short or (genus and species) specified")

    organism = None
    try:
        if short:
            if short in organism_dict:
                return organism_dict[short]
            organism = session.query(Organism).\
                filter(Organism.abbreviation == short).one()

        elif genus and species:
            if genus in organism_dict and species in organism_dict[genus]:
                return organism_dict[genus][species]

            organism = session.query(Organism).\
                filter(Organism.genus == genus,
                       Organism.species == species).one()
        organism_dict[organism.abbreviation] = organism
        if genus not in organism_dict:
            organism_dict[organism.genus] = {}
        organism_dict[organism.genus][organism.species] = organism

    except NoResultFound:
        raise CodingError("HarvdevError: Could not find organism given abbreviation '{}' or genus '{}' and species '{}'".format(short, genus, species))

    return organism
