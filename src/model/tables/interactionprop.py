from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Interactionprop(Base):
    __tablename__ = 'interactionprop'
    __table_args__ = (
        UniqueConstraint('interaction_id', 'type_id', 'rank'),
    )

    interactionprop_id = Column(Integer, primary_key=True, server_default=text("nextval('interactionprop_interactionprop_id_seq'::regclass)"))
    interaction_id = Column(ForeignKey('interaction.interaction_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    interaction = relationship('Interaction')
    type = relationship('Cvterm')


