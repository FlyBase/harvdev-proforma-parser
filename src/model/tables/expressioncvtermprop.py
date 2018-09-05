from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class ExpressionCvtermprop(Base):
    __tablename__ = 'expression_cvtermprop'
    __table_args__ = (
        UniqueConstraint('expression_cvterm_id', 'type_id', 'rank'),
    )

    expression_cvtermprop_id = Column(Integer, primary_key=True, server_default=text("nextval('expression_cvtermprop_expression_cvtermprop_id_seq'::regclass)"))
    expression_cvterm_id = Column(ForeignKey('expression_cvterm.expression_cvterm_id', ondelete='CASCADE'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    expression_cvterm = relationship('ExpressionCvterm')
    type = relationship('Cvterm')


