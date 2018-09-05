from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class OrganismGrpmember(Base):
    __tablename__ = 'organism_grpmember'
    __table_args__ = (
        UniqueConstraint('grpmember_id', 'organism_id'),
    )

    organism_grpmember_id = Column(Integer, primary_key=True, server_default=text("nextval('organism_grpmember_organism_grpmember_id_seq'::regclass)"))
    grpmember_id = Column(ForeignKey('grpmember.grpmember_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    organism_id = Column(ForeignKey('organism.organism_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    grpmember = relationship('Grpmember')
    organism = relationship('Organism')


