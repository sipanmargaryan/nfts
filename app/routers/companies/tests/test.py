from fastapi import status

from app.routers.common.tests.factory import CountryFactory, IndustryFactory
from app.routers.users.tests.factory import UserProfileFactory
from app.routers.auth.tests.factory import AccountFactory
from .factory import CompanyProfileFactory, MintedNFTFactory
from app.helpers import messages
from app.routers.companies.schemas import CompanyCreateSchema, MintedNFTUpdateToken


def test_create_company_success(client, db, auth_headers):
    user = AccountFactory()
    UserProfileFactory(account=user)
    country = CountryFactory()
    industry = IndustryFactory()

    payload = CompanyCreateSchema(
        industry_id=industry.id,
        country_id=country.id,
        company_name="Test Company",
        registration_number="",
        bussines_phone_number=""
    ).model_dump()


    response = client.post(
        "/company/create-company",
        headers=auth_headers(user),
        json=payload
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["message"] == messages.SUCCESS

    assert "company_name" in response.json()["data"]
    assert "id" in response.json()["data"]


def test_create_company_invalid_name(client, db, auth_headers):
    company_name = "Test Company"
    user = AccountFactory()
    UserProfileFactory(account=user)
    country = CountryFactory()
    industry = IndustryFactory()
    CompanyProfileFactory(account=user, country=country, industry=industry, company_name=company_name)

    payload = CompanyCreateSchema(
        industry_id=industry.id,
        country_id=country.id,
        company_name=company_name,
        registration_number="",
        bussines_phone_number=""
    ).model_dump()


    response = client.post(
        "/company/create-company",
        headers=auth_headers(user),
        json=payload
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"]["message"] == messages.COMPANY_EXISTS


def test_update_minted_nft_token_info_success(client, db, auth_headers):
    user = AccountFactory()
    UserProfileFactory(account=user)
    company = CompanyProfileFactory(account=user)
    nft = MintedNFTFactory(company=company)

    update_data = MintedNFTUpdateToken(
        company_id=company.id,
        token_id="0x123abc456",
        recipient_address="0xAbC123456789000"
    ).model_dump()

    response = client.put(
        f"/company/minted-nfts/{nft.id}",
        headers=auth_headers(user),
        json=update_data
    )

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["data"]
    assert response_data["id"] == nft.id
    assert response_data["token_id"] == update_data["token_id"]
    assert response_data["recipient_address"] == update_data["recipient_address"]


def test_update_minted_nft_token_invalid_company(client, db, auth_headers):
    user = AccountFactory()
    UserProfileFactory(account=user)
    company = CompanyProfileFactory(account=user)
    nft = MintedNFTFactory(company=company)

    update_data = MintedNFTUpdateToken(
        company_id=company.id + 100,
        token_id="0x123abc456",
        recipient_address="0xAbC123456789000"
    ).model_dump()

    response = client.put(
        f"/company/minted-nfts/{nft.id}",
        headers=auth_headers(user),
        json=update_data
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_minted_nft_token_invalid_nft(client, db, auth_headers):
    user = AccountFactory()
    UserProfileFactory(account=user)
    company = CompanyProfileFactory(account=user)
    nft = MintedNFTFactory(company=company)

    update_data = MintedNFTUpdateToken(
        company_id=company.id,
        token_id="0x123abc456",
        recipient_address="0xAbC123456789000"
    ).model_dump()

    response = client.put(
        f"/company/minted-nfts/{nft.id + 100}",
        headers=auth_headers(user),
        json=update_data
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND