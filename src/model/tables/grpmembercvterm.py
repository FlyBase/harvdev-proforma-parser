from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class GrpmemberCvterm(Base):
    __tablename__ = 'grpmember_cvterm'
    __table_args__ = (
        UniqueConstraint('cvterm_id', 'grpmember_id', 'pub_id'),
    )

    grpmember_cvterm_id = Column(Integer, primary_key=True, server_default=text("nextval('grpmember_cvterm_grpmember_cvterm_id_seq'::regclass)"))
    is_not = Column(Boolean, nullable=False, server_default=text("false"))
    cvterm_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    grpmember_id = Column(ForeignKey('grpmember.grpmember_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    cvterm = relationship('Cvterm')
    grpmember = relationship('Grpmember')
    pub = relationship('Pub')


