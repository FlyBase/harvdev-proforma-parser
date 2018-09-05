from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class CvtermRelationship(Base):
    __tablename__ = 'cvterm_relationship'
    __table_args__ = (
        UniqueConstraint('type_id', 'subject_id', 'object_id'),
    )

    cvterm_relationship_id = Column(Integer, primary_key=True, server_default=text("nextval('cvterm_relationship_cvterm_relationship_id_seq'::regclass)"))
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    subject_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    object_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    object = relationship('Cvterm', primaryjoin='CvtermRelationship.object_id == Cvterm.cvterm_id')
    subject = relationship('Cvterm', primaryjoin='CvtermRelationship.subject_id == Cvterm.cvterm_id')
    type = relationship('Cvterm', primaryjoin='CvtermRelationship.type_id == Cvterm.cvterm_id')


t_cvterm_type = Table(
    'cvterm_type', metadata,
    Column('cvterm_id', Integer),
    Column('name', String(1024)),
    Column('termtype', String(255))
)


