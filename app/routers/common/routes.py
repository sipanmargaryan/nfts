from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.helpers.database import get_db
from app.helpers import messages
from app.helpers.response import Response

from .crud import get_country, get_industry
from .schemas import CountryListSchema, IndustryListSchema

router = APIRouter(
    prefix="/common",
    tags=["common"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get("/countries")
async def country(db: Session = Depends(get_db)):
    country_list = get_country(db)
    countries = CountryListSchema(data=jsonable_encoder(country_list)).model_dump()
    return Response(
        data=countries["data"], message=messages.SUCCESS, code=status.HTTP_200_OK
    )


@router.get("/industries")
async def industry(db: Session = Depends(get_db)):
    industry_list = get_industry(db)
    industries = IndustryListSchema(data=jsonable_encoder(industry_list)).model_dump()
    return Response(
        data=industries["data"], message=messages.SUCCESS, code=status.HTTP_200_OK
    )
