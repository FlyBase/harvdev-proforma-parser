from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class GrpDbxref(Base):
    __tablename__ = 'grp_dbxref'
    __table_args__ = (
        UniqueConstraint('dbxref_id', 'grp_id'),
    )

    grp_dbxref_id = Column(Integer, primary_key=True, server_default=text("nextval('grp_dbxref_grp_dbxref_id_seq'::regclass)"))
    is_current = Column(Boolean, nullable=False, server_default=text("true"))
    dbxref_id = Column(ForeignKey('dbxref.dbxref_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    grp_id = Column(ForeignKey('grp.grp_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    dbxref = relationship('Dbxref')
    grp = relationship('Grp')


