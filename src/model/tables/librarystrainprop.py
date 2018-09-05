from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class LibraryStrainprop(Base):
    __tablename__ = 'library_strainprop'
    __table_args__ = (
        UniqueConstraint('library_strain_id', 'type_id', 'rank'),
    )

    library_strainprop_id = Column(Integer, primary_key=True, server_default=text("nextval('library_strainprop_library_strainprop_id_seq'::regclass)"))
    library_strain_id = Column(ForeignKey('library_strain.library_strain_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    library_strain = relationship('LibraryStrain')
    type = relationship('Cvterm')


