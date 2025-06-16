from typing import Type

from sqlalchemy.orm import Session

from .models import Country


def get_country(db: Session) -> list[Type[Country]]:
    return db.query(Country).all()
