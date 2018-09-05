from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class FeatureInteractionprop(Base):
    __tablename__ = 'feature_interactionprop'
    __table_args__ = (
        UniqueConstraint('feature_interaction_id', 'type_id', 'rank'),
    )

    feature_interactionprop_id = Column(Integer, primary_key=True, server_default=text("nextval('feature_interactionprop_feature_interactionprop_id_seq'::regclass)"))
    feature_interaction_id = Column(ForeignKey('feature_interaction.feature_interaction_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    feature_interaction = relationship('FeatureInteraction')
    type = relationship('Cvterm')


