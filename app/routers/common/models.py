from sqlalchemy import Column, Integer, String

from app.helpers.database import BaseDBModel


class Country(BaseDBModel):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True)
    code = Column(String(3), unique=True)
    dial_code = Column(String(5))
    name = Column(String, unique=True)


class Industry(BaseDBModel):
    __tablename__ = "industries"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
