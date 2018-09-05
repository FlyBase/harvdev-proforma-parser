from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_repr import RepresentableBase

Base = declarative_base(cls=RepresentableBase)