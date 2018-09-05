from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Dbxref(Base):
    __tablename__ = 'dbxref'
    __table_args__ = (
        UniqueConstraint('db_id', 'accession', 'version'),
    )

    dbxref_id = Column(Integer, primary_key=True, server_default=text("nextval('dbxref_dbxref_id_seq'::regclass)"))
    db_id = Column(ForeignKey('db.db_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    accession = Column(String(255), nullable=False, index=True)
    version = Column(String(255), nullable=False, index=True, server_default=text("''::character varying"))
    description = Column(Text)
    url = Column(String(255))

    db = relationship('Db')


