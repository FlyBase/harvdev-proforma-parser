from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class StrainPhenotypeprop(Base):
    __tablename__ = 'strain_phenotypeprop'
    __table_args__ = (
        UniqueConstraint('strain_phenotype_id', 'type_id', 'rank'),
    )

    strain_phenotypeprop_id = Column(Integer, primary_key=True, server_default=text("nextval('strain_phenotypeprop_strain_phenotypeprop_id_seq'::regclass)"))
    strain_phenotype_id = Column(ForeignKey('strain_phenotype.strain_phenotype_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    strain_phenotype = relationship('StrainPhenotype')
    type = relationship('Cvterm')


