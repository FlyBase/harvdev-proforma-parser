from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class GrpRelationship(Base):
    __tablename__ = 'grp_relationship'
    __table_args__ = (
        UniqueConstraint('rank', 'type_id', 'subject_id', 'object_id'),
    )

    grp_relationship_id = Column(Integer, primary_key=True, server_default=text("nextval('grp_relationship_grp_relationship_id_seq'::regclass)"))
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    subject_id = Column(ForeignKey('grp.grp_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    object_id = Column(ForeignKey('grp.grp_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    object = relationship('Grp', primaryjoin='GrpRelationship.object_id == Grp.grp_id')
    subject = relationship('Grp', primaryjoin='GrpRelationship.subject_id == Grp.grp_id')
    type = relationship('Cvterm')


