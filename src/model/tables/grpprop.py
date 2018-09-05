from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Grpprop(Base):
    __tablename__ = 'grpprop'
    __table_args__ = (
        UniqueConstraint('rank', 'type_id', 'grp_id'),
    )

    grpprop_id = Column(Integer, primary_key=True, server_default=text("nextval('grpprop_grpprop_id_seq'::regclass)"))
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    grp_id = Column(ForeignKey('grp.grp_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    grp = relationship('Grp')
    type = relationship('Cvterm')


