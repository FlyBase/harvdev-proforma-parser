from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Libraryprop(Base):
    __tablename__ = 'libraryprop'
    __table_args__ = (
        UniqueConstraint('library_id', 'type_id', 'rank'),
    )

    libraryprop_id = Column(Integer, primary_key=True, server_default=text("nextval('libraryprop_libraryprop_id_seq'::regclass)"))
    library_id = Column(ForeignKey('library.library_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    library = relationship('Library')
    type = relationship('Cvterm')


