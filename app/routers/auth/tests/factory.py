import random
import string
from datetime import datetime, timedelta, timezone

import factory

from app.routers.auth.models import Account
from app.routers.auth.utils import get_password_hash


def random_code(length=6):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


class AccountFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Account
        sqlalchemy_session_persistence = "commit"

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = factory.LazyFunction(lambda: get_password_hash("password123"))
    auth_code = factory.LazyFunction(random_code)
    reset_pass_code = None
    reset_pass_code_expiration_date = factory.LazyFunction(
        lambda: datetime.now(timezone.utc) + timedelta(hours=1)
    )
    active = True
    refresh_token = None
    refresh_token_expiration = factory.LazyFunction(
        lambda: datetime.now(timezone.utc) + timedelta(days=30)
    )
