from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class LibraryInteraction(Base):
    __tablename__ = 'library_interaction'
    __table_args__ = (
        UniqueConstraint('interaction_id', 'library_id', 'pub_id'),
    )

    library_interaction_id = Column(Integer, primary_key=True, server_default=text("nextval('library_interaction_library_interaction_id_seq'::regclass)"))
    interaction_id = Column(ForeignKey('interaction.interaction_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    library_id = Column(ForeignKey('library.library_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    interaction = relationship('Interaction')
    library = relationship('Library')
    pub = relationship('Pub')


