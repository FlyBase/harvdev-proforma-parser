from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Pubauthor(Base):
    __tablename__ = 'pubauthor'
    __table_args__ = (
        UniqueConstraint('pub_id', 'rank'),
    )

    pubauthor_id = Column(Integer, primary_key=True, server_default=text("nextval('pubauthor_pubauthor_id_seq'::regclass)"))
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    rank = Column(Integer, nullable=False)
    editor = Column(Boolean, server_default=text("false"))
    surname = Column(String(100), nullable=False)
    givennames = Column(String(100))
    suffix = Column(String(100))

    pub = relationship('Pub')


