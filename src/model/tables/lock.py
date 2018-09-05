from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Lock(Base):
    __tablename__ = 'lock'
    __table_args__ = (
        UniqueConstraint('lockname', 'lockrank', 'locktype'),
    )

    lock_id = Column(Integer, primary_key=True, server_default=text("nextval('lock_lock_id_seq'::regclass)"))
    username = Column(String(20), nullable=False, server_default=text("'administrator'::character varying"))
    locktype = Column(String(20), nullable=False, server_default=text("'write'::character varying"))
    lockname = Column(String(100), nullable=False)
    lockrank = Column(Integer, nullable=False, server_default=text("0"))
    lockstatus = Column(Boolean, nullable=False, server_default=text("false"))
    timeaccessioend = Column(DateTime, nullable=False, server_default=text("now()"))
    timelastmodified = Column(DateTime, nullable=False, server_default=text("now()"))
    chadoxmlfile = Column(String(100))
    comment = Column(String(100))
    task = Column(String(50), nullable=False, server_default=text("'modify gene model'::character varying"))


