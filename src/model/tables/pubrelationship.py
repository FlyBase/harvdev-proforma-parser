from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class PubRelationship(Base):
    __tablename__ = 'pub_relationship'
    __table_args__ = (
        UniqueConstraint('subject_id', 'object_id', 'type_id'),
    )

    pub_relationship_id = Column(Integer, primary_key=True, server_default=text("nextval('pub_relationship_pub_relationship_id_seq'::regclass)"))
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    subject_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    object_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)

    object = relationship('Pub', primaryjoin='PubRelationship.object_id == Pub.pub_id')
    subject = relationship('Pub', primaryjoin='PubRelationship.subject_id == Pub.pub_id')
    type = relationship('Cvterm')


