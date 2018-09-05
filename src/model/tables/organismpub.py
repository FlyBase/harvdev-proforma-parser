from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class OrganismPub(Base):
    __tablename__ = 'organism_pub'
    __table_args__ = (
        UniqueConstraint('organism_id', 'pub_id'),
    )

    organism_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('organism_pub_organism_pub_id_seq'::regclass)"))
    organism_id = Column(ForeignKey('organism.organism_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    organism = relationship('Organism')
    pub = relationship('Pub')


