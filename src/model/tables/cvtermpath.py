from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Cvtermpath(Base):
    __tablename__ = 'cvtermpath'
    __table_args__ = (
        UniqueConstraint('subject_id', 'object_id'),
    )

    cvtermpath_id = Column(Integer, primary_key=True, server_default=text("nextval('cvtermpath_cvtermpath_id_seq'::regclass)"))
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='SET NULL'), index=True)
    subject_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    object_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    cv_id = Column(Integer, nullable=False, index=True)
    pathdistance = Column(Integer)

    object = relationship('Cvterm', primaryjoin='Cvtermpath.object_id == Cvterm.cvterm_id')
    subject = relationship('Cvterm', primaryjoin='Cvtermpath.subject_id == Cvterm.cvterm_id')
    type = relationship('Cvterm', primaryjoin='Cvtermpath.type_id == Cvterm.cvterm_id')


