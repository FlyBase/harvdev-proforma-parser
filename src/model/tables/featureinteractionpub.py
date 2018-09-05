from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class FeatureInteractionPub(Base):
    __tablename__ = 'feature_interaction_pub'
    __table_args__ = (
        UniqueConstraint('feature_interaction_id', 'pub_id'),
    )

    feature_interaction_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('feature_interaction_pub_feature_interaction_pub_id_seq'::regclass)"))
    feature_interaction_id = Column(ForeignKey('feature_interaction.feature_interaction_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    feature_interaction = relationship('FeatureInteraction')
    pub = relationship('Pub')


