from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class CellLine(Base):
    __tablename__ = 'cell_line'
    __table_args__ = (
        UniqueConstraint('uniquename', 'organism_id'),
    )

    cell_line_id = Column(Integer, primary_key=True, server_default=text("nextval('cell_line_cell_line_id_seq'::regclass)"))
    name = Column(String(255))
    uniquename = Column(String(255), nullable=False)
    organism_id = Column(ForeignKey('organism.organism_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    timeaccessioned = Column(DateTime, nullable=False, server_default=text("now()"))
    timelastmodified = Column(DateTime, nullable=False, server_default=text("now()"))

    organism = relationship('Organism')


