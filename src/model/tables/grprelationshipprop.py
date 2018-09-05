from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class GrpRelationshipprop(Base):
    __tablename__ = 'grp_relationshipprop'
    __table_args__ = (
        UniqueConstraint('rank', 'type_id', 'grp_relationship_id'),
    )

    grp_relationshipprop_id = Column(Integer, primary_key=True, server_default=text("nextval('grp_relationshipprop_grp_relationshipprop_id_seq'::regclass)"))
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    grp_relationship_id = Column(ForeignKey('grp_relationship.grp_relationship_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    grp_relationship = relationship('GrpRelationship')
    type = relationship('Cvterm')


