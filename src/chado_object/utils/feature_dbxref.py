"""Feature_dbxref, general routines.

   :synopsis: General Feature_dbxref functions.

.. moduleauthor:: Ian Longden <ilongden@morgan.harvard.edu>
"""

from harvdev_utils.chado_functions import get_or_create
from harvdev_utils.production import (
    FeatureDbxref
)


def fd_add_by_ids(session, feature_id, dbxref_id, is_current=True):
    """get/create feature_dbxref from the ids of feature, dbxref.

    Args:
        session (sqlalchemy.orm.session.Session object): db connection  to use.

        feature_id (int): chado feature_id.

        dbxref_id (int): chado dbxref_id.

        is_current (bool): used to set if current or not. (default: True)

    Returns:
        feature_dbxref object.
    """
    fd, _ = get_or_create(session, FeatureDbxref, feature_id=feature_id, dbxref_id=dbxref_id)
    fd.is_current = is_current
    return fd


def fd_add_by_params(session, params):
    pass
