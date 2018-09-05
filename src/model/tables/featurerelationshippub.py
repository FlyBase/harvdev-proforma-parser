from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class FeatureRelationshipPub(Base):
    __tablename__ = 'feature_relationship_pub'
    __table_args__ = (
        UniqueConstraint('feature_relationship_id', 'pub_id'),
    )

    feature_relationship_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('feature_relationship_pub_feature_relationship_pub_id_seq'::regclass)"))
    feature_relationship_id = Column(ForeignKey('feature_relationship.feature_relationship_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    feature_relationship = relationship('FeatureRelationship')
    pub = relationship('Pub')


