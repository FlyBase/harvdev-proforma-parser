from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class LibrarypropPub(Base):
    __tablename__ = 'libraryprop_pub'
    __table_args__ = (
        UniqueConstraint('libraryprop_id', 'pub_id'),
    )

    libraryprop_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('libraryprop_pub_libraryprop_pub_id_seq'::regclass)"))
    libraryprop_id = Column(ForeignKey('libraryprop.libraryprop_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    libraryprop = relationship('Libraryprop')
    pub = relationship('Pub')


