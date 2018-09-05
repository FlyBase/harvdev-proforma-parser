from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class LibraryFeature(Base):
    __tablename__ = 'library_feature'
    __table_args__ = (
        UniqueConstraint('library_id', 'feature_id'),
    )

    library_feature_id = Column(Integer, primary_key=True, server_default=text("nextval('library_feature_library_feature_id_seq'::regclass)"))
    library_id = Column(ForeignKey('library.library_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    feature_id = Column(ForeignKey('feature.feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    feature = relationship('Feature')
    library = relationship('Library')


