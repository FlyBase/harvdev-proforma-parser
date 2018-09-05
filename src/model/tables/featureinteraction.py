from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class FeatureInteraction(Base):
    __tablename__ = 'feature_interaction'
    __table_args__ = (
        UniqueConstraint('feature_id', 'interaction_id', 'role_id'),
    )

    feature_interaction_id = Column(Integer, primary_key=True, server_default=text("nextval('feature_interaction_feature_interaction_id_seq'::regclass)"))
    feature_id = Column(ForeignKey('feature.feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    interaction_id = Column(ForeignKey('interaction.interaction_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    role_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    feature = relationship('Feature')
    interaction = relationship('Interaction')
    role = relationship('Cvterm')


