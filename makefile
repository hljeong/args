.PHONY: install test clean

install:
	python -m pip install -r requirements.txt

test:
	python -m pytest -vx --cov=args --cov-report html

clean:
	rm -rf .coverage .pytest_cache htmlcov
	python -Bc "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]" # delete .pyc and .pyo files
	python -Bc "import pathlib; [p.rmdir() for p in pathlib.Path('.').rglob('__pycache__')]" # delete __pycache__ directories

