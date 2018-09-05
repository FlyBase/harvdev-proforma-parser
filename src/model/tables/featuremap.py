from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Featuremap(Base):
    __tablename__ = 'featuremap'

    featuremap_id = Column(Integer, primary_key=True, server_default=text("nextval('featuremap_featuremap_id_seq'::regclass)"))
    name = Column(String(255), unique=True)
    description = Column(Text)
    unittype_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'))

    unittype = relationship('Cvterm')


