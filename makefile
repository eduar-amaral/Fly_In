PYTHON := python3
VENV := .venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip

MAIN := main.py
PROJECT_DIRS := algorithms graph models parser pathfinding simulation ui

MYPY_FLAGS := \
	--warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

.PHONY: help install run debug lint clean fclean

help:
	@echo "Available commands:"
	@echo "  make install  - Create virtual environment and install dependencies"
	@echo "  make run      - Run the project"
	@echo "  make debug    - Run the project with pdb"
	@echo "  make lint     - Run flake8 and mypy"
	@echo "  make clean    - Remove Python cache files"
	@echo "  make fclean   - Remove cache files and virtual environment"

install:
	$(PYTHON) -m venv $(VENV)
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt

run:
	@if [ ! -x "$(VENV_PYTHON)" ]; then \
		echo "Virtual environment not found."; \
		echo "Run 'make install' first."; \
		exit 1; \
	fi
	$(VENV_PYTHON) $(MAIN)

debug:
	@if [ ! -x "$(VENV_PYTHON)" ]; then \
		echo "Virtual environment not found."; \
		echo "Run 'make install' first."; \
		exit 1; \
	fi
	$(VENV_PYTHON) -m pdb $(MAIN)

lint:
	@if [ ! -x "$(VENV_PYTHON)" ]; then \
		echo "Virtual environment not found."; \
		echo "Run 'make install' first."; \
		exit 1; \
	fi
	$(VENV_PYTHON) -m flake8 $(PROJECT_DIRS)
	$(VENV_PYTHON) -m mypy $(PROJECT_DIRS) $(MYPY_FLAGS)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

fclean: clean
	rm -rf $(VENV)