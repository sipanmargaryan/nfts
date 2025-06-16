from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, event
from sqlalchemy.orm import relationship

from app.core.database import BaseDBModel
from app.routers.common.models import Country


class CompanyProfile(BaseDBModel):
    __tablename__ = "company_profiles"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=True)
    company_name = Column(String, nullable=False)
    industry = Column(String)
    registration_number = Column(String, nullable=True)
    country = Column(String, nullable=True)
    bussines_phone_number = Column(String, nullable=True)
    verified = Column(Boolean, default=False)

    account = relationship("Account", back_populates="company_profiles")
    country = relationship(Country)


@event.listens_for(CompanyProfile, "before_update")
def receive_before_update(mapper, connection, target):
    target.updated_at = datetime.now(timezone.utc)
