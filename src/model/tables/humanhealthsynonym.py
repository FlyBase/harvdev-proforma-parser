from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class HumanhealthSynonym(Base):
    __tablename__ = 'humanhealth_synonym'
    __table_args__ = (
        UniqueConstraint('synonym_id', 'humanhealth_id', 'pub_id'),
    )

    humanhealth_synonym_id = Column(Integer, primary_key=True, server_default=text("nextval('humanhealth_synonym_humanhealth_synonym_id_seq'::regclass)"))
    humanhealth_id = Column(ForeignKey('humanhealth.humanhealth_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    synonym_id = Column(ForeignKey('synonym.synonym_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_current = Column(Boolean, nullable=False, server_default=text("false"))
    is_internal = Column(Boolean, nullable=False, server_default=text("false"))

    humanhealth = relationship('Humanhealth')
    pub = relationship('Pub')
    synonym = relationship('Synonym')


