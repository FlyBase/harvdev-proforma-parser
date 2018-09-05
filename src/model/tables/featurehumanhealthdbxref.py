from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class FeatureHumanhealthDbxref(Base):
    __tablename__ = 'feature_humanhealth_dbxref'
    __table_args__ = (
        UniqueConstraint('humanhealth_dbxref_id', 'feature_id', 'pub_id'),
    )

    feature_humanhealth_dbxref_id = Column(Integer, primary_key=True, server_default=text("nextval('feature_humanhealth_dbxref_feature_humanhealth_dbxref_id_seq'::regclass)"))
    humanhealth_dbxref_id = Column(ForeignKey('humanhealth_dbxref.humanhealth_dbxref_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    feature_id = Column(ForeignKey('feature.feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)

    feature = relationship('Feature')
    humanhealth_dbxref = relationship('HumanhealthDbxref')
    pub = relationship('Pub')


