from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class FeatureSynonym(Base):
    __tablename__ = 'feature_synonym'
    __table_args__ = (
        UniqueConstraint('synonym_id', 'feature_id', 'pub_id'),
    )

    feature_synonym_id = Column(Integer, primary_key=True, server_default=text("nextval('feature_synonym_feature_synonym_id_seq'::regclass)"))
    synonym_id = Column(ForeignKey('synonym.synonym_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    feature_id = Column(ForeignKey('feature.feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_current = Column(Boolean, nullable=False, server_default=text("true"))
    is_internal = Column(Boolean, nullable=False, server_default=text("false"))

    feature = relationship('Feature')
    pub = relationship('Pub')
    synonym = relationship('Synonym')


