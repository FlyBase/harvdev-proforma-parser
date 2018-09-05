from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class HumanhealthDbxref(Base):
    __tablename__ = 'humanhealth_dbxref'
    __table_args__ = (
        UniqueConstraint('humanhealth_id', 'dbxref_id'),
    )

    humanhealth_dbxref_id = Column(Integer, primary_key=True, server_default=text("nextval('humanhealth_dbxref_humanhealth_dbxref_id_seq'::regclass)"))
    humanhealth_id = Column(ForeignKey('humanhealth.humanhealth_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    dbxref_id = Column(ForeignKey('dbxref.dbxref_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_current = Column(Boolean, nullable=False, server_default=text("true"))

    dbxref = relationship('Dbxref')
    humanhealth = relationship('Humanhealth')


