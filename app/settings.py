import os

from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENV", "dev")

# Database
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Auth
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS"))
FRONT_API = os.getenv("FRONT_API")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URL = os.getenv("REDIRECT_URL")


# Email
class EmailEnv:
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM = os.getenv("MAIL_FROM")
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_STARTTLS = False if ENV == "local" else True
    MAIL_SSL_TLS = False
    USE_CREDENTIAL = False if ENV == "local" else True


# Pinata
PINATA_JWT = os.getenv("PINATA_JWT")
