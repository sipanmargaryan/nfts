import factory

from app.routers.auth.tests.factory import AccountFactory
from app.routers.common.tests.factory import CountryFactory
from app.routers.users.models import UserProfile


class UserProfileFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = UserProfile
        sqlalchemy_session_persistence = "commit"

    account = factory.SubFactory(AccountFactory)
    country = factory.SubFactory(CountryFactory)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
