PYTHON	=	python3
PIP		=	pip
SRC		=	a_maze_ing.py config.txt

.PHONY: install run debug clean lint lint-strict

install:
		$(PIP) install -r requirements.txt

run:
		$(PYTHON) $(SRC)

debug:
		$(PYTHON) -m pdb $(SRC)

clean:
		rm -rf __pycache__
		rm -rf .mypy_cache
		rm -rf .pytest_cache
		find . -type d -name "__pycache__" -exec rm -rf {} +

lint:
		flake8 .
		mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
		flake8 .
		mypy . --strict