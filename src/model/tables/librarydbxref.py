from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class LibraryDbxref(Base):
    __tablename__ = 'library_dbxref'
    __table_args__ = (
        UniqueConstraint('library_id', 'dbxref_id'),
    )

    library_dbxref_id = Column(Integer, primary_key=True, server_default=text("nextval('library_dbxref_library_dbxref_id_seq'::regclass)"))
    library_id = Column(ForeignKey('library.library_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    dbxref_id = Column(ForeignKey('dbxref.dbxref_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_current = Column(Boolean, nullable=False, server_default=text("true"))

    dbxref = relationship('Dbxref')
    library = relationship('Library')


