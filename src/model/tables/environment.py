from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Environment(Base):
    __tablename__ = 'environment'

    environment_id = Column(Integer, primary_key=True, server_default=text("nextval('environment_environment_id_seq'::regclass)"))
    uniquename = Column(Text, nullable=False, unique=True)
    description = Column(Text)


