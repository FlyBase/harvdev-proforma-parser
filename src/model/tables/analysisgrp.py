from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Analysisgrp(Base):
    __tablename__ = 'analysisgrp'
    __table_args__ = (
        UniqueConstraint('analysis_id', 'grp_id'),
    )

    analysisgrp_id = Column(Integer, primary_key=True, server_default=text("nextval('analysisgrp_analysisgrp_id_seq'::regclass)"))
    rawscore = Column(Float(53))
    normscore = Column(Float(53))
    significance = Column(Float(53))
    identity = Column(Float(53))
    analysis_id = Column(ForeignKey('analysis.analysis_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    grp_id = Column(ForeignKey('grp.grp_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    analysis = relationship('Analysi')
    grp = relationship('Grp')


