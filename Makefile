.PHONY: test run

test:
	PYTHONPATH=. python tests/run.py

run:
	PYTHONPATH=. bin/montgolfier
