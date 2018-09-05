from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class LibraryFeatureprop(Base):
    __tablename__ = 'library_featureprop'
    __table_args__ = (
        UniqueConstraint('library_feature_id', 'type_id', 'rank'),
    )

    library_featureprop_id = Column(Integer, primary_key=True, server_default=text("nextval('library_featureprop_library_featureprop_id_seq'::regclass)"))
    library_feature_id = Column(ForeignKey('library_feature.library_feature_id', ondelete='CASCADE'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    library_feature = relationship('LibraryFeature')
    type = relationship('Cvterm')


