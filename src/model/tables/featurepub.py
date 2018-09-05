from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class FeaturePub(Base):
    __tablename__ = 'feature_pub'
    __table_args__ = (
        UniqueConstraint('feature_id', 'pub_id'),
    )

    feature_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('feature_pub_feature_pub_id_seq'::regclass)"))
    feature_id = Column(ForeignKey('feature.feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    feature = relationship('Feature')
    pub = relationship('Pub')


