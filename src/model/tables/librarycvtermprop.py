from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class LibraryCvtermprop(Base):
    __tablename__ = 'library_cvtermprop'
    __table_args__ = (
        UniqueConstraint('library_cvterm_id', 'type_id', 'rank'),
    )

    library_cvtermprop_id = Column(Integer, primary_key=True, server_default=text("nextval('library_cvtermprop_library_cvtermprop_id_seq'::regclass)"))
    library_cvterm_id = Column(ForeignKey('library_cvterm.library_cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    library_cvterm = relationship('LibraryCvterm')
    type = relationship('Cvterm')


