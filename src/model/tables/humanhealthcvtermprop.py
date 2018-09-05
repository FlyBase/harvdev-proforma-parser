from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class HumanhealthCvtermprop(Base):
    __tablename__ = 'humanhealth_cvtermprop'
    __table_args__ = (
        UniqueConstraint('humanhealth_cvterm_id', 'type_id', 'rank'),
    )

    humanhealth_cvtermprop_id = Column(Integer, primary_key=True, server_default=text("nextval('humanhealth_cvtermprop_humanhealth_cvtermprop_id_seq'::regclass)"))
    humanhealth_cvterm_id = Column(ForeignKey('humanhealth_cvterm.humanhealth_cvterm_id', ondelete='CASCADE'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    humanhealth_cvterm = relationship('HumanhealthCvterm')
    type = relationship('Cvterm')


