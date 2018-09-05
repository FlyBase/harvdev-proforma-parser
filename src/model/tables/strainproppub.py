from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class StrainpropPub(Base):
    __tablename__ = 'strainprop_pub'
    __table_args__ = (
        UniqueConstraint('strainprop_id', 'pub_id'),
    )

    strainprop_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('strainprop_pub_strainprop_pub_id_seq'::regclass)"))
    strainprop_id = Column(ForeignKey('strainprop.strainprop_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    pub = relationship('Pub')
    strainprop = relationship('Strainprop')


