from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata

t_af_type = Table(
    'af_type', metadata,
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
    Column('analysis_id', Integer),
    Column('timeaccessioned', DateTime),
    Column('timelastmodified', DateTime)
)


t_alignment_evidence = Table(
    'alignment_evidence', metadata,
    Column('alignment_evidence_id', Text),
    Column('feature_id', Integer),
    Column('evidence_id', Integer),
    Column('analysis_id', Integer)
)


class Analysi(Base):
    __tablename__ = 'analysis'
    __table_args__ = (
        UniqueConstraint('program', 'programversion', 'sourcename'),
    )

    analysis_id = Column(Integer, primary_key=True, server_default=text("nextval('analysis_analysis_id_seq'::regclass)"))
    name = Column(String(255))
    description = Column(Text)
    program = Column(String(255), nullable=False)
    programversion = Column(String(255), nullable=False)
    algorithm = Column(String(255))
    sourcename = Column(String(255), index=True)
    sourceversion = Column(String(255))
    sourceuri = Column(Text)
    timeexecuted = Column(DateTime, nullable=False, server_default=text("('now'::text)::timestamp(6) with time zone"))
