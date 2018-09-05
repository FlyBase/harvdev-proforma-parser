from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Tableinfo(Base):
    __tablename__ = 'tableinfo'

    tableinfo_id = Column(Integer, primary_key=True, server_default=text("nextval('tableinfo_tableinfo_id_seq'::regclass)"))
    name = Column(String(30), nullable=False, unique=True)
    primary_key_column = Column(String(30))
    is_view = Column(Integer, nullable=False, server_default=text("0"))
    view_on_table_id = Column(Integer)
    superclass_table_id = Column(Integer)
    is_updateable = Column(Integer, nullable=False, server_default=text("1"))
    modification_date = Column(Date, nullable=False, server_default=text("now()"))


