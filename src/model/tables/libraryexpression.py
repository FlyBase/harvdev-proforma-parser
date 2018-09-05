from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class LibraryExpression(Base):
    __tablename__ = 'library_expression'
    __table_args__ = (
        UniqueConstraint('expression_id', 'library_id', 'pub_id'),
    )

    library_expression_id = Column(Integer, primary_key=True, server_default=text("nextval('library_expression_library_expression_id_seq'::regclass)"))
    expression_id = Column(ForeignKey('expression.expression_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    library_id = Column(ForeignKey('library.library_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    expression = relationship('Expression')
    library = relationship('Library')
    pub = relationship('Pub')


