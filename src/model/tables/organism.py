from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Organism(Base):
    __tablename__ = 'organism'
    __table_args__ = (
        UniqueConstraint('genus', 'species'),
    )

    organism_id = Column(Integer, primary_key=True, server_default=text("nextval('organism_organism_id_seq'::regclass)"))
    abbreviation = Column(String(255))
    genus = Column(String(255), nullable=False)
    species = Column(String(255), nullable=False)
    common_name = Column(String(255))
    comment = Column(Text)
