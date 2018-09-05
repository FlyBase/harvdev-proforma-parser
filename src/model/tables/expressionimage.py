from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class ExpressionImage(Base):
    __tablename__ = 'expression_image'
    __table_args__ = (
        UniqueConstraint('expression_id', 'eimage_id'),
    )

    expression_image_id = Column(Integer, primary_key=True, server_default=text("nextval('expression_image_expression_image_id_seq'::regclass)"))
    expression_id = Column(ForeignKey('expression.expression_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    eimage_id = Column(ForeignKey('eimage.eimage_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    eimage = relationship('Eimage')
    expression = relationship('Expression')


