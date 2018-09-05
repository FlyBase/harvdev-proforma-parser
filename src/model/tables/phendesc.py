from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Phendesc(Base):
    __tablename__ = 'phendesc'
    __table_args__ = (
        UniqueConstraint('genotype_id', 'environment_id', 'type_id', 'pub_id'),
    )

    phendesc_id = Column(Integer, primary_key=True, server_default=text("nextval('phendesc_phendesc_id_seq'::regclass)"))
    genotype_id = Column(ForeignKey('genotype.genotype_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    environment_id = Column(ForeignKey('environment.environment_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    description = Column(Text, nullable=False)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    environment = relationship('Environment')
    genotype = relationship('Genotype')
    pub = relationship('Pub')
    type = relationship('Cvterm')


