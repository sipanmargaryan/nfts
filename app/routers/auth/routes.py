from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.helpers.database import get_db
from app.helpers.exceptions import AuthenticationFailedError, ValidationError
from app.helpers import messages
from app.helpers.mail import send_mail
from app.helpers.middlewares import is_logged_in_middleware
from app.helpers.response import Response
from app.helpers.oauth import get_user_info_from_provider
from app.settings import FRONT_API

from .crud import (
    check_user_reset_password_code,
    create_user,
    get_active_user_by_email,
    get_user_by_auth_code_and_update,
    get_user_by_email,
    get_active_user_by_refresh_token,
    update_auth_code,
    update_reset_pass_code,
    update_user_password,
    update_refresh_token,
)
from .schemas import (
    AuthCodeValidationSchema,
    ChangePasswordSchema,
    ForgotPasswordSchema,
    ResetPasswordSchema,
    UserLoginSchema,
    UserRegistrationSchema,
    RefreshTokenSchema,
    UserSchema,
    SocialSignUpSchema,
    SocialSignInSchema,
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


@router.post("/activate-user-by-auth-code")
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
async def sign_in(login: UserLoginSchema, db: Session = Depends(get_db)):
    user = get_active_user_by_email(db, login.email)
    if user is None:
        raise AuthenticationFailedError()
    if not verify_password(login.password, user.password):
        raise AuthenticationFailedError()

    data = generate_tokens(user)
    update_refresh_token(db, user, data["refresh_token"])

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


@router.patch("/refresh-token")
async def refresh_token(request: RefreshTokenSchema, db: Session = Depends(get_db)):
    user = get_active_user_by_refresh_token(db, request.refresh_token)
    if not user:
        raise ValidationError(messages.INVALID_CODE)

    data = generate_tokens(user, request.refresh_token)

    return Response(
        data=data, message=messages.SUCCESS, status_code=status.HTTP_204_NO_CONTENT
    )


@router.patch("/sign-out")
async def sign_out(db: Session = Depends(get_db), user=Depends(is_logged_in_middleware())):
    update_refresh_token(db, user, None, False)
    return Response(message=messages.SUCCESS, status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me")
async def me(user_info=Depends(is_logged_in_middleware())):
    user_info = UserSchema(
        id=user_info.id,
        email=user_info.email,
        first_name=user_info.user_profile.first_name,
        last_name=user_info.user_profile.last_name,
    ).model_dump()
    return Response(data=user_info, message=messages.SUCCESS, code=status.HTTP_200_OK)



@router.post("/oauth/sign-up")
async def social_sign_up(request: SocialSignUpSchema, db: Session = Depends(get_db)):
    info = await get_user_info_from_provider(
        request.provider,
        request.code,
    )
    if get_active_user_by_email(db, info["email"]):
        raise ValidationError(messages.EMAIL_EXISTS)
    if get_user_by_email(db, info["email"]):
        return Response(data=info, message=messages.SUCCESS, code=status.HTTP_200_OK)
    create_user(
        db,
        email=info["email"],
        first_name=info["first_name"],
        last_name=info["last_name"],
        country_id=request.country_id,
    )
    return Response(data=info, message=messages.SUCCESS, code=status.HTTP_200_OK)


@router.post("/oauth/sign-in")
async def social_sign_in(request: SocialSignInSchema, db: Session = Depends(get_db)):
    info = await get_user_info_from_provider(
        request.provider,
        request.code,
    )
    user = get_active_user_by_email(info["email"], db)
    if user:
        data = generate_tokens(user)
        return Response(data=data, message=messages.SUCCESS, code=status.HTTP_200_OK)
    raise AuthenticationFailedError()