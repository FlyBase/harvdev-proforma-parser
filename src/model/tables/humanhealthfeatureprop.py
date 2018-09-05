from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class HumanhealthFeatureprop(Base):
    __tablename__ = 'humanhealth_featureprop'
    __table_args__ = (
        UniqueConstraint('humanhealth_feature_id', 'type_id', 'rank'),
    )

    humanhealth_featureprop_id = Column(Integer, primary_key=True, server_default=text("nextval('humanhealth_featureprop_humanhealth_featureprop_id_seq'::regclass)"))
    humanhealth_feature_id = Column(ForeignKey('humanhealth_feature.humanhealth_feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    humanhealth_feature = relationship('HumanhealthFeature')
    type = relationship('Cvterm')


