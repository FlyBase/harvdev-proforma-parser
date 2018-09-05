from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class LibraryStrain(Base):
    __tablename__ = 'library_strain'
    __table_args__ = (
        UniqueConstraint('strain_id', 'library_id', 'pub_id'),
    )

    library_strain_id = Column(Integer, primary_key=True, server_default=text("nextval('library_strain_library_strain_id_seq'::regclass)"))
    strain_id = Column(ForeignKey('strain.strain_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    library_id = Column(ForeignKey('library.library_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)

    library = relationship('Library')
    pub = relationship('Pub')
    strain = relationship('Strain')


