from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class LibraryGrpmember(Base):
    __tablename__ = 'library_grpmember'
    __table_args__ = (
        UniqueConstraint('grpmember_id', 'library_id'),
    )

    library_grpmember_id = Column(Integer, primary_key=True, server_default=text("nextval('library_grpmember_library_grpmember_id_seq'::regclass)"))
    grpmember_id = Column(ForeignKey('grpmember.grpmember_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    library_id = Column(ForeignKey('library.library_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    grpmember = relationship('Grpmember')
    library = relationship('Library')


