from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class GrpCvterm(Base):
    __tablename__ = 'grp_cvterm'
    __table_args__ = (
        UniqueConstraint('cvterm_id', 'grp_id', 'pub_id'),
    )

    grp_cvterm_id = Column(Integer, primary_key=True, server_default=text("nextval('grp_cvterm_grp_cvterm_id_seq'::regclass)"))
    is_not = Column(Boolean, nullable=False, server_default=text("false"))
    cvterm_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    grp_id = Column(ForeignKey('grp.grp_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    pub_id = Column(ForeignKey('pub.pub_id', ondelete='CASCADE', onupdate='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    cvterm = relationship('Cvterm')
    grp = relationship('Grp')
    pub = relationship('Pub')


