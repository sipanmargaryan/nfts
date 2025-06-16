import json

from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine
from app.routers.common.models import (  # Adjust import based on your project structure
    Country,
)


def load_countries_from_json(json_path: str):
    with open(json_path, "r", encoding="utf-8") as f:
        countries = json.load(f)
    return countries


def fill_countries():
    countries = load_countries_from_json("app/templates/static/countries.json")
    session = SessionLocal()

    try:
        for c in countries:
            # Check if country already exists to avoid duplicates
            exists = session.query(Country).filter_by(code=c["code"]).first()
            if not exists:
                country = Country(
                    name=c["name"], dial_code=c["dial_code"], code=c["code"]
                )
                session.add(country)
        session.commit()
        print("Countries inserted successfully.")
    except Exception as e:
        session.rollback()
        print("Error inserting countries:", e)
    finally:
        session.close()


if __name__ == "__main__":
    fill_countries()
