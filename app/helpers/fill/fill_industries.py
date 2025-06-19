import json

from sqlalchemy.orm import Session

from app.helpers.database import SessionLocal, engine
from app.routers.common.models import Industry


def load_industries_from_json(json_path: str):
    with open(json_path, "r", encoding="utf-8") as f:
        industries = json.load(f)
    return industries


def fill_industries():
    industries = load_industries_from_json("app/templates/static/industries.json")
    session = SessionLocal()

    try:
        for i in industries:
            exists = session.query(Industry).filter_by(name=i["name"]).first()
            if not exists:
                industry = Industry(
                    name=i["name"],
                )
                session.add(industry)
        session.commit()
        print("Industries inserted successfully.")
    except Exception as e:
        session.rollback()
        print("Error inserting industries:", e)
    finally:
        session.close()


if __name__ == "__main__":
    fill_industries()
