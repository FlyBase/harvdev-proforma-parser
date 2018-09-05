from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class FeatureGenotype(Base):
    __tablename__ = 'feature_genotype'
    __table_args__ = (
        UniqueConstraint('feature_id', 'genotype_id', 'cvterm_id', 'chromosome_id', 'rank', 'cgroup'),
    )

    feature_genotype_id = Column(Integer, primary_key=True, server_default=text("nextval('feature_genotype_feature_genotype_id_seq'::regclass)"))
    feature_id = Column(ForeignKey('feature.feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    genotype_id = Column(ForeignKey('genotype.genotype_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    chromosome_id = Column(ForeignKey('feature.feature_id', ondelete='SET NULL'))
    rank = Column(Integer, nullable=False)
    cgroup = Column(Integer, nullable=False)
    cvterm_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)

    chromosome = relationship('Feature', primaryjoin='FeatureGenotype.chromosome_id == Feature.feature_id')
    cvterm = relationship('Cvterm')
    feature = relationship('Feature', primaryjoin='FeatureGenotype.feature_id == Feature.feature_id')
    genotype = relationship('Genotype')


