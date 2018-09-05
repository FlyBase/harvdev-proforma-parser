from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class InteractionCellLine(Base):
    __tablename__ = 'interaction_cell_line'
    __table_args__ = (
        UniqueConstraint('cell_line_id', 'interaction_id', 'pub_id'),
    )

    interaction_cell_line_id = Column(Integer, primary_key=True, server_default=text("nextval('interaction_cell_line_interaction_cell_line_id_seq'::regclass)"))
    cell_line_id = Column(ForeignKey('cell_line.cell_line_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    interaction_id = Column(ForeignKey('interaction.interaction_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    cell_line = relationship('CellLine')
    interaction = relationship('Interaction')
    pub = relationship('Pub')


