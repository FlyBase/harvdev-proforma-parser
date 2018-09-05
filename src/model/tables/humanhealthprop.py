from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class Humanhealthprop(Base):
    __tablename__ = 'humanhealthprop'
    __table_args__ = (
        UniqueConstraint('humanhealth_id', 'type_id', 'rank'),
    )

    humanhealthprop_id = Column(Integer, primary_key=True, server_default=text("nextval('humanhealthprop_humanhealthprop_id_seq'::regclass)"))
    humanhealth_id = Column(ForeignKey('humanhealth.humanhealth_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    type_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    value = Column(Text)
    rank = Column(Integer, nullable=False, server_default=text("0"))

    humanhealth = relationship('Humanhealth')
    type = relationship('Cvterm')


