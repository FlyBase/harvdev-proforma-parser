from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship
from model.tables import Feature
from sqlalchemy import event

metadata = Base.metadata

class Gene(Feature):
    __mapper_args__ = {'polymorphic_identity': 219}