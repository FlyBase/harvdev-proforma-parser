from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class InteractionExpression(Base):
    __tablename__ = 'interaction_expression'
    __table_args__ = (
        UniqueConstraint('expression_id', 'interaction_id', 'pub_id'),
    )

    interaction_expression_id = Column(Integer, primary_key=True, server_default=text("nextval('interaction_expression_interaction_expression_id_seq'::regclass)"))
    expression_id = Column(ForeignKey('expression.expression_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    interaction_id = Column(ForeignKey('interaction.interaction_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    expression = relationship('Expression')
    interaction = relationship('Interaction')
    pub = relationship('Pub')


