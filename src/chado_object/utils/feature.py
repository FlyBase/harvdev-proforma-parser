"""
.. module:: feature
   :synopsis: Lookup and general Feature functions.

.. moduleauthor:: Ian Longden <ilongden@morgan.harvard.edu>
"""

# harvdev utils
from harvdev_utils.production import (
    Synonym, FeatureSynonym, Feature
)
from harvdev_utils.char_conversions import sub_sup_to_sgml
from harvdev_utils.char_conversions import sgml_to_unicode
from harvdev_utils.chado_functions import get_cvterm, DataError, CodingError

# local utils
from chado_object.utils.organism import get_default_organism_id

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import logging
log = logging.getLogger(__name__)


def get_feature_by_uniquename(session, uniquename, type_name=None, organism_id=None):
    """
    Get the feature from the uniquename and aswell optionally from the organsism_id and type i.e. 'gene', 'chemical entity'

    Raises errors NoResultFound or MultipleResultsFound accordingly.
    """
    feature = None
    if not type_name and not organism_id:
        feature = _simple_uniquename_lookup(session, uniquename)
    if not feature:  # uniquename not enough or type_name and/or organism specified
        filter_spec = (Feature.uniquename == uniquename,
                       Feature.is_obsolete == 'f')
        if organism_id:
            filter_spec += (Feature.organism_id == organism_id,)
        if type_name:
            if type_name in ['bogus symbol', 'single balancer', 'chemical entity']:
                cv_type = 'FlyBase miscellaneous CV'
            else:
                cv_type = 'SO'
            feature_type = get_cvterm(session, cv_type, type_name)
            filter_spec += (Feature.type_id == feature_type.cvterm_id,)
        feature = session.query(Feature).filter(*filter_spec).one()
    return feature


def get_feature_and_check_uname_symbol(session, uniquename, synonym, type_name=None, organism_id=None):
    """
    features are unique wrt:- uniquename, organism_id and type_id
    So we need to make sure we have all 3 to be safe. (though normally just the uniquename may do)

    uniquename : FBxx0000001 type. Also be aware of things like FBgn0000014:11 which is an exon.

    NOTE: If user supplies no type_name or organism, we can get the probable organism form the synonym
          then lookup just using unique name and report problem if more than one found.

    Raises DataError if feature cannot be found uniquely.
    """
    try:
        feature = get_feature_by_uniquename(session, uniquename, type_name=type_name, organism_id=organism_id)
    except NoResultFound:
        message = "Unable to find Feature with uniquename {}.".format(uniquename)
        raise DataError(message)
    except MultipleResultsFound:
        message = "Found more than feature with this 'uniquename' {}.".format(uniquename)
        raise DataError(message)

    try:
        feat_check = feature_symbol_lookup(session, type_name, synonym)
    except NoResultFound:
        message = "Unable to find Feature with symbol {}.".format(synonym)
        raise DataError(message)
    except MultipleResultsFound:
        message = "Found more than feature with this symbol {}.".format(synonym)
        raise DataError(message)

    if feat_check.feature_id != feature.feature_id:
        message = "Symbol {} does not match that for {}.".format(synonym, uniquename)
        raise DataError(message)
    return feature


def feature_name_lookup(session, name, organism_id=None, type_name=None, type_id=None):
    """
    Lookup feature using the feature name.

    If no organism_id is given thenm it will default to Dmel

    Optional args of type_name or type_id to refine further.

    type_name is the type of feature i.e. 'gene', 'chemical entity'
    or
    type_id is the type_id of the feature to lookup.

    Raises DataError if not found uniquely.
    """
    if type_name and type_id:
        raise CodingError("Cannot specify type_name and type_id")

    # Default to Dros if no organism specified.
    if not organism_id:
        organism_id = get_default_organism_id(session)

    if type_name:
        if type_name in ['bogus symbol', 'single balancer', 'chemical entity']:
            cv_type = 'FlyBase miscellaneous CV'
        else:
            cv_type = 'SO'
        feature_type = get_cvterm(session, cv_type, type_name)
        type_id = feature_type.cvterm_id

    filter_spec = (Feature.name == name,
                   Feature.is_obsolete == 'f',
                   Feature.organism_id == organism_id)
    if type_id:
        filter_spec += (Feature.type_id == type_id,)
    try:
        feature = session.query(Feature).filter(*filter_spec).one_or_none()
    except MultipleResultsFound:
        raise DataError("DataError: Found multiple with name for type '{}'.".format(name, feature_type.name))
        feature = None
    return feature


