from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class LibraryExpressionprop(Base):
    __tablename__ = 'library_expressionprop'
    __table_args__ = (
        UniqueConstraint('library_expression_id', 'type_id', 'rank'),
    )

    library_expressionprop_id = Column(Integer, primary_key=True, server_default=text("nextval('library_expressionprop_library_expressionprop_id_seq'::regclass)"))
    library_expression_id = Column(ForeignKey('library_expression.library_expression_id', ondelete='CASCADE'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    library_expression = relationship('LibraryExpression')
    type = relationship('Cvterm')


