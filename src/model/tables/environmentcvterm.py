from sqlalchemy import *
from model.base import Base
from sqlalchemy.orm import relationship

metadata = Base.metadata
class EnvironmentCvterm(Base):
    __tablename__ = 'environment_cvterm'
    __table_args__ = (
        UniqueConstraint('environment_id', 'cvterm_id'),
    )

    environment_cvterm_id = Column(Integer, primary_key=True, server_default=text("nextval('environment_cvterm_environment_cvterm_id_seq'::regclass)"))
    environment_id = Column(ForeignKey('environment.environment_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    cvterm_id = Column(ForeignKey('cvterm.cvterm_id', ondelete='CASCADE', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    cvterm = relationship('Cvterm')
    environment = relationship('Environment')


