from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Library(Base):
    __tablename__ = 'library'
    __table_args__ = (
        UniqueConstraint('organism_id', 'uniquename', 'type_id'),
    )

    library_id = Column(Integer, primary_key=True, server_default=text("nextval('library_library_id_seq'::regclass)"))
    organism_id = Column(ForeignKey('organism.organism_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    name = Column(String(255), index=True)
    uniquename = Column(Text, nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_obsolete = Column(Boolean, nullable=False, server_default=text("false"))
    timeaccessioned = Column(DateTime, nullable=False, server_default=text("now()"))
    timelastmodified = Column(DateTime, nullable=False, server_default=text("now()"))

    organism = relationship('Organism')
    type = relationship('Cvterm')


