from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class LibraryHumanhealthprop(Base):
    __tablename__ = 'library_humanhealthprop'
    __table_args__ = (
        UniqueConstraint('library_humanhealth_id', 'type_id', 'rank'),
    )

    library_humanhealthprop_id = Column(Integer, primary_key=True, server_default=text("nextval('library_humanhealthprop_library_humanhealthprop_id_seq'::regclass)"))
    library_humanhealth_id = Column(ForeignKey('library_humanhealth.library_humanhealth_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    library_humanhealth = relationship('LibraryHumanhealth')
    type = relationship('Cvterm')


