from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Eimage(Base):
    __tablename__ = 'eimage'

    eimage_id = Column(Integer, primary_key=True, server_default=text("nextval('eimage_eimage_id_seq'::regclass)"))
    eimage_data = Column(Text)
    eimage_type = Column(String(255), nullable=False)
    image_uri = Column(String(255))


