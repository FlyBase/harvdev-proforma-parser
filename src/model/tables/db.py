from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Db(Base):
    __tablename__ = 'db'

    db_id = Column(Integer, primary_key=True, server_default=text("nextval('db_db_id_seq'::regclass)"))
    name = Column(String(255), nullable=False, unique=True)
    contact_id = Column(ForeignKey('contact.contact_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'))
    description = Column(String(255))
    urlprefix = Column(String(255))
    url = Column(String(255))

    contact = relationship('Contact')


