from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class StrainFeature(Base):
    __tablename__ = 'strain_feature'
    __table_args__ = (
        UniqueConstraint('strain_id', 'feature_id', 'pub_id'),
    )

    strain_feature_id = Column(Integer, primary_key=True, server_default=text("nextval('strain_feature_strain_feature_id_seq'::regclass)"))
    strain_id = Column(ForeignKey('strain.strain_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    feature_id = Column(ForeignKey('feature.feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)

    feature = relationship('Feature')
    pub = relationship('Pub')
    strain = relationship('Strain')


