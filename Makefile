activate_venv=.venv/bin/activate

.venv:
	@if command -v pyenv; then pyenv install --skip-existing; fi
	@python3 -m venv .venv
	. $(activate_venv); pip3 install -r requirements-dev.txt
	. $(activate_venv); pip3 install -r requirements-lambda.txt


.PHONY: clean
clean:
	@rm -Rf .venv/
	@rm -Rf dependencies
	@rm -Rf *.zip
	@rm -Rf .pytest_cache
	@rm -Rf .coverage


.PHONY: unit
unit: .venv
	. $(activate_venv); coverage run -m pytest -v -p no:cacheprovider tests/$(TEST_FOLDER) && coverage report --omit="*/test*"


.PHONY: pretty
pretty: .venv
	. $(activate_venv); isort --profile black ./src
	. $(activate_venv); isort --profile black ./tests
	. $(activate_venv); black ./src --line-length 100
	. $(activate_venv); black ./tests --line-length 100


.PHONY: lint
lint: .venv
	. $(activate_venv); flake8 . --count --show-source --statistics --max-complexity=13 --max-line-length=120 --exclude .venv,dependencies
