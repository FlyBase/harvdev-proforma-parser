from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class StrainPub(Base):
    __tablename__ = 'strain_pub'
    __table_args__ = (
        UniqueConstraint('strain_id', 'pub_id'),
    )

    strain_pub_id = Column(Integer, primary_key=True, server_default=text("nextval('strain_pub_strain_pub_id_seq'::regclass)"))
    strain_id = Column(ForeignKey('strain.strain_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    pub = relationship('Pub')
    strain = relationship('Strain')


