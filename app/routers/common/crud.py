from typing import Type

from sqlalchemy.orm import Session

from .models import Country, Industry


def insert_data(db: Session, instance):
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


def get_country(db: Session) -> list[Type[Country]]:
    return db.query(Country).all()


def get_industry(db: Session) -> list[Type[Industry]]:
    return db.query(Industry).all()
