from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class GrpmemberpropPub(Base):
    __tablename__ = 'grpmemberprop_pub'
    __table_args__ = (
        UniqueConstraint('pub_id', 'grpmemberprop_id'),
    )

    grpmemberprop_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('grpmemberprop_pub_grpmemberprop_pub_id_seq'::regclass)"))
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    grpmemberprop_id = Column(ForeignKey('grpmemberprop.grpmemberprop_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    grpmemberprop = relationship('Grpmemberprop')
    pub = relationship('Pub')


