from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class FeatureRelationshipprop(Base):
    __tablename__ = 'feature_relationshipprop'
    __table_args__ = (
        UniqueConstraint('feature_relationship_id', 'type_id', 'rank'),
    )

    feature_relationshipprop_id = Column(Integer, primary_key=True, server_default=text("nextval('feature_relationshipprop_feature_relationshipprop_id_seq'::regclass)"))
    feature_relationship_id = Column(ForeignKey('feature_relationship.feature_relationship_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    feature_relationship = relationship('FeatureRelationship')
    type = relationship('Cvterm')


