from sqlalchemy.orm import Session

from app.routers.common.crud import insert_data

from .models import CompanyProfile, MintedNFT
from .schemas import CompanyCreateSchema, MintedNFTCreate


def get_company_by_name(db: Session, name: str, user_id: int) -> CompanyProfile | None:
    company = (
        db.query(CompanyProfile)
        .filter(
            CompanyProfile.account_id == user_id,
            CompanyProfile.company_name == name,
        )
        .first()
    )

    return company


def create_new_company(
    db: Session, user_id: int, company: CompanyCreateSchema
) -> CompanyProfile:
    company_profile = CompanyProfile(
        account_id=user_id,
        country_id=company.country_id,
        industry_id=company.industry_id,
        company_name=company.company_name,
        registration_number=company.registration_number,
        bussines_phone_number=company.bussines_phone_number,
    )

    return insert_data(db, company_profile)


def save_nft(db: Session, nft_data: MintedNFTCreate) -> MintedNFT:
    nft = MintedNFT(**nft_data.model_dump(exclude_none=True))
    return insert_data(db, nft)


def user_owns_company(
    db: Session, user_id: int, company_id: int
) -> CompanyProfile | None:
    company = (
        db.query(CompanyProfile)
        .filter(
            CompanyProfile.account_id == user_id,
            CompanyProfile.id == company_id,
        )
        .first()
    )

    return company


def update_token_info(
    db: Session, nft_id: int, company_id: int, token_id: str, recipient_address: str
):
    nft = (
        db.query(MintedNFT)
        .filter(MintedNFT.id == nft_id, MintedNFT.company_id == company_id)
        .first()
    )

    if not nft:
        return None

    nft.token_id = token_id
    nft.recipient_address = recipient_address

    return insert_data(db, nft)
