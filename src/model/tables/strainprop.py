from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Strainprop(Base):
    __tablename__ = 'strainprop'
    __table_args__ = (
        UniqueConstraint('strain_id', 'type_id', 'rank'),
    )

    strainprop_id = Column(Integer, primary_key=True, server_default=text("nextval('strainprop_strainprop_id_seq'::regclass)"))
    strain_id = Column(ForeignKey('strain.strain_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    strain = relationship('Strain')
    type = relationship('Cvterm')


