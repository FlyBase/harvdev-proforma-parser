from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Cvterm(Base):
    __tablename__ = 'cvterm'
    __table_args__ = (
        UniqueConstraint('cv_id', 'name', 'is_obsolete'),
    )

    cvterm_id = Column(Integer, primary_key=True, server_default=text("nextval('cvterm_cvterm_id_seq'::regclass)"))
    cv_id = Column(ForeignKey('cv.cv_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    definition = Column(Text)
    dbxref_id = Column(ForeignKey('dbxref.dbxref_id', ondelete='SET NULL'), nullable=False, unique=True)
    is_obsolete = Column(Integer, nullable=False, server_default=text("0"))
    is_relationshiptype = Column(Integer, nullable=False, server_default=text("0"))
    name = Column(String(1024), nullable=False, index=True)

    cv = relationship('Cv')
    dbxref = relationship('Dbxref', uselist=False)