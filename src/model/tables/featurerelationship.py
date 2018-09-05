from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class FeatureRelationship(Base):
    __tablename__ = 'feature_relationship'
    __table_args__ = (
        UniqueConstraint('subject_id', 'object_id', 'type_id', 'rank'),
    )

    feature_relationship_id = Column(Integer, primary_key=True, server_default=text("nextval('feature_relationship_feature_relationship_id_seq'::regclass)"))
    subject_id = Column(ForeignKey('feature.feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    object_id = Column(ForeignKey('feature.feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    rank = Column(Integer, nullable=False, server_default=text("0"))
    value = Column(Text)

    object = relationship('Feature', primaryjoin='FeatureRelationship.object_id == Feature.feature_id')
    subject = relationship('Feature', primaryjoin='FeatureRelationship.subject_id == Feature.feature_id')
    type = relationship('Cvterm')


