from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Featureloc(Base):
    __tablename__ = 'featureloc'
    __table_args__ = (
        CheckConstraint('fmin <= fmax'),
        UniqueConstraint('feature_id', 'locgroup', 'rank'),
        Index('featureloc_idx3', 'srcfeature_id', 'fmin', 'fmax')
    )

    featureloc_id = Column(Integer, primary_key=True, server_default=text("nextval('featureloc_featureloc_id_seq'::regclass)"))
    feature_id = Column(ForeignKey('feature.feature_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    srcfeature_id = Column(ForeignKey('feature.feature_id', ondelete='SET NULL'), index=True)
    fmin = Column(Integer, index=True)
    is_fmin_partial = Column(Boolean, nullable=False, server_default=text("false"))
    fmax = Column(Integer, index=True)
    is_fmax_partial = Column(Boolean, nullable=False, server_default=text("false"))
    strand = Column(SmallInteger)
    phase = Column(Integer)
    residue_info = Column(Text)
    locgroup = Column(Integer, nullable=False, server_default=text("0"))
    rank = Column(Integer, nullable=False, server_default=text("0"))

    feature = relationship('Feature', primaryjoin='Featureloc.feature_id == Feature.feature_id')
    srcfeature = relationship('Feature', primaryjoin='Featureloc.srcfeature_id == Feature.feature_id')


t_featureloc_allcoords = Table(
    'featureloc_allcoords', metadata,
    Column('featureloc_id', Integer),
    Column('feature_id', Integer),
    Column('srcfeature_id', Integer),
    Column('fmin', Integer),
    Column('is_fmin_partial', Boolean),
    Column('fmax', Integer),
    Column('is_fmax_partial', Boolean),
    Column('strand', SmallInteger),
    Column('phase', Integer),
    Column('residue_info', Text),
    Column('locgroup', Integer),
    Column('rank', Integer),
    Column('gbeg', Integer),
    Column('gend', Integer),
    Column('nbeg', Integer),
    Column('nend', Integer)
)


