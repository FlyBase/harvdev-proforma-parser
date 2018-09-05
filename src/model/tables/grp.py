from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Grp(Base):
    __tablename__ = 'grp'
    __table_args__ = (
        UniqueConstraint('uniquename', 'type_id'),
    )

    grp_id = Column(Integer, primary_key=True, server_default=text("nextval('grp_grp_id_seq'::regclass)"))
    name = Column(String(255), index=True)
    uniquename = Column(Text, nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_analysis = Column(Boolean, nullable=False, server_default=text("false"))
    is_obsolete = Column(Boolean, nullable=False, server_default=text("false"))

    type = relationship('Cvterm')


