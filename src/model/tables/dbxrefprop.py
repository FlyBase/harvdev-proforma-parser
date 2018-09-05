from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Dbxrefprop(Base):
    __tablename__ = 'dbxrefprop'
    __table_args__ = (
        UniqueConstraint('dbxref_id', 'type_id', 'rank'),
    )

    dbxrefprop_id = Column(Integer, primary_key=True, server_default=text("nextval('dbxrefprop_dbxrefprop_id_seq'::regclass)"))
    dbxref_id = Column(ForeignKey('dbxref.dbxref_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text, nullable=False, server_default=text("''::text"))
    rank = Column(Integer, nullable=False, server_default=text("0"))

    dbxref = relationship('Dbxref')
    type = relationship('Cvterm')


