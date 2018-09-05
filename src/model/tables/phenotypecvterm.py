from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class PhenotypeCvterm(Base):
    __tablename__ = 'phenotype_cvterm'
    __table_args__ = (
        UniqueConstraint('phenotype_id', 'cvterm_id', 'rank'),
    )

    phenotype_cvterm_id = Column(Integer, primary_key=True, server_default=text("nextval('phenotype_cvterm_phenotype_cvterm_id_seq'::regclass)"))
    phenotype_id = Column(ForeignKey('phenotype.phenotype_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    cvterm_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    cvterm = relationship('Cvterm')
    phenotype = relationship('Phenotype')


