import factory
from faker import Faker

from factory.alchemy import SQLAlchemyModelFactory
from app.routers.companies.models import CompanyProfile, MintedNFT
from app.routers.auth.tests.factory import AccountFactory
from app.routers.common.tests.factory import CountryFactory, IndustryFactory

faker = Faker()

class CompanyProfileFactory(SQLAlchemyModelFactory):
    class Meta:
        model = CompanyProfile
        sqlalchemy_session_persistence = "commit"

    account = factory.SubFactory(AccountFactory)
    country = factory.SubFactory(CountryFactory)
    industry = factory.SubFactory(IndustryFactory)

    company_name = factory.Faker("company")
    registration_number = factory.Faker("ean13")
    bussines_phone_number = factory.Faker("phone_number")
    verified = factory.Faker("boolean")



class MintedNFTFactory(SQLAlchemyModelFactory):
    class Meta:
        model = MintedNFT
        sqlalchemy_session_persistence = "commit"

    company = factory.SubFactory(CompanyProfileFactory)

    description = factory.Faker("sentence")
    metadata_ipfs_url = factory.Faker("uri")
    token_id = factory.LazyFunction(lambda: faker.uuid4())
    chain = factory.Iterator(["ethereum", "polygon", "arbitrum", "optimism"])
    recipient_address = factory.LazyFunction(lambda: f"0x{faker.hexify(text='^' * 40)}")
    name = factory.Faker("word")
    metadata_json = factory.LazyFunction(lambda: {
        "name": "Sample NFT",
        "description": "A generated NFT for testing.",
        "image": "ipfs://samplehash",
        "attributes": [
            {"trait_type": "Background", "value": "Blue"},
            {"trait_type": "Rarity", "value": "Rare"},
        ]
    })