from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class GrppropPub(Base):
    __tablename__ = 'grpprop_pub'
    __table_args__ = (
        UniqueConstraint('pub_id', 'grpprop_id'),
    )

    grpprop_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('grpprop_pub_grpprop_pub_id_seq'::regclass)"))
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    grpprop_id = Column(ForeignKey('grpprop.grpprop_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    grpprop = relationship('Grpprop')
    pub = relationship('Pub')


