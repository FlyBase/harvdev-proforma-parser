from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class LibraryDbxrefprop(Base):
    __tablename__ = 'library_dbxrefprop'
    __table_args__ = (
        UniqueConstraint('library_dbxref_id', 'type_id', 'rank'),
    )

    library_dbxrefprop_id = Column(Integer, primary_key=True, server_default=text("nextval('library_dbxrefprop_library_dbxrefprop_id_seq'::regclass)"))
    library_dbxref_id = Column(ForeignKey('library_dbxref.library_dbxref_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    library_dbxref = relationship('LibraryDbxref')
    type = relationship('Cvterm')


