from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Pub(Base):
    __tablename__ = 'pub'

    pub_id = Column(Integer, primary_key=True, server_default=text("nextval('pub_pub_id_seq'::regclass)"))
    title = Column(Text)
    volumetitle = Column(Text)
    volume = Column(String(255))
    series_name = Column(String(255))
    issue = Column(String(255))
    pyear = Column(String(255))
    pages = Column(String(255))
    miniref = Column(String(255))
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_obsolete = Column(Boolean, server_default=text("false"))
    publisher = Column(String(255))
    pubplace = Column(String(255))
    uniquename = Column(Text, nullable=False, unique=True)

    type = relationship('Cvterm')


