from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Expression(Base):
    __tablename__ = 'expression'

    expression_id = Column(Integer, primary_key=True, server_default=text("nextval('expression_expression_id_seq'::regclass)"))
    uniquename = Column(Text, nullable=False, unique=True)
    md5checksum = Column(String(32))
    description = Column(Text)


