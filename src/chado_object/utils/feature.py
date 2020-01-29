"""
.. module:: feature
   :synopsis: Lookup and general Feature functions.

.. moduleauthor:: Ian Longden <ilongden@morgan.harvard.edu>
"""

from harvdev_utils.production import (
    Synonym, FeatureSynonym, Feature
)
from harvdev_utils.char_conversions import sub_sup_to_sgml
from harvdev_utils.char_conversions import sgml_to_unicode
from .organism import get_default_organism_id
from harvdev_utils.chado_functions import get_cvterm, CodingError

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


def feature_name_lookup(session, type_name, name, organism_id=None):
    """
    Lookup feature using the feature name.
    type_name is the type of feature i.e. 'gene', 'chemical entity'
    """
    # Default to Dros if not organism specified.
    if not organism_id:
        organism_id = get_default_organism_id(session)
    if type_name in ['bogus symbol', 'single balancer', 'chemical entity']:
        cv_type = 'FlyBase miscellaneous CV'
    else:
        cv_type = 'SO'
    feature_type = get_cvterm(session, cv_type, type_name)

    feature = session.query(Feature).filter(Feature.type_id == feature_type.cvterm_id,
                                            Feature.name == name,
                                            Feature.organism_id == organism_id)
    return feature


def feature_synonym_lookup(session, type_name, synonym_name, organism_id=None, cv_name='synonym type', cvterm_name='symbol'):
    """
    Lookup to see if the synonym has been used before. Even if not current

    Return features? if the synonym exists
    Return None if not found
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
        raise CodingError("HarvdevError: Could not find current synonym '{}', sgml = '{}' for type '{}'.".format(synonym_name, synonym_sgml, cvterm_name))
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

    try:
        feature = session.query(Feature).join(FeatureSynonym).join(Synonym).\
            filter(Synonym.type_id == synonym_type.cvterm_id,
                   Synonym.synonym_sgml == synonym_sgml,
                   Feature.organism_id == organism_id,
                   FeatureSynonym.is_current == 't',
                   Feature.type_id == feature_type.cvterm_id).one_or_none()
    except NoResultFound:
        raise CodingError("HarvdevError: Could not find current synonym '{}', sgml = '{}' for type '{}'.".format(synonym_name, synonym_sgml, cvterm_name))
        return None

    return feature
