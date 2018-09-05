from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Cvtermsynonym(Base):
    __tablename__ = 'cvtermsynonym'
    __table_args__ = (
        UniqueConstraint('cvterm_id', 'name'),
    )

    cvtermsynonym_id = Column(Integer, primary_key=True, server_default=text("nextval('cvtermsynonym_cvtermsynonym_id_seq'::regclass)"))
    cvterm_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    name = Column(String(1024), nullable=False)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'))

    cvterm = relationship('Cvterm', primaryjoin='Cvtermsynonym.cvterm_id == Cvterm.cvterm_id')
    type = relationship('Cvterm', primaryjoin='Cvtermsynonym.type_id == Cvterm.cvterm_id')


