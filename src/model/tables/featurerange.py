from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Featurerange(Base):
    __tablename__ = 'featurerange'

    featurerange_id = Column(Integer, primary_key=True, server_default=text("nextval('featurerange_featurerange_id_seq'::regclass)"))
    featuremap_id = Column(ForeignKey('featuremap.featuremap_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    feature_id = Column(ForeignKey('feature.feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    leftstartf_id = Column(ForeignKey('feature.feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    leftendf_id = Column(ForeignKey('feature.feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), index=True)
    rightstartf_id = Column(ForeignKey('feature.feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), index=True)
    rightendf_id = Column(ForeignKey('feature.feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    rangestr = Column(String(255))

    feature = relationship('Feature', primaryjoin='Featurerange.feature_id == Feature.feature_id')
    featuremap = relationship('Featuremap')
    leftendf = relationship('Feature', primaryjoin='Featurerange.leftendf_id == Feature.feature_id')
    leftstartf = relationship('Feature', primaryjoin='Featurerange.leftstartf_id == Feature.feature_id')
    rightendf = relationship('Feature', primaryjoin='Featurerange.rightendf_id == Feature.feature_id')
    rightstartf = relationship('Feature', primaryjoin='Featurerange.rightstartf_id == Feature.feature_id')


t_fnr_type = Table(
    'fnr_type', metadata,
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
    Column('timeaccessioned', DateTime),
    Column('timelastmodified', DateTime)
)


t_fp_key = Table(
    'fp_key', metadata,
    Column('featureprop_id', Integer),
    Column('feature_id', Integer),
    Column('type', String(1024)),
    Column('value', Text)
)


