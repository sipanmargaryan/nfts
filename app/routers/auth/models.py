from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Integer, String, event
from sqlalchemy.orm import relationship
from app.helpers.database import BaseDBModel

class Account(BaseDBModel):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    reset_pass_code = Column(String, unique=True, nullable=True)
    auth_code = Column(String, unique=True, nullable=True)
    active = Column(Boolean, default=False)
    reset_pass_code_expiration_date = Column(DateTime, nullable=True)
    refresh_token = Column(String, unique=True, nullable=True)
    refresh_token_expiration = Column(DateTime, nullable=True)

    user_profile = relationship("UserProfile", back_populates="account", uselist=False)


@event.listens_for(Account, "before_update")
def receive_before_update(mapper, connection, target):
    target.updated_at = datetime.now(timezone.utc)
