from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Grpmember(Base):
    __tablename__ = 'grpmember'
    __table_args__ = (
        UniqueConstraint('rank', 'type_id', 'grp_id'),
    )

    grpmember_id = Column(Integer, primary_key=True, server_default=text("nextval('grpmember_grpmember_id_seq'::regclass)"))
    rank = Column(Integer, nullable=False, server_default=text("0"))
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    grp_id = Column(ForeignKey('grp.grp_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    grp = relationship('Grp')
    type = relationship('Cvterm')


