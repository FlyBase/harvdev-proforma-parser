from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Project(Base):
    __tablename__ = 'project'

    project_id = Column(Integer, primary_key=True, server_default=text("nextval('project_project_id_seq'::regclass)"))
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(255), nullable=False)


