RUN=docker-compose run --rm nft
all:
	docker-compose build

run:
	docker-compose up

ms:
	$(RUN) alembic revision --autogenerate

migrate:
	$(RUN) alembic upgrade head

shell:
	$(RUN) /bin/bash

fmt:
	$(RUN) poetry run black .
	$(RUN) poetry run isort . --profile black

lint:
	$(RUN) poetry run black . --check
	$(RUN) poetry run isort . -c --profile black

test:
	$(RUN) poetry run pytest -x -vvv --pdb

report:
	$(RUN) poetry run pytest -x --pdb

report-fail:
	$(RUN) poetry run pytest --cov-report term --cov-fail-under=90

fill-countries:
	docker-compose run --rm nft python3 -m app.helpers.fill.fill_countries

fill-industries:
	docker-compose run --rm nft python3 -m app.helpers.fill.fill_industries