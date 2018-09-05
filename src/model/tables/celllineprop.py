from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class CellLineprop(Base):
    __tablename__ = 'cell_lineprop'
    __table_args__ = (
        UniqueConstraint('cell_line_id', 'type_id', 'rank'),
    )

    cell_lineprop_id = Column(Integer, primary_key=True, server_default=text("nextval('cell_lineprop_cell_lineprop_id_seq'::regclass)"))
    cell_line_id = Column(ForeignKey('cell_line.cell_line_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    cell_line = relationship('CellLine')
    type = relationship('Cvterm')


