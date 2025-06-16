from fastapi import status

from app.helpers import messages
from app.routers.auth.schemas import (
    AuthCodeValidationSchema,
    ChangePasswordSchema,
    ForgotPasswordSchema,
    ResetPasswordSchema,
    UserLoginSchema,
    UserRegistrationSchema,
)
from app.routers.auth.utils import get_password_hash
from app.routers.common.tests.factory import CountryFactory
from app.routers.users.tests.factory import UserProfileFactory

from .factory import AccountFactory


def test_sign_up_new_user(client, db):
    country = CountryFactory()
    user_data = UserRegistrationSchema(
        email="newuser@example.com",
        password="newpassword123",
        first_name="New",
        last_name="User",
        country_id=country.id,
    ).model_dump()
    response = client.post("/auth/sign-up", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert "success" in response.json()["message"].lower()


def test_sign_up_existing_active_user(client, db):
    country = CountryFactory()
    existing_user = AccountFactory(active=True)

    user_data = UserRegistrationSchema(
        email=existing_user.email,
        password="password123",
        first_name="John",
        last_name="Doe",
        country_id=country.id,
    ).model_dump()
    response = client.post("/auth/sign-up", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert messages.EMAIL_EXISTS == response.json()["detail"]["message"]


def test_validate_auth_code_success(client, db):
    account = AccountFactory(auth_code="testcode123", active=False)

    payload = AuthCodeValidationSchema(code="testcode123").model_dump()

    response = client.post("/auth/check-user-by-auth-code", json=payload)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.json()["data"]["email"] == account.email
    assert messages.SUCCESS == response.json()["message"]


def test_validate_auth_code_invalid(client, db):
    payload = AuthCodeValidationSchema(code="wrongcode").model_dump()

    response = client.post("/auth/check-user-by-auth-code", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert messages.INVALID_CODE == response.json()["detail"]["message"]


def test_sign_in_valid_credentials(client, db):
    user = AccountFactory()
    UserProfileFactory(account=user)

    login_data = UserLoginSchema(
        email=user.email,
        password="password123",
    ).model_dump()
    response = client.post("/auth/sign-in", json=login_data)
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()["data"]


def test_sign_in_invalid_password(client, db):
    user = AccountFactory()
    UserProfileFactory(account=user)

    login_data = UserLoginSchema(
        email=user.email,
        password="wrongpassword",
    ).model_dump()
    response = client.post("/auth/sign-in", json=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_sign_in_unknown_email(client, db):
    login_data = UserLoginSchema(
        email="doesnotexist@example.com",
        password="any",
    ).model_dump()
    response = client.post("/auth/sign-in", json=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_forgot_password_success(client, db, mocker):
    user = AccountFactory(active=True)

    mocker.patch("app.routers.auth.routes.send_mail", return_value=None)

    data = ForgotPasswordSchema(email=user.email).model_dump()

    response = client.post("/auth/forgot-password", json=data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["email"] == user.email


def test_forgot_password_invalid_email(client, db):

    data = {"email": "notexist@example.com"}

    response = client.post("/auth/forgot-password", json=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"]["message"] == messages.EMAIL_NOT_EXISTS


def test_reset_password_success(client, db):
    reset_pass_code = "reset_code"
    user = AccountFactory(reset_pass_code=reset_pass_code)

    new_password = "NewSecurePassword123"

    reset_data = ResetPasswordSchema(
        code=reset_pass_code, password=new_password
    ).model_dump()

    response = client.patch("/auth/reset-password", json=reset_data)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert user.password != get_password_hash("oldpassword")
    assert (
        user.reset_pass_code is None
        or user.password != get_password_hash(new_password) is False
    )


def test_reset_password_invalid_code(client):

    reset_data = ResetPasswordSchema(
        code="invalid_code", password="password"
    ).model_dump()

    response = client.patch("/auth/reset-password", json=reset_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_change_password_success(client, db, auth_headers):
    old_password = "oldpass123"
    new_password = "newpass456"
    user = AccountFactory(password=get_password_hash(old_password))
    UserProfileFactory(account=user)

    data = ChangePasswordSchema(
        old_password=old_password,
        password=new_password
    ).model_dump()

    response = client.patch(
        "/auth/change-password",
        headers=auth_headers(user),
        json=data
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_password_invalid_old_password(client, db, auth_headers):
    user = AccountFactory(password=get_password_hash("correct-password"))
    UserProfileFactory(account=user)


    data = ChangePasswordSchema(
        old_password="wrong-password",
        password="new-password123"
    ).model_dump()

    response = client.patch(
        "/auth/change-password",
        headers=auth_headers(user),
        json=data
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"]["message"] == messages.INVALID_PASSWORD