from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class InteractionCvtermprop(Base):
    __tablename__ = 'interaction_cvtermprop'
    __table_args__ = (
        UniqueConstraint('interaction_cvterm_id', 'type_id', 'rank'),
    )

    interaction_cvtermprop_id = Column(Integer, primary_key=True, server_default=text("nextval('interaction_cvtermprop_interaction_cvtermprop_id_seq'::regclass)"))
    interaction_cvterm_id = Column(ForeignKey('interaction_cvterm.interaction_cvterm_id', ondelete='CASCADE'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    interaction_cvterm = relationship('InteractionCvterm')
    type = relationship('Cvterm')


