from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class OrganismCvterm(Base):
    __tablename__ = 'organism_cvterm'
    __table_args__ = (
        UniqueConstraint('organism_id', 'cvterm_id', 'pub_id', 'rank'),
    )

    organism_cvterm_id = Column(Integer, primary_key=True, server_default=text("nextval('organism_cvterm_organism_cvterm_id_seq'::regclass)"))
    organism_id = Column(ForeignKey('organism.organism_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    cvterm_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    rank = Column(Integer, nullable=False, server_default=text("0"))
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)

    cvterm = relationship('Cvterm')
    organism = relationship('Organism')
    pub = relationship('Pub')


