from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    event,
)
from sqlalchemy.orm import relationship

from app.helpers.database import BaseDBModel


class CompanyProfile(BaseDBModel):
    __tablename__ = "company_profiles"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    industry_id = Column(Integer, ForeignKey("industries.id"), nullable=False)
    company_name = Column(String, nullable=False)
    registration_number = Column(String, nullable=True)
    bussines_phone_number = Column(String, nullable=True)
    verified = Column(Boolean, default=False)

    account = relationship("Account", backref="company_profiles")
    industry = relationship("Industry", backref="companies")
    country = relationship("Country")
    minted_nfts = relationship("MintedNFT", back_populates="company")

    __table_args__ = (
        UniqueConstraint("account_id", "company_name", name="uq_account_company"),
    )


class MintedNFT(BaseDBModel):
    __tablename__ = "minted_nfts"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company_profiles.id"), nullable=False)

    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    metadata_ipfs_url = Column(String, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    token_id = Column(String, nullable=True)
    chain = Column(String, nullable=True)
    recipient_address = Column(String, nullable=True)

    company = relationship("CompanyProfile", back_populates="minted_nfts")


@event.listens_for(CompanyProfile, "before_update")
@event.listens_for(MintedNFT, "before_update")
def receive_before_update(mapper, connection, target):
    target.updated_at = datetime.now(timezone.utc)
