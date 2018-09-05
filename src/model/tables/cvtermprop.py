from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Cvtermprop(Base):
    __tablename__ = 'cvtermprop'
    __table_args__ = (
        UniqueConstraint('cvterm_id', 'type_id', 'value', 'rank'),
    )

    cvtermprop_id = Column(Integer, primary_key=True, server_default=text("nextval('cvtermprop_cvtermprop_id_seq'::regclass)"))
    cvterm_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text, nullable=False, server_default=text("''::text"))
    rank = Column(Integer, nullable=False, server_default=text("0"))

    cvterm = relationship('Cvterm', primaryjoin='Cvtermprop.cvterm_id == Cvterm.cvterm_id')
    type = relationship('Cvterm', primaryjoin='Cvtermprop.type_id == Cvterm.cvterm_id')


