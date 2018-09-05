from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class LibraryHumanhealth(Base):
    __tablename__ = 'library_humanhealth'
    __table_args__ = (
        UniqueConstraint('humanhealth_id', 'library_id', 'pub_id'),
    )

    library_humanhealth_id = Column(Integer, primary_key=True, server_default=text("nextval('library_humanhealth_library_humanhealth_id_seq'::regclass)"))
    humanhealth_id = Column(ForeignKey('humanhealth.humanhealth_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    library_id = Column(ForeignKey('library.library_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)

    humanhealth = relationship('Humanhealth')
    library = relationship('Library')
    pub = relationship('Pub')


