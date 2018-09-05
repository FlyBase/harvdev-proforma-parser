from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class CellLineFeature(Base):
    __tablename__ = 'cell_line_feature'
    __table_args__ = (
        UniqueConstraint('cell_line_id', 'feature_id', 'pub_id'),
    )

    cell_line_feature_id = Column(Integer, primary_key=True, server_default=text("nextval('cell_line_feature_cell_line_feature_id_seq'::regclass)"))
    cell_line_id = Column(ForeignKey('cell_line.cell_line_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    feature_id = Column(ForeignKey('feature.feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)

    cell_line = relationship('CellLine')
    feature = relationship('Feature')
    pub = relationship('Pub')


