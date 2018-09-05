from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class OrganismCvtermprop(Base):
    __tablename__ = 'organism_cvtermprop'
    __table_args__ = (
        UniqueConstraint('organism_cvterm_id', 'type_id', 'rank'),
    )

    organism_cvtermprop_id = Column(Integer, primary_key=True, server_default=text("nextval('organism_cvtermprop_organism_cvtermprop_id_seq'::regclass)"))
    organism_cvterm_id = Column(ForeignKey('organism_cvterm.organism_cvterm_id', ondelete='CASCADE'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    organism_cvterm = relationship('OrganismCvterm')
    type = relationship('Cvterm')


