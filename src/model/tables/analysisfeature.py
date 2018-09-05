from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Analysisfeature(Base):
    __tablename__ = 'analysisfeature'
    __table_args__ = (
        UniqueConstraint('feature_id', 'analysis_id'),
    )

    analysisfeature_id = Column(Integer, primary_key=True, server_default=text("nextval('analysisfeature_analysisfeature_id_seq'::regclass)"))
    feature_id = Column(ForeignKey('feature.feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    analysis_id = Column(ForeignKey('analysis.analysis_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    rawscore = Column(Float(53))
    normscore = Column(Float(53))
    significance = Column(Float(53))
    identity = Column(Float(53))

    analysis = relationship('Analysi')
    feature = relationship('Feature')


