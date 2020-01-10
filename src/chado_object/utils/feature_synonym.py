#
#
# Module to deal with general feature_synonym db stuff
#
# Errors are raised if things go wrong for some reason
from .util_errors import CodingError
from harvdev_utils.chado_functions import get_or_create
from harvdev_utils.production import (
    Cv, Cvterm, Synonym, FeatureSynonym
)

import logging
log = logging.getLogger(__name__)


def fs_add_by_ids(session, feature_id, synonym_id, pub_id, is_current=True, is_internal=False):
    #
    # get/create feature_synonym from the ids of feature, synonym and pub.
    #
    fs, _ = get_or_create(session, FeatureSynonym, feature_id=feature_id, synonym_id=synonym_id,
                          pub_id=pub_id, is_current=is_current, is_internal=is_internal)
    return fs


def fs_add_by_synonym_name_and_type(session, feature_id, synonym_name, cv_name, cvterm_name, pub_id,
                                    synonym_sgml=None, is_current=True, is_internal=False):
    #
    # Add a feature_synonym given a feature_id and an synonym_name and type_name.
    # It is envisioned we will always have a feature_id as this is th start point of all proforma,
    # if this turns out not to be the case we can add feature name and type in another function and
    # then call this one.
    #

    # Get/Create the synonym

    # First get the type_id from the type_name
    cvterm = session.query(Cvterm).join(Cv).filter(Cv.name == cv_name,
                                                   Cvterm.name == cvterm_name,
                                                   Cvterm.is_obsolete == 0).one()
    if not cvterm:
        raise CodingError("HarvdevError: Could not find cvterm '{}' for cv 'synonym type'".type_name)

    # Then get_create the synonym
    if not synonym_sgml:
        synonym_sgml = synonym_name
    synonym, _ = get_or_create(session, Synonym, type_id=cvterm.cvterm_id, name=synonym_name, synonym_sgml=synonym_sgml)
    if not synonym:
        raise CodingError("HarvdevError: Could not create synonym")

    # Then call fs_add_by_ids to create the fs form the f and s.
    fs = fs_add_by_ids(session, feature_id, synonym.synonym_id, pub_id, is_current, is_internal)
    return fs
