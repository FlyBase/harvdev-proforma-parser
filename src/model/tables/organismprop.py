from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Organismprop(Base):
    __tablename__ = 'organismprop'
    __table_args__ = (
        UniqueConstraint('organism_id', 'type_id', 'rank'),
    )

    organismprop_id = Column(Integer, primary_key=True, server_default=text("nextval('organismprop_organismprop_id_seq'::regclass)"))
    organism_id = Column(ForeignKey('organism.organism_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    organism = relationship('Organism')
    type = relationship('Cvterm')


