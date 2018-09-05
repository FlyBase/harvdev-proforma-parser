from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class FeatureExpression(Base):
    __tablename__ = 'feature_expression'
    __table_args__ = (
        UniqueConstraint('expression_id', 'feature_id', 'pub_id'),
    )

    feature_expression_id = Column(Integer, primary_key=True, server_default=text("nextval('feature_expression_feature_expression_id_seq'::regclass)"))
    expression_id = Column(ForeignKey('expression.expression_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    feature_id = Column(ForeignKey('feature.feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    expression = relationship('Expression')
    feature = relationship('Feature')
    pub = relationship('Pub')


