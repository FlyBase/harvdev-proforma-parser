from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class LibraryCvterm(Base):
    __tablename__ = 'library_cvterm'
    __table_args__ = (
        UniqueConstraint('library_id', 'cvterm_id', 'pub_id'),
    )

    library_cvterm_id = Column(Integer, primary_key=True, server_default=text("nextval('library_cvterm_library_cvterm_id_seq'::regclass)"))
    library_id = Column(ForeignKey('library.library_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    cvterm_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    cvterm = relationship('Cvterm')
    library = relationship('Library')
    pub = relationship('Pub')