def feature_synonym_lookup(session, type_name, synonym_name, organism_id=None, cv_name='synonym type', cvterm_name='symbol'):
    """
    Lookup to see if the synonym has been used before. Even if not current

    Return features if the synonym exists

    Raises DataError if not found at least once.

    """
    # Default to Dros if not organism specified.
    if not organism_id:
        organism_id = get_default_organism_id(session)

    # convert name to sgml format for lookup
    synonym_sgml = sgml_to_unicode(sub_sup_to_sgml(synonym_name))

    # get feature type expected from type_name
    # NOTE: most are SO apart from these 3 rascals.
    if type_name in ['bogus symbol', 'single balancer', 'chemical entity']:
        cv_type = 'FlyBase miscellaneous CV'
    else:
        cv_type = 'SO'

    feature_type = get_cvterm(session, cv_type, type_name)
    synonym_type = get_cvterm(session, cv_name, cvterm_name)

    try:
        feature = session.query(Feature).join(FeatureSynonym).join(Synonym).\
            filter(Synonym.type_id == synonym_type.cvterm_id,
                   Synonym.synonym_sgml == synonym_sgml,
                   FeatureSynonym.is_current == 'f',
                   Feature.organism_id == organism_id,
                   Feature.type_id == feature_type.cvterm_id).all()
        return feature
    except NoResultFound:
        raise DataError("DataError: Could not find current synonym '{}', sgml = '{}' for type '{}'.".format(synonym_name, synonym_sgml, cvterm_name))
        return None


def feature_symbol_lookup(session, type_name, synonym_name, organism_id=None, cv_name='synonym type', cvterm_name='symbol'):
    """
    Lookup feature that has a specific type and synonym name

    type_name: feature 'SO' name.  i.e. gene, chemical entity, chromosome
               NOTE we have 3 deviants that are not SO and these are checked for
               by changing the cv_type from 'SO' to 'FlyBase miscellaneous CV'

    synonym_name: The synonym Name.   REQUIRED if no uniquename

    ONLY replace cvterm_name and cv_name if you know what exactly you are doing.
    symbol lookups are kind of special and initialized here for ease of use.

    Raises errors of NoResultFound and MultipleResultsFound on errors.
    """
    # Defualt to Dros if not organism specified.
    if not organism_id:
        organism_id = get_default_organism_id(session)

    # convert name to sgml format for lookup
    synonym_sgml = sgml_to_unicode(sub_sup_to_sgml(synonym_name))

    # get feature type expected from type_name
    # NOTE: most are SO apart from these 3 rascals.
    if type_name in ['bogus symbol', 'single balancer', 'chemical entity']:
        cv_type = 'FlyBase miscellaneous CV'
    else:
        cv_type = 'SO'

    feature_type = get_cvterm(session, cv_type, type_name)
    synonym_type = get_cvterm(session, cv_name, cvterm_name)

    feature = session.query(Feature).join(FeatureSynonym).join(Synonym).\
        filter(Synonym.type_id == synonym_type.cvterm_id,
               Synonym.synonym_sgml == synonym_sgml,
               Feature.organism_id == organism_id,
               FeatureSynonym.is_current == 't',
               Feature.type_id == feature_type.cvterm_id).one()
    return feature


def _simple_uniquename_lookup(session, uniquename):
    """
    Lookup feature by uniquename only. Will probably work most times.

    returns feature if found uniquely or None if more than one found.

    Raises error NoResultFound if not found
    """
    try:
        feature = session.query(Feature).filter(Feature.uniquename == uniquename,
                                                Feature.is_obsolete == 'f').one_or_none()
        return feature
    except MultipleResultsFound:
        return None
