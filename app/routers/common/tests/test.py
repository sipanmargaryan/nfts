from starlette import status

from app.routers.common.tests.factory import CountryFactory, IndustryFactory


def test_get_countries(client, db):
    CountryFactory.create_batch(3)

    response = client.get("/common/countries")

    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()

    assert "data" in json_data
    assert isinstance(json_data["data"], list)
    assert len(json_data["data"]) == 3

    for item in json_data["data"]:
        assert "name" in item
        assert "code" in item
        assert "dial_code" in item
        assert "id" in item


def test_get_industries(client, db):
    IndustryFactory.create_batch(3)

    response = client.get("/common/industries")

    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()

    assert "data" in json_data
    assert isinstance(json_data["data"], list)
    assert len(json_data["data"]) == 3

    for item in json_data["data"]:
        assert "name" in item
        assert "id" in item