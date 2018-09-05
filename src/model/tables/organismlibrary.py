from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class OrganismLibrary(Base):
    __tablename__ = 'organism_library'
    __table_args__ = (
        UniqueConstraint('organism_id', 'library_id'),
    )

    organism_library_id = Column(Integer, primary_key=True, server_default=text("nextval('organism_library_organism_library_id_seq'::regclass)"))
    organism_id = Column(ForeignKey('organism.organism_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    library_id = Column(ForeignKey('library.library_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    library = relationship('Library')
    organism = relationship('Organism')


