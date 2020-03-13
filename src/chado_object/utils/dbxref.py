from harvdev_utils.production import (
    Db, Dbxref
)
from harvdev_utils.chado_functions import get_or_create

def get_dbxref_by_params(session, params):
    """Get dbxref.

    """
    try:
        db = session.query(Db).filter(name=params['dbname']).one()
        dbxref, is_new = get_or_create(session, Dbxref, db_id=db.db_id, accession=params['accession'])
    except KeyError:
        return None, None
    return dbxref, is_new