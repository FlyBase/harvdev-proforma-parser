from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class CellLineDbxref(Base):
    __tablename__ = 'cell_line_dbxref'
    __table_args__ = (
        UniqueConstraint('cell_line_id', 'dbxref_id'),
    )

    cell_line_dbxref_id = Column(Integer, primary_key=True, server_default=text("nextval('cell_line_dbxref_cell_line_dbxref_id_seq'::regclass)"))
    cell_line_id = Column(ForeignKey('cell_line.cell_line_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    dbxref_id = Column(ForeignKey('dbxref.dbxref_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    is_current = Column(Boolean, nullable=False, server_default=text("true"))

    cell_line = relationship('CellLine')
    dbxref = relationship('Dbxref')


