import enum

from pydantic import BaseModel, ConfigDict, WrapValidator, validate_email
from pydantic_core import PydanticCustomError
from typing_extensions import Annotated

from app.helpers.exceptions import AuthenticationFailedError, ValidationError
from app.helpers.messages import INVALID_EMAIL, INVALID_PASSWORD


def validate_email_format(error_class):
    def wrapper(value, handler):
        """CUSTOM FUNCTION TO VALIDATE EMAIL FORMAT
        Raises ValidationError if email is not valid for EmailString
        Raises AuthenticationFailedError if email is not valid for LoginEmailString
        """
        try:
            validate_email(value)
        except PydanticCustomError:
            raise error_class
        return value.lower()

    return wrapper


EmailString = Annotated[
    str, WrapValidator(validate_email_format(ValidationError(INVALID_EMAIL)))
]
LoginEmailString = Annotated[
    str, WrapValidator(validate_email_format(AuthenticationFailedError))
]


class UserSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailString


class UserRegistrationSchema(BaseModel):
    email: EmailString
    password: str
    first_name: str
    last_name: str
    country_id: int

    model_config = ConfigDict(from_attributes=True)


class UserLoginSchema(BaseModel):
    email: LoginEmailString
    password: str


class AuthCodeValidationSchema(BaseModel):
    code: str


class ForgotPasswordSchema(BaseModel):
    email: EmailString


class ResetPasswordSchema(BaseModel):
    password: str
    code: str


class ChangePasswordSchema(BaseModel):
    old_password: str
    password: str


class UserTokenPayload(BaseModel):
    user_id: int
    email: EmailString
    first_name: str
    last_name: str


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class ProviderEnum(enum.Enum):
    GOOGLE = "google"


class SocialSignUpSchema(BaseModel):
    code: str
    provider: ProviderEnum
    country_id: int


class SocialSignInSchema(BaseModel):
    code: str
    provider: ProviderEnum