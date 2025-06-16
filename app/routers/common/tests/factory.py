import random

import factory

from app.routers.common.models import Country


class CountryFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Country
        sqlalchemy_session_persistence = "commit"

    code = factory.Faker("country_code")
    dial_code = factory.LazyAttribute(lambda _: f"+{random.randint(1, 999)}")
    name = factory.Faker("country")
