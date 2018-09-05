from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Genotype(Base):
    __tablename__ = 'genotype'

    genotype_id = Column(Integer, primary_key=True, server_default=text("nextval('genotype_genotype_id_seq'::regclass)"))
    uniquename = Column(Text, nullable=False, unique=True)
    description = Column(String(255))
    name = Column(Text, index=True)


t_gffatts_slim = Table(
    'gffatts_slim', metadata,
    Column('feature_id', Integer),
    Column('type', String),
    Column('attribute', Text)
)


t_gffatts_slpar = Table(
    'gffatts_slpar', metadata,
    Column('feature_id', Integer),
    Column('type', String),
    Column('attribute', Text)
)


