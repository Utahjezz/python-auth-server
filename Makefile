setup-local-env:
	pip install pip-tools
	@make requirements-dev.txt
	pip install -r requirements-dev.txt
	pre-commit install

requirements-dev.txt: requirements-dev.in
	pip-compile requirements-dev.in --output-file $@

requirements.txt: requirements.in
	pip-compile requirements.in --output-file $@

install:
	pip install -r requirements.txt

bump:
	cz bump

push-tags:
	git push --tags

run-local:
	PYTHONPATH=. env $(cat .env.local) python app/asgi.py

docker-run-local-db:
	@ docker run --rm -it -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=auth postgres:14.2-alpine

run-tests:
	pytest -v --cov

build-docker:
	@ docker build -t auth-backend .

run-docker: build-docker
	@ PORT=5050 docker run --rm -it -p 5050:5050 --env-file .env.local.docker auth-backend

docker-test:
	@ docker build --target test -t auth-backend-tests .

docker-run-tests: docker-test
	@ docker run --rm -it auth-backend-tests
