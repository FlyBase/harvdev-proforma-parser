from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Grpmemberprop(Base):
    __tablename__ = 'grpmemberprop'
    __table_args__ = (
        UniqueConstraint('rank', 'type_id', 'grpmember_id'),
    )

    grpmemberprop_id = Column(Integer, primary_key=True, server_default=text("nextval('grpmemberprop_grpmemberprop_id_seq'::regclass)"))
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    grpmember_id = Column(ForeignKey('grpmember.grpmember_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    grpmember = relationship('Grpmember')
    type = relationship('Cvterm')


