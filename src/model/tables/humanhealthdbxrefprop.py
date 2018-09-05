from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class HumanhealthDbxrefprop(Base):
    __tablename__ = 'humanhealth_dbxrefprop'
    __table_args__ = (
        UniqueConstraint('humanhealth_dbxref_id', 'type_id', 'rank'),
    )

    humanhealth_dbxrefprop_id = Column(Integer, primary_key=True, server_default=text("nextval('humanhealth_dbxrefprop_humanhealth_dbxrefprop_id_seq'::regclass)"))
    humanhealth_dbxref_id = Column(ForeignKey('humanhealth_dbxref.humanhealth_dbxref_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    humanhealth_dbxref = relationship('HumanhealthDbxref')
    type = relationship('Cvterm')


