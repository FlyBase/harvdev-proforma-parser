from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class CellLinepropPub(Base):
    __tablename__ = 'cell_lineprop_pub'
    __table_args__ = (
        UniqueConstraint('cell_lineprop_id', 'pub_id'),
    )

    cell_lineprop_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('cell_lineprop_pub_cell_lineprop_pub_id_seq'::regclass)"))
    cell_lineprop_id = Column(ForeignKey('cell_lineprop.cell_lineprop_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)

    cell_lineprop = relationship('CellLineprop')
    pub = relationship('Pub')


