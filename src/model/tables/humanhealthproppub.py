from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class HumanhealthpropPub(Base):
    __tablename__ = 'humanhealthprop_pub'
    __table_args__ = (
        UniqueConstraint('humanhealthprop_id', 'pub_id'),
    )

    humanhealthprop_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('humanhealthprop_pub_humanhealthprop_pub_id_seq'::regclass)"))
    humanhealthprop_id = Column(ForeignKey('humanhealthprop.humanhealthprop_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    humanhealthprop = relationship('Humanhealthprop')
    pub = relationship('Pub')


