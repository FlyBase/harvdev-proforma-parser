from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class InteractionCvterm(Base):
    __tablename__ = 'interaction_cvterm'
    __table_args__ = (
        UniqueConstraint('interaction_id', 'cvterm_id'),
    )

    interaction_cvterm_id = Column(Integer, primary_key=True, server_default=text("nextval('interaction_cvterm_interaction_cvterm_id_seq'::regclass)"))
    interaction_id = Column(ForeignKey('interaction.interaction_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    cvterm_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    cvterm = relationship('Cvterm')
    interaction = relationship('Interaction')


