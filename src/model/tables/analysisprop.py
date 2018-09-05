from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Analysisprop(Base):
    __tablename__ = 'analysisprop'
    __table_args__ = (
        UniqueConstraint('analysis_id', 'type_id', 'value'),
    )

    analysisprop_id = Column(Integer, primary_key=True, server_default=text("nextval('analysisprop_analysisprop_id_seq'::regclass)"))
    analysis_id = Column(ForeignKey('analysis.analysis_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)

    analysis = relationship('Analysi')
    type = relationship('Cvterm')


