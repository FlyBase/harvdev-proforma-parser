from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Pubprop(Base):
    __tablename__ = 'pubprop'
    __table_args__ = (
        UniqueConstraint('pub_id', 'type_id', 'rank'),
    )

    pubprop_id = Column(Integer, primary_key=True, server_default=text("nextval('pubprop_pubprop_id_seq'::regclass)"))
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text, nullable=False)
    rank = Column(Integer)

    pub = relationship('Pub')
    type = relationship('Cvterm')


