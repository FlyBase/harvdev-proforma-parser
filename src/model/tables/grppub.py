from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class GrpPub(Base):
    __tablename__ = 'grp_pub'
    __table_args__ = (
        UniqueConstraint('pub_id', 'grp_id'),
    )

    grp_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('grp_pub_grp_pub_id_seq'::regclass)"))
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    grp_id = Column(ForeignKey('grp.grp_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    grp = relationship('Grp')
    pub = relationship('Pub')


