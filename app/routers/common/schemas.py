from pydantic import BaseModel


class CountrySchema(BaseModel):
    name: str
    dial_code: str
    code: str
    id: int


class IndustrySchema(BaseModel):
    id: int
    name: str


class CountryListSchema(BaseModel):
    data: list[CountrySchema]


class IndustryListSchema(BaseModel):
    data: list[IndustrySchema]
