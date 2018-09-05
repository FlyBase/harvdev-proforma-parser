from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Phenstatement(Base):
    __tablename__ = 'phenstatement'
    __table_args__ = (
        UniqueConstraint('genotype_id', 'phenotype_id', 'environment_id', 'type_id', 'pub_id'),
    )

    phenstatement_id = Column(Integer, primary_key=True, server_default=text("nextval('phenstatement_phenstatement_id_seq'::regclass)"))
    genotype_id = Column(ForeignKey('genotype.genotype_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    environment_id = Column(ForeignKey('environment.environment_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    phenotype_id = Column(ForeignKey('phenotype.phenotype_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)

    environment = relationship('Environment')
    genotype = relationship('Genotype')
    phenotype = relationship('Phenotype')
    pub = relationship('Pub')
    type = relationship('Cvterm')


t_prediction_evidence = Table(
    'prediction_evidence', metadata,
    Column('prediction_evidence_id', Text),
    Column('feature_id', Integer),
    Column('evidence_id', Integer),
    Column('analysis_id', Integer)
)


