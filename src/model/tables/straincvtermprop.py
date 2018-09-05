from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class StrainCvtermprop(Base):
    __tablename__ = 'strain_cvtermprop'
    __table_args__ = (
        UniqueConstraint('strain_cvterm_id', 'type_id', 'rank'),
    )

    strain_cvtermprop_id = Column(Integer, primary_key=True, server_default=text("nextval('strain_cvtermprop_strain_cvtermprop_id_seq'::regclass)"))
    strain_cvterm_id = Column(ForeignKey('strain_cvterm.strain_cvterm_id', ondelete='CASCADE'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    strain_cvterm = relationship('StrainCvterm')
    type = relationship('Cvterm')


