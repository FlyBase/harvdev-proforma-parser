from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Contact(Base):
    __tablename__ = 'contact'

    contact_id = Column(Integer, primary_key=True, server_default=text("nextval('contact_contact_id_seq'::regclass)"))
    description = Column(String(255))
    name = Column(String(30), nullable=False, unique=True)


