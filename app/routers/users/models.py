from datetime import datetime, timezone

from sqlalchemy import Column, ForeignKey, Integer, String, event
from sqlalchemy.orm import relationship

from app.helpers.database import BaseDBModel


class UserProfile(BaseDBModel):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), unique=True)
    country_id = Column(Integer, ForeignKey("countries.id"))
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)

    account = relationship("Account", back_populates="user_profile", uselist=False)
    country = relationship("Country")


@event.listens_for(UserProfile, "before_update")
def receive_before_update(mapper, connection, target):
    target.updated_at = datetime.now(timezone.utc)
