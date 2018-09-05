from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class GrpPubprop(Base):
    __tablename__ = 'grp_pubprop'
    __table_args__ = (
        UniqueConstraint('rank', 'type_id', 'grp_pub_id'),
    )

    grp_pubprop_id = Column(Integer, primary_key=True, server_default=text("nextval('grp_pubprop_grp_pubprop_id_seq'::regclass)"))
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    grp_pub_id = Column(ForeignKey('grp_pub.grp_pub_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    grp_pub = relationship('GrpPub')
    type = relationship('Cvterm')


