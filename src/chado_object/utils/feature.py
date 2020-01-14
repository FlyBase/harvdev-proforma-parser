#
#
# Module to deal with general feature_synonym db stuff
#
# Errors are raised if things go wrong for some reason
from .util_errors import CodingError
from harvdev_utils.production import (
    Cv, Cvterm, Synonym, FeatureSynonym, Feature
)
from sqlalchemy.orm.exc import NoResultFound

import logging
log = logging.getLogger(__name__)


def get_feature_and_check_uname_name(uniquename, synonym):
    """
     uniquename : FBxx0000001 type.
                 If PRESENT only that is needed to find featue,
                 if synonym_name is given use as a check.

    """
    pass


def feature_symbol_lookup(session, type_name, synonym_name, cv_name='synonym type', cvterm_name='symbol'):
    """
    Lookup feature that has a specific type and synonym name

    type_name: feature 'SO' name.  i.e. gene, chemical entity, chromosome
               NOTE we have 3 deviants that are not SO and these are checked for
               by changing the cv_type from 'SO' to 'FlyBase miscellaneous CV'

    synonym_name: The synonym Name.   REQUIRED if no uniquename

    ONLY replace cvterm_name and cv_name if you know what exactly you are doing.
    symbol lookups are kind of special and initialized here for ease of use.
    """

    # get feature type expected from type_name
    # NOTE: most are SO apart from these 3 rascals.
    if type_name in ['bogus symbol', 'single balancer', 'chemical entity']:
        cv_type = 'FlyBase miscellaneous CV'
    else:
        cv_type = 'SO'

    try:
        feature_type = session.query(Cvterm).join(Cv).\
            filter(Cvterm.name == type_name,
                   Cv.name == cv_type,
                   Cvterm.is_obsolete == 0).one()
    except NoResultFound:
        raise CodingError("HarvdevError: Could not find cv {}, cvterm {}.".format(cv_type, type_name))
        return None

    # get the type_id from cv and cvterm
    try:
        synonym_type = session.query(Cvterm).join(Cv).\
            filter(Cvterm.name == cvterm_name,
                   Cv.name == cv_name,
                   Cvterm.is_obsolete == 0).one()
    except NoResultFound:
        raise CodingError("HarvdevError: Could not find cv {}, cvterm {}.".format(cv_name, cvterm_name))
        return None

    try:
        feature = session.query(Feature).join(FeatureSynonym).join(Synonym).\
            filter(Synonym.type_id == synonym_type.cvterm_id,
                   Synonym.synonym_sgml == synonym_name,
                   FeatureSynonym.is_current == True,
                   Feature.type_id == feature_type.cvterm_id).one()
    except NoResultFound:
        raise CodingError("HarvdevError: Could not find current synonym {}, for type {}.".format(synonym_name, cvterm_name))
        return None

    return feature
