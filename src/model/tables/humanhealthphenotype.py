from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class HumanhealthPhenotype(Base):
    __tablename__ = 'humanhealth_phenotype'
    __table_args__ = (
        UniqueConstraint('humanhealth_id', 'phenotype_id', 'pub_id'),
    )

    humanhealth_phenotype_id = Column(Integer, primary_key=True, server_default=text("nextval('humanhealth_phenotype_humanhealth_phenotype_id_seq'::regclass)"))
    humanhealth_id = Column(ForeignKey('humanhealth.humanhealth_id', ondelete='CASCADE'), nullable=False, index=True)
    phenotype_id = Column(ForeignKey('phenotype.phenotype_id', ondelete='CASCADE'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)

    humanhealth = relationship('Humanhealth')
    phenotype = relationship('Phenotype')
    pub = relationship('Pub')


