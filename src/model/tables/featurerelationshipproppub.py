from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class FeatureRelationshippropPub(Base):
    __tablename__ = 'feature_relationshipprop_pub'
    __table_args__ = (
        UniqueConstraint('feature_relationshipprop_id', 'pub_id'),
    )

    feature_relationshipprop_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('feature_relationshipprop_pub_feature_relationshipprop_pub_i_seq'::regclass)"))
    feature_relationshipprop_id = Column(ForeignKey('feature_relationshipprop.feature_relationshipprop_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    feature_relationshipprop = relationship('FeatureRelationshipprop')
    pub = relationship('Pub')


