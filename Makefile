format:
	poetry run black .
	poetry run isort .

analyze:
	poetry run mypy
	poetry run pylint --jobs 0 src/real_estate_scrapers tests

test:
	export PYTHONPATH=src
	poetry run pytest
