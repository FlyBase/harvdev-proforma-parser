from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class StrainRelationship(Base):
    __tablename__ = 'strain_relationship'
    __table_args__ = (
        UniqueConstraint('subject_id', 'object_id', 'type_id', 'rank'),
    )

    strain_relationship_id = Column(Integer, primary_key=True, server_default=text("nextval('strain_relationship_strain_relationship_id_seq'::regclass)"))
    subject_id = Column(ForeignKey('strain.strain_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    object_id = Column(ForeignKey('strain.strain_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    object = relationship('Strain', primaryjoin='StrainRelationship.object_id == Strain.strain_id')
    subject = relationship('Strain', primaryjoin='StrainRelationship.subject_id == Strain.strain_id')
    type = relationship('Cvterm')


