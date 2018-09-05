from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class FeatureExpressionprop(Base):
    __tablename__ = 'feature_expressionprop'
    __table_args__ = (
        UniqueConstraint('feature_expression_id', 'type_id', 'rank'),
    )

    feature_expressionprop_id = Column(Integer, primary_key=True, server_default=text("nextval('feature_expressionprop_feature_expressionprop_id_seq'::regclass)"))
    feature_expression_id = Column(ForeignKey('feature_expression.feature_expression_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    feature_expression = relationship('FeatureExpression')
    type = relationship('Cvterm')


