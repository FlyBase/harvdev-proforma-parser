from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class PhenotypeComparisonCvterm(Base):
    __tablename__ = 'phenotype_comparison_cvterm'
    __table_args__ = (
        UniqueConstraint('phenotype_comparison_id', 'cvterm_id'),
    )

    phenotype_comparison_cvterm_id = Column(Integer, primary_key=True, server_default=text("nextval('phenotype_comparison_cvterm_phenotype_comparison_cvterm_id_seq'::regclass)"))
    phenotype_comparison_id = Column(ForeignKey('phenotype_comparison.phenotype_comparison_id', ondelete='CASCADE'), nullable=False, index=True)
    cvterm_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE'), nullable=False, index=True)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    cvterm = relationship('Cvterm')
    phenotype_comparison = relationship('PhenotypeComparison')


