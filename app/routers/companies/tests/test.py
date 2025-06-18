from fastapi import status

from app.routers.common.tests.factory import CountryFactory, IndustryFactory
from app.routers.users.tests.factory import UserProfileFactory
from app.routers.auth.tests.factory import AccountFactory
from .factory import CompanyProfileFactory
from app.helpers import messages
from app.routers.companies.schemas import CompanyCreateSchema


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