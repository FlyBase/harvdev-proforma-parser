from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class GrpRelationshipPub(Base):
    __tablename__ = 'grp_relationship_pub'
    __table_args__ = (
        UniqueConstraint('pub_id', 'grp_relationship_id'),
    )

    grp_relationship_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('grp_relationship_pub_grp_relationship_pub_id_seq'::regclass)"))
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    grp_relationship_id = Column(ForeignKey('grp_relationship.grp_relationship_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    grp_relationship = relationship('GrpRelationship')
    pub = relationship('Pub')


