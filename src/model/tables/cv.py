from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Cv(Base):
    __tablename__ = 'cv'

    cv_id = Column(Integer, primary_key=True, server_default=text("nextval('cv_cv_id_seq'::regclass)"))
    name = Column(String(255), nullable=False, unique=True)
    definition = Column(Text)


