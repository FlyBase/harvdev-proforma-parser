from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class HumanhealthPub(Base):
    __tablename__ = 'humanhealth_pub'
    __table_args__ = (
        UniqueConstraint('humanhealth_id', 'pub_id'),
    )

    humanhealth_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('humanhealth_pub_humanhealth_pub_id_seq'::regclass)"))
    humanhealth_id = Column(ForeignKey('humanhealth.humanhealth_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    humanhealth = relationship('Humanhealth')
    pub = relationship('Pub')


