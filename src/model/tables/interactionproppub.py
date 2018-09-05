from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class InteractionpropPub(Base):
    __tablename__ = 'interactionprop_pub'
    __table_args__ = (
        UniqueConstraint('interactionprop_id', 'pub_id'),
    )

    interactionprop_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('interactionprop_pub_interactionprop_pub_id_seq'::regclass)"))
    interactionprop_id = Column(ForeignKey('interactionprop.interactionprop_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    interactionprop = relationship('Interactionprop')
    pub = relationship('Pub')


