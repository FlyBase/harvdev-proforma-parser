from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class StrainRelationshipPub(Base):
    __tablename__ = 'strain_relationship_pub'
    __table_args__ = (
        UniqueConstraint('strain_relationship_id', 'pub_id'),
    )

    strain_relationship_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('strain_relationship_pub_strain_relationship_pub_id_seq'::regclass)"))
    strain_relationship_id = Column(ForeignKey('strain_relationship.strain_relationship_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    pub = relationship('Pub')
    strain_relationship = relationship('StrainRelationship')


