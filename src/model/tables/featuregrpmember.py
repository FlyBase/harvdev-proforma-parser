from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class FeatureGrpmember(Base):
    __tablename__ = 'feature_grpmember'
    __table_args__ = (
        UniqueConstraint('grpmember_id', 'feature_id'),
    )

    feature_grpmember_id = Column(Integer, primary_key=True, server_default=text("nextval('feature_grpmember_feature_grpmember_id_seq'::regclass)"))
    grpmember_id = Column(ForeignKey('grpmember.grpmember_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    feature_id = Column(ForeignKey('feature.feature_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    feature = relationship('Feature')
    grpmember = relationship('Grpmember')


