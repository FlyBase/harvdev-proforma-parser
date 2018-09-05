from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class FeatureCvterm(Base):
    __tablename__ = 'feature_cvterm'
    __table_args__ = (
        UniqueConstraint('feature_id', 'cvterm_id', 'pub_id'),
    )

    feature_cvterm_id = Column(Integer, primary_key=True, server_default=text("nextval('feature_cvterm_feature_cvterm_id_seq'::regclass)"))
    feature_id = Column(ForeignKey('feature.feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    cvterm_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_not = Column(Boolean, nullable=False, server_default=text("false"))

    cvterm = relationship('Cvterm')
    feature = relationship('Feature')
    pub = relationship('Pub')


