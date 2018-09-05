from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class FeatureCvtermDbxref(Base):
    __tablename__ = 'feature_cvterm_dbxref'
    __table_args__ = (
        UniqueConstraint('feature_cvterm_id', 'dbxref_id'),
    )

    feature_cvterm_dbxref_id = Column(Integer, primary_key=True, server_default=text("nextval('feature_cvterm_dbxref_feature_cvterm_dbxref_id_seq'::regclass)"))
    feature_cvterm_id = Column(ForeignKey('feature_cvterm.feature_cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    dbxref_id = Column(ForeignKey('dbxref.dbxref_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    dbxref = relationship('Dbxref')
    feature_cvterm = relationship('FeatureCvterm')


