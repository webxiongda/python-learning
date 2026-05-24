PYTHON ?= python3
NPM ?= npm

.PHONY: check compile test-backend frontend-check frontend-build refresh-generic enhance-weak fill-missing all dev backend client

check:
	$(PYTHON) tools/check_learning_repo.py

compile:
	$(PYTHON) -m py_compile tools/check_learning_repo.py tools/generate_missing_chapters.py tools/refresh_generic_chapters.py tools/enhance_weak_chapters.py

test-backend:
	$(PYTHON) -m pytest backend/tests/test_workbench_api.py -q

frontend-check:
	$(NPM) run check

frontend-build:
	$(NPM) run build

refresh-generic:
	$(PYTHON) tools/refresh_generic_chapters.py

enhance-weak:
	$(PYTHON) tools/enhance_weak_chapters.py

fill-missing:
	$(PYTHON) tools/generate_missing_chapters.py

backend:
	$(PYTHON) -m uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000

client:
	$(NPM) run client

dev:
	$(NPM) run dev

all: compile check test-backend frontend-check frontend-build
