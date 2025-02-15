PY = python3

ifeq ($(OS), Windows_NT)
    PY=python
endif

all: check test lint

check_and_test: FORCE
	mypy azul --strict
	mypy interfaces --strict
	mypy test --strict
	mypy communication --strict
	$(PY) -m unittest 

lint: FORCE
	pylint azul/
	pylint interfaces/
	pylint test/
	pylint communication/

format: FORCE
	autopep8 -i azul/*.py
	autopep8 -i interfaces/*.py
	autopep8 -i test/*.py
	autopep8 -i communication/*.py

test: FORCE
	$(PY) -m unittest

check: FORCE
	mypy azul --strict
	mypy interfaces --strict
	mypy test --strict
	mypy communication --strict

game: FORCE
	@$(PY) -m communication.communication

FORCE: ;
