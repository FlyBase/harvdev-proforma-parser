from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class InteractionGroup(Base):
    __tablename__ = 'interaction_group'

    interaction_group_id = Column(Integer, primary_key=True, server_default=text("nextval('interaction_group_interaction_group_id_seq'::regclass)"))
    uniquename = Column(Text, nullable=False, unique=True)
    is_obsolete = Column(Boolean, nullable=False, server_default=text("false"))
    description = Column(Text)


