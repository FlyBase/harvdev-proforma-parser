from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class FeaturePhenotype(Base):
    __tablename__ = 'feature_phenotype'
    __table_args__ = (
        UniqueConstraint('feature_id', 'phenotype_id'),
    )

    feature_phenotype_id = Column(Integer, primary_key=True, server_default=text("nextval('feature_phenotype_feature_phenotype_id_seq'::regclass)"))
    feature_id = Column(ForeignKey('feature.feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    phenotype_id = Column(ForeignKey('phenotype.phenotype_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    feature = relationship('Feature')
    phenotype = relationship('Phenotype')


