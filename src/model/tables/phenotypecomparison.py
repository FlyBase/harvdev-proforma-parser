from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class PhenotypeComparison(Base):
    __tablename__ = 'phenotype_comparison'
    __table_args__ = (
        UniqueConstraint('genotype1_id', 'environment1_id', 'genotype2_id', 'environment2_id', 'phenotype1_id', 'pub_id'),
    )

    phenotype_comparison_id = Column(Integer, primary_key=True, server_default=text("nextval('phenotype_comparison_phenotype_comparison_id_seq'::regclass)"))
    genotype1_id = Column(ForeignKey('genotype.genotype_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    environment1_id = Column(ForeignKey('environment.environment_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    genotype2_id = Column(ForeignKey('genotype.genotype_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    environment2_id = Column(ForeignKey('environment.environment_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    phenotype1_id = Column(ForeignKey('phenotype.phenotype_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    phenotype2_id = Column(ForeignKey('phenotype.phenotype_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'))
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    organism_id = Column(ForeignKey('organism.organism_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)

    environment1 = relationship('Environment', primaryjoin='PhenotypeComparison.environment1_id == Environment.environment_id')
    environment2 = relationship('Environment', primaryjoin='PhenotypeComparison.environment2_id == Environment.environment_id')
    genotype1 = relationship('Genotype', primaryjoin='PhenotypeComparison.genotype1_id == Genotype.genotype_id')
    genotype2 = relationship('Genotype', primaryjoin='PhenotypeComparison.genotype2_id == Genotype.genotype_id')
    organism = relationship('Organism')
    phenotype1 = relationship('Phenotype', primaryjoin='PhenotypeComparison.phenotype1_id == Phenotype.phenotype_id')
    phenotype2 = relationship('Phenotype', primaryjoin='PhenotypeComparison.phenotype2_id == Phenotype.phenotype_id')
    pub = relationship('Pub')


