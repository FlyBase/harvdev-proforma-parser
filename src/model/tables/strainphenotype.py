from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class StrainPhenotype(Base):
    __tablename__ = 'strain_phenotype'
    __table_args__ = (
        UniqueConstraint('strain_id', 'phenotype_id', 'pub_id'),
    )

    strain_phenotype_id = Column(Integer, primary_key=True, server_default=text("nextval('strain_phenotype_strain_phenotype_id_seq'::regclass)"))
    strain_id = Column(ForeignKey('strain.strain_id', ondelete='CASCADE'), nullable=False, index=True)
    phenotype_id = Column(ForeignKey('phenotype.phenotype_id', ondelete='CASCADE'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)

    phenotype = relationship('Phenotype')
    pub = relationship('Pub')
    strain = relationship('Strain')


