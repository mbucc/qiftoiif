test:
	(cd regress; python tests.py)

clean:
	find . -name '*.pyc' | xargs rm
