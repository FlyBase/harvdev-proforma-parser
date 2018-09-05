from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class GrpmemberPub(Base):
    __tablename__ = 'grpmember_pub'
    __table_args__ = (
        UniqueConstraint('pub_id', 'grpmember_id'),
    )

    grpmember_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('grpmember_pub_grpmember_pub_id_seq'::regclass)"))
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    grpmember_id = Column(ForeignKey('grpmember.grpmember_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    grpmember = relationship('Grpmember')
    pub = relationship('Pub')


