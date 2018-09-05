from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class HumanhealthFeature(Base):
    __tablename__ = 'humanhealth_feature'
    __table_args__ = (
        UniqueConstraint('humanhealth_id', 'feature_id', 'pub_id'),
    )

    humanhealth_feature_id = Column(Integer, primary_key=True, server_default=text("nextval('humanhealth_feature_humanhealth_feature_id_seq'::regclass)"))
    humanhealth_id = Column(ForeignKey('humanhealth.humanhealth_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    feature_id = Column(ForeignKey('feature.feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)

    feature = relationship('Feature')
    humanhealth = relationship('Humanhealth')
    pub = relationship('Pub')


