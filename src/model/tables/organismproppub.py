from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class OrganismpropPub(Base):
    __tablename__ = 'organismprop_pub'
    __table_args__ = (
        UniqueConstraint('organismprop_id', 'pub_id'),
    )

    organismprop_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('organismprop_pub_organismprop_pub_id_seq'::regclass)"))
    organismprop_id = Column(ForeignKey('organismprop.organismprop_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    organismprop = relationship('Organismprop')
    pub = relationship('Pub')


