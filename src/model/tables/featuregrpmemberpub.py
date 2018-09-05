from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class FeatureGrpmemberPub(Base):
    __tablename__ = 'feature_grpmember_pub'
    __table_args__ = (
        UniqueConstraint('pub_id', 'feature_grpmember_id'),
    )

    feature_grpmember_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('feature_grpmember_pub_feature_grpmember_pub_id_seq'::regclass)"))
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    feature_grpmember_id = Column(ForeignKey('feature_grpmember.feature_grpmember_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    feature_grpmember = relationship('FeatureGrpmember')
    pub = relationship('Pub')


