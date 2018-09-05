from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class CvtermDbxref(Base):
    __tablename__ = 'cvterm_dbxref'
    __table_args__ = (
        UniqueConstraint('cvterm_id', 'dbxref_id'),
    )

    cvterm_dbxref_id = Column(Integer, primary_key=True, server_default=text("nextval('cvterm_dbxref_cvterm_dbxref_id_seq'::regclass)"))
    cvterm_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    dbxref_id = Column(ForeignKey('dbxref.dbxref_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_for_definition = Column(Integer, nullable=False, server_default=text("0"))

    cvterm = relationship('Cvterm')
    dbxref = relationship('Dbxref')


