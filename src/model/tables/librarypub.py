from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class LibraryPub(Base):
    __tablename__ = 'library_pub'
    __table_args__ = (
        UniqueConstraint('library_id', 'pub_id'),
    )

    library_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('library_pub_library_pub_id_seq'::regclass)"))
    library_id = Column(ForeignKey('library.library_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    library = relationship('Library')
    pub = relationship('Pub')


