from fastapi import APIRouter, Depends, Request, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import AuthenticationFailedError, ValidationError
from app.helpers import messages
from app.helpers.jwt import jwt_decode
from app.helpers.mail import send_mail
from app.helpers.middlewares import is_logged_in_middleware
from app.helpers.response import Response
from app.settings import FRONT_API

from .crud import (
    check_user_reset_password_code,
    create_user,
    get_active_user_by_email,
    get_user_by_auth_code_and_update,
    get_user_by_email,
    update_auth_code,
    update_reset_pass_code,
    update_user_password,
)
from .schemas import (
    AuthCodeValidationSchema,
    ChangePasswordSchema,
    ForgotPasswordSchema,
    ResetPasswordSchema,
    UserLoginSchema,
    UserRegistrationSchema,
)
from .utils import (
    generate_auth_code,
    generate_reset_code,
    generate_tokens,
    get_timedelta_from_hours,
    verify_password,
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("/sign-up")
async def sign_up(user: UserRegistrationSchema, db: Session = Depends(get_db)):
    user_info = get_user_by_email(db, user.email)
    auth_code = generate_auth_code()
    if user_info and user_info.active:
        raise ValidationError(messages.EMAIL_EXISTS)

    if not user_info:
        user = create_user(db, user, auth_code=auth_code)

    if user_info and user_info.auth_code and not user_info.active:
        update_auth_code(db, user.email, auth_code)

    await send_mail(
        messages.EmailSubjects.VERIFICATION_CODE,
        user.email,
        dict(
            auth_code_link=f"{FRONT_API}/sign-up?code={auth_code}",  # issue with query param
        ),
        "verify",
    )
    return Response(message=messages.SUCCESS, status_code=status.HTTP_201_CREATED)


@router.post("/check-user-by-auth-code")
async def validate_auth_code(
    request: AuthCodeValidationSchema, db: Session = Depends(get_db)
):
    user = get_user_by_auth_code_and_update(db, request.code)
    if not user:
        raise ValidationError(messages.INVALID_CODE)

    return Response(
        data=dict(email=user.email),
        message=messages.SUCCESS,
        status_code=status.HTTP_204_NO_CONTENT,
    )


@router.post("/sign-in")
async def sign_up(login: UserLoginSchema, db: Session = Depends(get_db)):
    user = get_active_user_by_email(db, login.email)
    if user is None:
        raise AuthenticationFailedError()
    if not verify_password(login.password, user.password):
        raise AuthenticationFailedError()

    data = generate_tokens(user)

    return Response(data=data, message=messages.SUCCESS, status_code=status.HTTP_200_OK)


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordSchema, db: Session = Depends(get_db)):
    user = get_active_user_by_email(db, request.email)
    if not user:
        raise ValidationError(messages.EMAIL_NOT_EXISTS)

    reset_pass_code = generate_reset_code()
    reset_pass_code_expiration_date = get_timedelta_from_hours(hours=1)

    user = update_reset_pass_code(
        db, user, reset_pass_code, reset_pass_code_expiration_date
    )

    await send_mail(
        messages.EmailSubjects.FORGOT_PASSWORD,
        user.email,
        dict(
            reset_pass_code=f"{reset_pass_code}",
        ),
        "forgot",
    )
    return Response(
        data=dict(email=user.email),
        message=messages.SUCCESS,
        status_code=status.HTTP_200_OK,
    )


@router.patch("/reset-password")
async def reset_password(request: ResetPasswordSchema, db: Session = Depends(get_db)):
    user = check_user_reset_password_code(db, request.code)
    if not user:
        raise ValidationError(messages.INVALID_CODE)

    update_user_password(db, user, request.password)

    return Response(message=messages.SUCCESS, status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/change-password")
async def change_password(request: ChangePasswordSchema,
                         db: Session = Depends(get_db),
                         user=Depends(is_logged_in_middleware())
                         ):
    
    if not verify_password(request.old_password, user.password):
        raise ValidationError(messages.INVALID_PASSWORD)

    update_user_password(db, user, request.password)

    return Response(message=messages.SUCCESS, status_code=status.HTTP_204_NO_CONTENT)
