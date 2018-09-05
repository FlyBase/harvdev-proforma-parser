from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Analysisgrpmember(Base):
    __tablename__ = 'analysisgrpmember'
    __table_args__ = (
        UniqueConstraint('analysis_id', 'grpmember_id'),
    )

    analysisgrpmember_id = Column(Integer, primary_key=True, server_default=text("nextval('analysisgrpmember_analysisgrpmember_id_seq'::regclass)"))
    rawscore = Column(Float(53))
    normscore = Column(Float(53))
    significance = Column(Float(53))
    identity = Column(Float(53))
    analysis_id = Column(ForeignKey('analysis.analysis_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    grpmember_id = Column(ForeignKey('grpmember.grpmember_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    analysis = relationship('Analysi')
    grpmember = relationship('Grpmember')


