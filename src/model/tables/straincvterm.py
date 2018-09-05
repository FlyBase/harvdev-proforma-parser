from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class StrainCvterm(Base):
    __tablename__ = 'strain_cvterm'
    __table_args__ = (
        UniqueConstraint('strain_id', 'cvterm_id', 'pub_id'),
    )

    strain_cvterm_id = Column(Integer, primary_key=True, server_default=text("nextval('strain_cvterm_strain_cvterm_id_seq'::regclass)"))
    strain_id = Column(ForeignKey('strain.strain_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    cvterm_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)

    cvterm = relationship('Cvterm')
    pub = relationship('Pub')
    strain = relationship('Strain')


