from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class HumanhealthRelationship(Base):
    __tablename__ = 'humanhealth_relationship'
    __table_args__ = (
        UniqueConstraint('subject_id', 'object_id', 'type_id', 'rank'),
    )

    humanhealth_relationship_id = Column(Integer, primary_key=True, server_default=text("nextval('humanhealth_relationship_humanhealth_relationship_id_seq'::regclass)"))
    subject_id = Column(ForeignKey('humanhealth.humanhealth_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    object_id = Column(ForeignKey('humanhealth.humanhealth_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    object = relationship('Humanhealth', primaryjoin='HumanhealthRelationship.object_id == Humanhealth.humanhealth_id')
    subject = relationship('Humanhealth', primaryjoin='HumanhealthRelationship.subject_id == Humanhealth.humanhealth_id')
    type = relationship('Cvterm')


