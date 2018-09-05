from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class FeatureCvtermprop(Base):
    __tablename__ = 'feature_cvtermprop'
    __table_args__ = (
        UniqueConstraint('feature_cvterm_id', 'type_id', 'rank'),
    )

    feature_cvtermprop_id = Column(Integer, primary_key=True, server_default=text("nextval('feature_cvtermprop_feature_cvtermprop_id_seq'::regclass)"))
    feature_cvterm_id = Column(ForeignKey('feature_cvterm.feature_cvterm_id', ondelete='CASCADE'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    feature_cvterm = relationship('FeatureCvterm')
    type = relationship('Cvterm')


