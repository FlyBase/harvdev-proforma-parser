# store easy lookup for cv, cvterm lookups
# should save time in the long run
from harvdev_utils.production import Cv, Cvterm
from sqlalchemy.orm.exc import NoResultFound
from .util_errors import CodingError
cv_cvterm = {}


def get_cvterm(session, cv_name, cvterm_name):
    """
    Lookup cvterm.
    """
    global cv_cvterm
    try:
        return cv_cvterm[cv_name][cvterm_name]
    except KeyError:
        pass
    try:
        cvterm = session.query(Cvterm).join(Cv).\
            filter(Cvterm.name == cvterm_name,
                   Cv.name == cv_name,
                   Cvterm.is_obsolete == 0).one()
        if cv_name not in cv_cvterm:
            cv_cvterm[cv_name] = {}
        cv_cvterm[cv_name][cvterm_name] = cvterm
    except NoResultFound:
        raise CodingError("HarvdevError: Could not find cv {}, cvterm {}.".format(cv_name, cvterm_name))
        return None
    return cv_cvterm[cv_name][cvterm_name]
