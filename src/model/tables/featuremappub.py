from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class FeaturemapPub(Base):
    __tablename__ = 'featuremap_pub'

    featuremap_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('featuremap_pub_featuremap_pub_id_seq'::regclass)"))
    featuremap_id = Column(ForeignKey('featuremap.featuremap_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    featuremap = relationship('Featuremap')
    pub = relationship('Pub')


