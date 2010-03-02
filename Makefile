test:
	(cd regress; python tests.py)

clean:
	find . -name '*.pyc' | xargs rm -f
	rm -f regress/parser.out
	rm -f regress/parsetab.py
	rm -f regress/testva.csv
	rm -f regress/testvendor.iif
