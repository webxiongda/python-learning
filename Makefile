PYTHON ?= python3

.PHONY: check compile refresh-generic fill-missing all

check:
	$(PYTHON) tools/check_learning_repo.py

compile:
	$(PYTHON) -m py_compile tools/check_learning_repo.py tools/generate_missing_chapters.py tools/refresh_generic_chapters.py

refresh-generic:
	$(PYTHON) tools/refresh_generic_chapters.py

fill-missing:
	$(PYTHON) tools/generate_missing_chapters.py

all: compile check
