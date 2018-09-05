from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class FeatureDbxref(Base):
    __tablename__ = 'feature_dbxref'
    __table_args__ = (
        UniqueConstraint('feature_id', 'dbxref_id'),
    )

    feature_dbxref_id = Column(Integer, primary_key=True, server_default=text("nextval('feature_dbxref_feature_dbxref_id_seq'::regclass)"))
    feature_id = Column(ForeignKey('feature.feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    dbxref_id = Column(ForeignKey('dbxref.dbxref_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_current = Column(Boolean, nullable=False, server_default=text("true"))

    dbxref = relationship('Dbxref')
    feature = relationship('Feature')


