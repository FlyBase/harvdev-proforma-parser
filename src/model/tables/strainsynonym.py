from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class StrainSynonym(Base):
    __tablename__ = 'strain_synonym'
    __table_args__ = (
        UniqueConstraint('synonym_id', 'strain_id', 'pub_id'),
    )

    strain_synonym_id = Column(Integer, primary_key=True, server_default=text("nextval('strain_synonym_strain_synonym_id_seq'::regclass)"))
    strain_id = Column(ForeignKey('strain.strain_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    synonym_id = Column(ForeignKey('synonym.synonym_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    is_current = Column(Boolean, nullable=False, server_default=text("false"))
    is_internal = Column(Boolean, nullable=False, server_default=text("false"))

    pub = relationship('Pub')
    strain = relationship('Strain')
    synonym = relationship('Synonym')


