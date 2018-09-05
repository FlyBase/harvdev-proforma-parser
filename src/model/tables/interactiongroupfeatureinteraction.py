from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class InteractionGroupFeatureInteraction(Base):
    __tablename__ = 'interaction_group_feature_interaction'
    __table_args__ = (
        UniqueConstraint('interaction_group_id', 'feature_interaction_id', 'rank'),
    )

    interaction_group_feature_interaction_id = Column(Integer, primary_key=True, server_default=text("nextval('interaction_group_feature_int_interaction_group_feature_int_seq'::regclass)"))
    interaction_group_id = Column(ForeignKey('interaction_group.interaction_group_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    feature_interaction_id = Column(ForeignKey('feature_interaction.feature_interaction_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    rank = Column(Integer, nullable=False, server_default=text("0"))
    ftype = Column(String(255))

    feature_interaction = relationship('FeatureInteraction')
    interaction_group = relationship('InteractionGroup')


