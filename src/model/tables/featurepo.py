from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Featurepo(Base):
    __tablename__ = 'featurepos'

    featurepos_id = Column(Integer, primary_key=True, server_default=text("nextval('featurepos_featurepos_id_seq'::regclass)"))
    featuremap_id = Column(ForeignKey('featuremap.featuremap_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True, server_default=text("nextval('featurepos_featuremap_id_seq'::regclass)"))
    feature_id = Column(ForeignKey('feature.feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    map_feature_id = Column(ForeignKey('feature.feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    mappos = Column(Float(53), nullable=False)

    feature = relationship('Feature', primaryjoin='Featurepo.feature_id == Feature.feature_id')
    featuremap = relationship('Featuremap')
    map_feature = relationship('Feature', primaryjoin='Featurepo.map_feature_id == Feature.feature_id')


