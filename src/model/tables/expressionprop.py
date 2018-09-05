from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Expressionprop(Base):
    __tablename__ = 'expressionprop'
    __table_args__ = (
        UniqueConstraint('expression_id', 'type_id', 'rank'),
    )

    expressionprop_id = Column(Integer, primary_key=True, server_default=text("nextval('expressionprop_expressionprop_id_seq'::regclass)"))
    expression_id = Column(ForeignKey('expression.expression_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    expression = relationship('Expression')
    type = relationship('Cvterm')


t_f_loc = Table(
    'f_loc', metadata,
    Column('feature_id', Integer),
    Column('name', String(255)),
    Column('dbxref_id', Integer),
    Column('fmin', Integer),
    Column('fmax', Integer),
    Column('strand', SmallInteger)
)


t_f_type = Table(
    'f_type', metadata,
    Column('feature_id', Integer),
    Column('name', String(255)),
    Column('uniquename', Text),
    Column('dbxref_id', Integer),
    Column('type', String(1024)),
    Column('residues', Text),
    Column('seqlen', Integer),
    Column('md5checksum', String(32)),
    Column('type_id', Integer),
    Column('organism_id', Integer),
    Column('is_analysis', Boolean),
    Column('timeaccessioned', DateTime),
    Column('timelastmodified', DateTime)
)


