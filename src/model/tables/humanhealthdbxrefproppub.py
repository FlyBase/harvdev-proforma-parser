from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class HumanhealthDbxrefpropPub(Base):
    __tablename__ = 'humanhealth_dbxrefprop_pub'
    __table_args__ = (
        UniqueConstraint('humanhealth_dbxrefprop_id', 'pub_id'),
    )

    humanhealth_dbxrefprop_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('humanhealth_dbxrefprop_pub_humanhealth_dbxrefprop_pub_id_seq'::regclass)"))
    humanhealth_dbxrefprop_id = Column(ForeignKey('humanhealth_dbxrefprop.humanhealth_dbxrefprop_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    humanhealth_dbxrefprop = relationship('HumanhealthDbxrefprop')
    pub = relationship('Pub')


