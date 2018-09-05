from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class CellLineCvtermprop(Base):
    __tablename__ = 'cell_line_cvtermprop'
    __table_args__ = (
        UniqueConstraint('cell_line_cvterm_id', 'type_id', 'rank'),
    )

    cell_line_cvtermprop_id = Column(Integer, primary_key=True, server_default=text("nextval('cell_line_cvtermprop_cell_line_cvtermprop_id_seq'::regclass)"))
    cell_line_cvterm_id = Column(ForeignKey('cell_line_cvterm.cell_line_cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    cell_line_cvterm = relationship('CellLineCvterm')
    type = relationship('Cvterm')


