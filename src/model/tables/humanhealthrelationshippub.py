from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class HumanhealthRelationshipPub(Base):
    __tablename__ = 'humanhealth_relationship_pub'
    __table_args__ = (
        UniqueConstraint('humanhealth_relationship_id', 'pub_id'),
    )

    humanhealth_relationship_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('humanhealth_relationship_pub_humanhealth_relationship_pub_i_seq'::regclass)"))
    humanhealth_relationship_id = Column(ForeignKey('humanhealth_relationship.humanhealth_relationship_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    humanhealth_relationship = relationship('HumanhealthRelationship')
    pub = relationship('Pub')


