from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class FeaturePubprop(Base):
    __tablename__ = 'feature_pubprop'
    __table_args__ = (
        UniqueConstraint('feature_pub_id', 'type_id', 'rank'),
    )

    feature_pubprop_id = Column(Integer, primary_key=True, server_default=text("nextval('feature_pubprop_feature_pubprop_id_seq'::regclass)"))
    feature_pub_id = Column(ForeignKey('feature_pub.feature_pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    feature_pub = relationship('FeaturePub')
    type = relationship('Cvterm')


