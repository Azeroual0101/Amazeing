# Makefile for A-Maze-ing project

PYTHON = python3
PIP = pip
MAIN = a_maze_ing.py
CONFIG = config.txt

.PHONY: all install run debug clean lint build

all: install

install:
	$(PIP) install -e .

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	rm -rf build/ dist/ *.egg-info .mypy_cache .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

build:
	$(PYTHON) -m build