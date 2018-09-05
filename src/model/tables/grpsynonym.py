from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class GrpSynonym(Base):
    __tablename__ = 'grp_synonym'
    __table_args__ = (
        UniqueConstraint('synonym_id', 'grp_id', 'pub_id'),
    )

    grp_synonym_id = Column(Integer, primary_key=True, server_default=text("nextval('grp_synonym_grp_synonym_id_seq'::regclass)"))
    synonym_id = Column(ForeignKey('synonym.synonym_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    grp_id = Column(ForeignKey('grp.grp_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_current = Column(Boolean, nullable=False, server_default=text("false"))
    is_internal = Column(Boolean, nullable=False, server_default=text("false"))

    grp = relationship('Grp')
    pub = relationship('Pub')
    synonym = relationship('Synonym')


