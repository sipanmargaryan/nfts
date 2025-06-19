from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class CompanyCreateSchema(BaseModel):
    country_id: int
    industry_id: int
    company_name: str = Field(..., min_length=1)
    registration_number: str | None
    bussines_phone_number: str | None


class CompanyProfileResponse(BaseModel):
    id: int
    company_name: str
    registration_number: str | None
    bussines_phone_number: str | None
    verified: bool
    country_id: int
    industry_id: int

    model_config = ConfigDict(from_attributes=True)


class MintedNFTCreate(BaseModel):
    company_id: int
    name: str
    description: Optional[str]
    metadata_ipfs_url: str
    metadata_json: Optional[Any]
    chain: str


class MintedNFTUpdateToken(BaseModel):
    token_id: Optional[str]
    recipient_address: Optional[str]
    company_id: int


class MintedNFTOut(BaseModel):
    id: int
    company_id: int
    name: str
    description: Optional[str]
    metadata_ipfs_url: str
    token_id: Optional[str]
    chain: Optional[str]
    recipient_address: str

    model_config = ConfigDict(from_attributes=True)
