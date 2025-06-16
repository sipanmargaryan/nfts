from pydantic import BaseModel


class CountrySchema(BaseModel):
    name: str
    dial_code: str
    code: str
    id: int


class CountryListSchema(BaseModel):
    data: list[CountrySchema]
