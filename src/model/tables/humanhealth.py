from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Humanhealth(Base):
    __tablename__ = 'humanhealth'
    __table_args__ = (
        UniqueConstraint('organism_id', 'uniquename'),
    )

    humanhealth_id = Column(Integer, primary_key=True, server_default=text("nextval('humanhealth_humanhealth_id_seq'::regclass)"))
    name = Column(String(255), index=True)
    uniquename = Column(Text, nullable=False, index=True)
    organism_id = Column(ForeignKey('organism.organism_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    dbxref_id = Column(ForeignKey('dbxref.dbxref_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'))
    is_obsolete = Column(Boolean, nullable=False, server_default=text("false"))

    dbxref = relationship('Dbxref')
    organism = relationship('Organism')


