from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class InteractionPub(Base):
    __tablename__ = 'interaction_pub'
    __table_args__ = (
        UniqueConstraint('interaction_id', 'pub_id'),
    )

    interaction_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('interaction_pub_interaction_pub_id_seq'::regclass)"))
    interaction_id = Column(ForeignKey('interaction.interaction_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    interaction = relationship('Interaction')
    pub = relationship('Pub')


