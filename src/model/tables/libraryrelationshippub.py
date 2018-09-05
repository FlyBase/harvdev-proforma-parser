from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class LibraryRelationshipPub(Base):
    __tablename__ = 'library_relationship_pub'
    __table_args__ = (
        UniqueConstraint('library_relationship_id', 'pub_id'),
    )

    library_relationship_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('library_relationship_pub_library_relationship_pub_id_seq'::regclass)"))
    library_relationship_id = Column(ForeignKey('library_relationship.library_relationship_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    library_relationship = relationship('LibraryRelationship')
    pub = relationship('Pub')


