from datetime import datetime, timezone

from app.settings import JWT_REFRESH_TOKEN_EXPIRE_DAYS
from sqlalchemy.orm import Session

from app.routers.users.models import UserProfile
from app.routers.common.crud import insert_data

from .models import Account
from .schemas import UserRegistrationSchema
from .utils import get_password_hash, get_timedelta_from_hours



def get_user_by_email(db: Session, email: str) -> Account | None:
    return db.query(Account).filter_by(email=email).first()


def get_active_user_by_id(db: Session, user_id: int) -> Account | None:
    return db.query(Account).filter_by(id=user_id, active=True).first()


def get_active_user_by_refresh_token(db: Session, refresh_token: str) -> Account | None:
    current_datetime = datetime.now(timezone.utc)
    return db.query(Account).filter(
            Account.refresh_token == refresh_token,
            Account.refresh_token_expiration > current_datetime,
            Account.active == True,
        ).first()


def get_active_user_by_email(db: Session, email: str) -> Account | None:
    return db.query(Account).filter_by(email=email, active=True).first()


def create_user(
    db: Session, user_data: UserRegistrationSchema, auth_code: str
) -> Account:
    hashed_password = get_password_hash(user_data.password)

    new_account = Account(
        email=user_data.email,
        password=hashed_password,
        auth_code=auth_code,
        active=False,
    )
    db.add(new_account)
    db.flush()

    user_profile = UserProfile(
        account_id=new_account.id,
        country_id=user_data.country_id,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
    )

    insert_data(db, user_profile)
    return new_account


def update_auth_code(db: Session, email: str, code: str) -> Account:
    user = db.query(Account).filter_by(email=email).first()
    if user:
        user.auth_code = code

    return insert_data(db, user)


def get_user_by_auth_code_and_update(db: Session, auth_code: str) -> Account | None:
    user = db.query(Account).filter_by(auth_code=auth_code).first()
    if not user:
        return None

    user.active = True
    user.auth_code = None
    return insert_data(db, user)


def update_reset_pass_code(
    db: Session, user: Account, code: str, reset_pass_code_expiration_date: datetime
) -> Account:
    user.reset_pass_code = code
    user.reset_pass_code_expiration_date = reset_pass_code_expiration_date
    return insert_data(db, user)


def check_user_reset_password_code(db: Session, code: str) -> Account | None:
    current_datetime = datetime.now(timezone.utc)
    user = (
        db.query(Account)
        .filter(
            Account.reset_pass_code == code,
            Account.reset_pass_code_expiration_date > current_datetime,
            Account.active == True,
        )
        .first()
    )

    return user


def update_user_password(
    db: Session,
    user: Account,
    password: str,
) -> Account:

    user.password = get_password_hash(password)
    user.reset_pass_code_expiration_date = None
    user.reset_pass_code = None

    return insert_data(db, user)


def update_refresh_token(
    db: Session,
    user: Account,
    refresh_token: str,
    set_expiration = True
) -> Account:
    expiration_date = None
    if set_expiration:
        expiration_date = get_timedelta_from_hours(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    user.refresh_token = refresh_token
    user.refresh_token_expiration = expiration_date

    return insert_data(db, user)