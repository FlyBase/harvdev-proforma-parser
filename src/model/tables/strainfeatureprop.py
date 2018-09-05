from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class StrainFeatureprop(Base):
    __tablename__ = 'strain_featureprop'
    __table_args__ = (
        UniqueConstraint('strain_feature_id', 'type_id', 'rank'),
    )

    strain_featureprop_id = Column(Integer, primary_key=True, server_default=text("nextval('strain_featureprop_strain_featureprop_id_seq'::regclass)"))
    strain_feature_id = Column(ForeignKey('strain_feature.strain_feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    strain_feature = relationship('StrainFeature')
    type = relationship('Cvterm')


