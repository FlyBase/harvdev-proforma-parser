"""Feature_synonym, general routines.

   :synopsis: General Feature_synonym functions.

.. moduleauthor:: Ian Longden <ilongden@morgan.harvard.edu>
"""

from harvdev_utils.chado_functions import get_or_create, get_cvterm, CodingError
from harvdev_utils.production import (
    Synonym, FeatureSynonym
)
from harvdev_utils.char_conversions import sgml_to_plain_text
from harvdev_utils.char_conversions import sub_sup_to_sgml
from harvdev_utils.char_conversions import sgml_to_unicode
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

import logging
log = logging.getLogger(__name__)


def fs_add_by_ids(session, feature_id, synonym_id, pub_id, is_current=True, is_internal=False):
    """get/create feature_synonym from the ids of feature, synonym and pub.

    Args:
        session (sqlalchemy.orm.session.Session object): db connection  to use.

        feature_id (int): chado feature_id.

        synonym_id (int): chado synonym_id.

        pub_id (int): chado pub_id.

        is_current (bool): used to set if current or not. (default: True)

        is_internal (bool): used to set if internal or not. (default: False)

    Returns:
        feature_synonym object.
    """
    fs, _ = get_or_create(session, FeatureSynonym, feature_id=feature_id, synonym_id=synonym_id,
                          pub_id=pub_id)
    fs.is_current = is_current
    fs.is_internal = is_internal
    return fs


def fs_add_by_synonym_name_and_type(session, feature_id, synonym_name, cv_name, cvterm_name, pub_id,
                                    synonym_sgml=None, is_current=True, is_internal=False):
    """Create a feature_synoym given a feature_id and an synonym_name and type_name.

    Args:
        session (sqlalchemy.orm.session.Session object): db connection  to use.

        feature_id (int): chado feature_id.

        synonym_name (str): synonym name.

        cv_name (str):  cv name to get type of synonym

        cvterm_name (str):  cvterm name to get type of synonym

        pub_id (int): chado pub_id.

        synonym_sgml (str): <optional> If not given it will be calculated.

        is_current (bool): used to set if current or not. (default: True)

        is_internal (bool): used to set if internal or not. (default: False)

    Returns:
        feature_synonym object.

    Raises:
        CodingError: cv/cvterm lookup fails. unable to create synonym.
   """
    #
    # Add a feature_synonym given a feature_id and an synonym_name and type_name.
    # It is envisioned we will always have a feature_id as this is the start point of all proforma,
    # if this turns out not to be the case we can add feature name and type in another function and
    # then call this one.
    #

    # Get/Create the synonym

    # First get the type_id from the type_name
    cvterm = get_cvterm(session, cv_name, cvterm_name)

    if not cvterm:
        raise CodingError("HarvdevError: Could not find cvterm '{}' for cv {}".format(cvterm_name, cv_name))

    # Then get_create the synonym
    if not synonym_sgml:
        synonym_sgml = sgml_to_unicode(sub_sup_to_sgml(synonym_name))
    synonym_name = sgml_to_plain_text(synonym_name)
    synonym, _ = get_or_create(session, Synonym, type_id=cvterm.cvterm_id, name=synonym_name, synonym_sgml=synonym_sgml)
    if not synonym:
        raise CodingError("HarvdevError: Could not create synonym")

    # Then call fs_add_by_ids to create the fs form the f and s.
    fs = fs_add_by_ids(session, feature_id, synonym.synonym_id, pub_id, is_current, is_internal)
    return fs


def fs_remove_current_symbol(session, feature_id, cv_name, cvterm_name, pub_id):
    """Remove is_current for this feature_synonym.

    Make the current symbol for this feature is_current=False.
    Usually done when assigning a new symbol we want to set the old one
    to is_current = False and not to delete it.

    Args:
        session (sqlalchemy.orm.session.Session object): db connection  to use.

        feature_id (int): chado feature_id.

        synonym_name (str): synonym name.

        cv_name (str):  cv name to get type of synonym

        cvterm_name (str):  cvterm name to get type of synonym

        pub_id (int): chado pub_id.

    Returns: Null

    Raises:
        CodingError: cv/cvterm lookup fails. unable to get synonym type.
    """
    cvterm = get_cvterm(session, cv_name, cvterm_name)
    if not cvterm:
        raise CodingError("HarvdevError: Could not find cvterm '{}' for cv {}".format(cvterm_name, cv_name))

    try:
        fs = session.query(FeatureSynonym).join(Synonym).\
            filter(FeatureSynonym.feature_id == feature_id,
                   # FeatureSynonym.pub_id == pub_id,
                   Synonym.type_id == cvterm.cvterm_id,
                   FeatureSynonym.is_current == 't').one()
        fs.is_current = False
    except MultipleResultsFound:
        log.error("More than one result for feature id = {}".format(feature_id))
        fss = session.query(FeatureSynonym).join(Synonym).\
            filter(FeatureSynonym.feature_id == feature_id,
                   # FeatureSynonym.pub_id == pub_id,
                   Synonym.type_id == cvterm.cvterm_id,
                   FeatureSynonym.is_current == 't')
        for fs in fss:
            log.error(fs)
        raise MultipleResultsFound
    except NoResultFound:
        return
