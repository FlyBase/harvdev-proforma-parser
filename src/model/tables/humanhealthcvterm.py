from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class HumanhealthCvterm(Base):
    __tablename__ = 'humanhealth_cvterm'
    __table_args__ = (
        UniqueConstraint('humanhealth_id', 'cvterm_id', 'pub_id'),
    )

    humanhealth_cvterm_id = Column(Integer, primary_key=True, server_default=text("nextval('humanhealth_cvterm_humanhealth_cvterm_id_seq'::regclass)"))
    humanhealth_id = Column(ForeignKey('humanhealth.humanhealth_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    cvterm_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False)

    cvterm = relationship('Cvterm')
    humanhealth = relationship('Humanhealth')
    pub = relationship('Pub')


