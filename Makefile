activate_venv=.venv/bin/activate

.PHONY: .venv
.venv:
	@if command -v pyenv; then pyenv install --skip-existing; fi
	@python3 -m venv .venv
	. $(activate_venv); pip3 install -r requirements-dev.txt
	. $(activate_venv); pip3 install -r requirements-lambda.txt

.PHONY: clean
clean:
	@rm -Rf .venv/

.PHONY: unit
unit: .venv
	. $(activate_venv); coverage run -m pytest -v -p no:cacheprovider tests/$(TEST_FOLDER) && coverage report --omit="*/test*"


.PHONY: pretty
pretty: .venv
	. $(activate_venv); isort --profile black ./src
	. $(activate_venv); isort --profile black ./tests
	. $(activate_venv); black ./src --line-length 120
	. $(activate_venv); black ./tests --line-length 120

.PHONY: lint
lint: .venv
	. $(activate_venv); flake8 . --count --select=E9,F63,F7,F82,F401 --show-source --statistics --max-complexity=10 --max-line-length=120 --exclude .venv,packages
