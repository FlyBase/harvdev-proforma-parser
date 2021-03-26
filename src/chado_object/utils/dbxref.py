"""Dbxref, general routines.

.. module:: Dbxref
   :synopsis: Lookup and general dbxref functions.

.. moduleauthor:: Ian Longden <ilongden@morgan.harvard.edu>
"""
from harvdev_utils.production import (
    Db, Dbxref
)
from harvdev_utils.chado_functions import get_or_create


def get_dbxref_by_params(session, params):
    """Get/Create dbxref.

    Args:
        params:
            dbname
            accession
            description

    Returns:
        Dbxref object:
        Bool: if it is new or not
    """
    try:
        db = session.query(Db).filter(Db.name == params['dbname']).one()
        dbxref, is_new = get_or_create(session, Dbxref, db_id=db.db_id, accession=params['accession'])
        if dbxref.description is None:
            if 'description' in params:
                dbxref.description = params['description']
    except KeyError:
        return None, None
    return dbxref, is_new
