from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.helpers import messages
from app.helpers.response import Response

from .crud import get_country
from .schemas import CountryListSchema

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
