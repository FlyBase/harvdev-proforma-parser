from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class CellLineLibraryprop(Base):
    __tablename__ = 'cell_line_libraryprop'
    __table_args__ = (
        UniqueConstraint('cell_line_library_id', 'type_id', 'rank'),
    )

    cell_line_libraryprop_id = Column(Integer, primary_key=True, server_default=text("nextval('cell_line_libraryprop_cell_line_libraryprop_id_seq'::regclass)"))
    cell_line_library_id = Column(ForeignKey('cell_line_library.cell_line_library_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    cell_line_library = relationship('CellLineLibrary')
    type = relationship('Cvterm')


