from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class FeaturepropPub(Base):
    __tablename__ = 'featureprop_pub'
    __table_args__ = (
        UniqueConstraint('featureprop_id', 'pub_id'),
    )

    featureprop_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('featureprop_pub_featureprop_pub_id_seq'::regclass)"))
    featureprop_id = Column(ForeignKey('featureprop.featureprop_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    featureprop = relationship('Featureprop')
    pub = relationship('Pub')


