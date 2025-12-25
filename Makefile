.PHONY: install test

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

test:
	@echo "No tests configured yet."
