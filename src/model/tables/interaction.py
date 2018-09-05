from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Interaction(Base):
    __tablename__ = 'interaction'
    __table_args__ = (
        UniqueConstraint('uniquename', 'type_id'),
    )

    interaction_id = Column(Integer, primary_key=True, server_default=text("nextval('interaction_interaction_id_seq'::regclass)"))
    uniquename = Column(Text, nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    description = Column(Text)
    is_obsolete = Column(Boolean, nullable=False, server_default=text("false"))

    type = relationship('Cvterm')


