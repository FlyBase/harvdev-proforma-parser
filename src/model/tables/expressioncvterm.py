from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class ExpressionCvterm(Base):
    __tablename__ = 'expression_cvterm'
    __table_args__ = (
        UniqueConstraint('expression_id', 'cvterm_id', 'rank', 'cvterm_type_id'),
    )

    expression_cvterm_id = Column(Integer, primary_key=True, server_default=text("nextval('expression_cvterm_expression_cvterm_id_seq'::regclass)"))
    expression_id = Column(ForeignKey('expression.expression_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    cvterm_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    rank = Column(Integer, nullable=False, server_default=text("0"))
    cvterm_type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    cvterm = relationship('Cvterm', primaryjoin='ExpressionCvterm.cvterm_id == Cvterm.cvterm_id')
    cvterm_type = relationship('Cvterm', primaryjoin='ExpressionCvterm.cvterm_type_id == Cvterm.cvterm_id')
    expression = relationship('Expression')


