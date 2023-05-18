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

run:
	PYTHONPATH=. python app/asgi.py
