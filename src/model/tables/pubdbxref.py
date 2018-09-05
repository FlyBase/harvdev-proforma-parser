from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class PubDbxref(Base):
    __tablename__ = 'pub_dbxref'
    __table_args__ = (
        UniqueConstraint('pub_id', 'dbxref_id'),
    )

    pub_dbxref_id = Column(Integer, primary_key=True, server_default=text("nextval('pub_dbxref_pub_dbxref_id_seq'::regclass)"))
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    dbxref_id = Column(ForeignKey('dbxref.dbxref_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_current = Column(Boolean, nullable=False, server_default=text("true"))

    dbxref = relationship('Dbxref')
    pub = relationship('Pub')


