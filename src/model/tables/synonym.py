from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Synonym(Base):
    __tablename__ = 'synonym'
    __table_args__ = (
        UniqueConstraint('name', 'type_id', 'synonym_sgml'),
    )

    synonym_id = Column(Integer, primary_key=True, server_default=text("nextval('synonym_synonym_id_seq'::regclass)"))
    name = Column(String(255), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    synonym_sgml = Column(String(255), nullable=False, index=True)

    type = relationship('Cvterm')