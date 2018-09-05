from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Phenotype(Base):
    __tablename__ = 'phenotype'

    phenotype_id = Column(Integer, primary_key=True, server_default=text("nextval('phenotype_phenotype_id_seq'::regclass)"))
    uniquename = Column(Text, nullable=False, unique=True)
    observable_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), index=True)
    attr_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='SET NULL'), index=True)
    value = Column(Text)
    cvalue_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='SET NULL'), index=True)
    assay_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='SET NULL'))

    assay = relationship('Cvterm', primaryjoin='Phenotype.assay_id == Cvterm.cvterm_id')
    attr = relationship('Cvterm', primaryjoin='Phenotype.attr_id == Cvterm.cvterm_id')
    cvalue = relationship('Cvterm', primaryjoin='Phenotype.cvalue_id == Cvterm.cvterm_id')
    observable = relationship('Cvterm', primaryjoin='Phenotype.observable_id == Cvterm.cvterm_id')


