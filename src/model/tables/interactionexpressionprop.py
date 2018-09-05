from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class InteractionExpressionprop(Base):
    __tablename__ = 'interaction_expressionprop'
    __table_args__ = (
        UniqueConstraint('interaction_expression_id', 'type_id', 'rank'),
    )

    interaction_expressionprop_id = Column(Integer, primary_key=True, server_default=text("nextval('interaction_expressionprop_interaction_expressionprop_id_seq'::regclass)"))
    interaction_expression_id = Column(ForeignKey('interaction_expression.interaction_expression_id', ondelete='CASCADE'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    interaction_expression = relationship('InteractionExpression')
    type = relationship('Cvterm')


