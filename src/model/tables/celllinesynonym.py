from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class CellLineSynonym(Base):
    __tablename__ = 'cell_line_synonym'
    __table_args__ = (
        UniqueConstraint('synonym_id', 'cell_line_id', 'pub_id'),
    )

    cell_line_synonym_id = Column(Integer, primary_key=True, server_default=text("nextval('cell_line_synonym_cell_line_synonym_id_seq'::regclass)"))
    cell_line_id = Column(ForeignKey('cell_line.cell_line_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    synonym_id = Column(ForeignKey('synonym.synonym_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    is_current = Column(Boolean, nullable=False, server_default=text("false"))
    is_internal = Column(Boolean, nullable=False, server_default=text("false"))

    cell_line = relationship('CellLine')
    pub = relationship('Pub')
    synonym = relationship('Synonym')


