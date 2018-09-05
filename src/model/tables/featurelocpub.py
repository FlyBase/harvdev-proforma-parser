from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class FeaturelocPub(Base):
    __tablename__ = 'featureloc_pub'
    __table_args__ = (
        UniqueConstraint('featureloc_id', 'pub_id'),
    )

    featureloc_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('featureloc_pub_featureloc_pub_id_seq'::regclass)"))
    featureloc_id = Column(ForeignKey('featureloc.featureloc_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    featureloc = relationship('Featureloc')
    pub = relationship('Pub')


