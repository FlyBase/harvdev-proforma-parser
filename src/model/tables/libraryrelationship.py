from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class LibraryRelationship(Base):
    __tablename__ = 'library_relationship'
    __table_args__ = (
        UniqueConstraint('subject_id', 'object_id', 'type_id'),
    )

    library_relationship_id = Column(Integer, primary_key=True, server_default=text("nextval('library_relationship_library_relationship_id_seq'::regclass)"))
    subject_id = Column(ForeignKey('library.library_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    object_id = Column(ForeignKey('library.library_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    object = relationship('Library', primaryjoin='LibraryRelationship.object_id == Library.library_id')
    subject = relationship('Library', primaryjoin='LibraryRelationship.subject_id == Library.library_id')
    type = relationship('Cvterm')


