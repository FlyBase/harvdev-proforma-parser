from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class CellLineRelationship(Base):
    __tablename__ = 'cell_line_relationship'
    __table_args__ = (
        UniqueConstraint('subject_id', 'object_id', 'type_id'),
    )

    cell_line_relationship_id = Column(Integer, primary_key=True, server_default=text("nextval('cell_line_relationship_cell_line_relationship_id_seq'::regclass)"))
    subject_id = Column(ForeignKey('cell_line.cell_line_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    object_id = Column(ForeignKey('cell_line.cell_line_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)

    object = relationship('CellLine', primaryjoin='CellLineRelationship.object_id == CellLine.cell_line_id')
    subject = relationship('CellLine', primaryjoin='CellLineRelationship.subject_id == CellLine.cell_line_id')
    type = relationship('Cvterm')


