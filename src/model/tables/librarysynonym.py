from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class LibrarySynonym(Base):
    __tablename__ = 'library_synonym'
    __table_args__ = (
        UniqueConstraint('synonym_id', 'library_id', 'pub_id'),
    )

    library_synonym_id = Column(Integer, primary_key=True, server_default=text("nextval('library_synonym_library_synonym_id_seq'::regclass)"))
    synonym_id = Column(ForeignKey('synonym.synonym_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    library_id = Column(ForeignKey('library.library_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_current = Column(Boolean, nullable=False, server_default=text("true"))
    is_internal = Column(Boolean, nullable=False, server_default=text("false"))

    library = relationship('Library')
    pub = relationship('Pub')
    synonym = relationship('Synonym')


