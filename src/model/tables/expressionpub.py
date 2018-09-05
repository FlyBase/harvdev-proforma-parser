from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class ExpressionPub(Base):
    __tablename__ = 'expression_pub'
    __table_args__ = (
        UniqueConstraint('expression_id', 'pub_id'),
    )

    expression_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('expression_pub_expression_pub_id_seq'::regclass)"))
    expression_id = Column(ForeignKey('expression.expression_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    expression = relationship('Expression')
    pub = relationship('Pub')


