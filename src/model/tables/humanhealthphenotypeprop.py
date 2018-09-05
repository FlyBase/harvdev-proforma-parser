from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class HumanhealthPhenotypeprop(Base):
    __tablename__ = 'humanhealth_phenotypeprop'
    __table_args__ = (
        UniqueConstraint('humanhealth_phenotype_id', 'type_id', 'rank'),
    )

    humanhealth_phenotypeprop_id = Column(Integer, primary_key=True, server_default=text("nextval('humanhealth_phenotypeprop_humanhealth_phenotypeprop_id_seq'::regclass)"))
    humanhealth_phenotype_id = Column(ForeignKey('humanhealth_phenotype.humanhealth_phenotype_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    humanhealth_phenotype = relationship('HumanhealthPhenotype')
    type = relationship('Cvterm')


