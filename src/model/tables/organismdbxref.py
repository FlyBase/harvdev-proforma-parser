from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class OrganismDbxref(Base):
    __tablename__ = 'organism_dbxref'
    __table_args__ = (
        UniqueConstraint('organism_id', 'dbxref_id'),
    )

    organism_dbxref_id = Column(Integer, primary_key=True, server_default=text("nextval('organism_dbxref_organism_dbxref_id_seq'::regclass)"))
    organism_id = Column(ForeignKey('organism.organism_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    dbxref_id = Column(ForeignKey('dbxref.dbxref_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_current = Column(Boolean, nullable=False, server_default=text("true"))

    dbxref = relationship('Dbxref')
    organism = relationship('Organism')


