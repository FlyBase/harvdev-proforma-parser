from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class CellLineStrain(Base):
    __tablename__ = 'cell_line_strain'
    __table_args__ = (
        UniqueConstraint('strain_id', 'cell_line_id', 'pub_id'),
    )

    cell_line_strain_id = Column(Integer, primary_key=True, server_default=text("nextval('cell_line_strain_cell_line_strain_id_seq'::regclass)"))
    strain_id = Column(ForeignKey('strain.strain_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    cell_line_id = Column(ForeignKey('cell_line.cell_line_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)

    cell_line = relationship('CellLine')
    pub = relationship('Pub')
    strain = relationship('Strain')


