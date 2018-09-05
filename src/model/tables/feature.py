from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Feature(Base):
    __tablename__ = 'feature'
    __table_args__ = (
        UniqueConstraint('organism_id', 'uniquename', 'type_id'),
    )

    feature_id = Column(Integer, primary_key=True, server_default=text("nextval('feature_feature_id_seq'::regclass)"))
    dbxref_id = Column(ForeignKey('dbxref.dbxref_id', ondelete='SET NULL'), index=True)
    organism_id = Column(ForeignKey('organism.organism_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    name = Column(String(255), index=True)
    uniquename = Column(Text, nullable=False, index=True)
    residues = Column(Text)
    seqlen = Column(Integer)
    md5checksum = Column(String(32))
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_analysis = Column(Boolean, nullable=False, server_default=text("false"))
    timeaccessioned = Column(DateTime, nullable=False, server_default=text("('now'::text)::timestamp(6) with time zone"))
    timelastmodified = Column(DateTime, nullable=False, server_default=text("('now'::text)::timestamp(6) with time zone"))
    is_obsolete = Column(Boolean, nullable=False, server_default=text("false"))

    dbxref = relationship('Dbxref')
    organism = relationship('Organism')
    type = relationship('Cvterm')
    featuresynonym = relationship('FeatureSynonym')

    __mapper_args__ = {'polymorphic_on': type_id}