import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.helpers.database import Base, get_db
from app.helpers.jwt import create_access_token
from app.main import app
from app.routers.auth.tests.factory import AccountFactory
from app.routers.auth.utils import get_token_payload
from app.routers.common.tests.factory import CountryFactory, IndustryFactory
from app.routers.users.tests.factory import UserProfileFactory
from app.routers.companies.tests.factory import CompanyProfileFactory, MintedNFTFactory

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_TEST_NAME")

TEST_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class CoreClient(TestClient):
    def request(self, method, url, *args, **kwargs):
        url = f"/api/v1{url}" if not url.startswith("/api/v1") else url
        return super().request(method, url, *args, **kwargs)


@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    # Create tables before tests
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables after tests
    Base.metadata.drop_all(bind=engine)


# Be aware add new factories here to auto commit and session local declaration
@pytest.fixture(autouse=True)
def set_factory_session(db):
    CountryFactory._meta.sqlalchemy_session = db
    AccountFactory._meta.sqlalchemy_session = db
    UserProfileFactory._meta.sqlalchemy_session = db
    IndustryFactory._meta.sqlalchemy_session = db
    CompanyProfileFactory._meta.sqlalchemy_session = db
    MintedNFTFactory._meta.sqlalchemy_session = db


@pytest.fixture(scope="function")
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield CoreClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    def _auth_headers(user):
        access_token = create_access_token(get_token_payload(user))
        return {"Authorization": f"Bearer {access_token}"}
    return _auth_headers