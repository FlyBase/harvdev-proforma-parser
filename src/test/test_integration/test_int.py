import pytest, configparser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from harvdev_utils.production import *

@pytest.fixture(scope='session')
def alchemy_session(request):
    # Import secure config variables.
    config = configparser.ConfigParser()
    config.read(request.config.getoption('config'))

    USER = config['connection']['USER']
    PASSWORD = config['connection']['PASSWORD']
    SERVER = config['connection']['SERVER']
    DB = config['connection']['DB']

    # Create our SQL Alchemy engine from our environmental variables.
    engine_var = 'postgresql://' + USER + ":" + PASSWORD + '@' + SERVER + '/' + DB

    engine = create_engine(engine_var)

    Session = sessionmaker(bind=engine)
    alchemy_session = Session()

    return alchemy_session

def run_app(session, filepath):
    pass

def test_213306_jma_edit_170928_part1(alchemy_session):
    filters = (
        Synonym.type_id == 59978,
        Synonym.name == 'HRSQ'
    )

    results = alchemy_session.query(Synonym).distinct().\
            filter(*filters).\
            one_or_none()

    assert results == None

    proforma_path = 'src/test/proformae/213306.jma.edit.170928'