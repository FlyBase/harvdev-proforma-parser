from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class StrainDbxref(Base):
    __tablename__ = 'strain_dbxref'
    __table_args__ = (
        UniqueConstraint('strain_id', 'dbxref_id'),
    )

    strain_dbxref_id = Column(Integer, primary_key=True, server_default=text("nextval('strain_dbxref_strain_dbxref_id_seq'::regclass)"))
    strain_id = Column(ForeignKey('strain.strain_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    dbxref_id = Column(ForeignKey('dbxref.dbxref_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_current = Column(Boolean, nullable=False, server_default=text("true"))

    dbxref = relationship('Dbxref')
    strain = relationship('Strain')


