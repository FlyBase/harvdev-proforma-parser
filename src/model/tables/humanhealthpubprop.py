from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class HumanhealthPubprop(Base):
    __tablename__ = 'humanhealth_pubprop'
    __table_args__ = (
        UniqueConstraint('rank', 'type_id', 'humanhealth_pub_id'),
    )

    humanhealth_pubprop_id = Column(Integer, primary_key=True, server_default=text("nextval('humanhealth_pubprop_humanhealth_pubprop_id_seq'::regclass)"))
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    humanhealth_pub_id = Column(ForeignKey('humanhealth_pub.humanhealth_pub_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    humanhealth_pub = relationship('HumanhealthPub')
    type = relationship('Cvterm')


