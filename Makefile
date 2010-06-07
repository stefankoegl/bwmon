
test:
	python runmonitor.py

docs:
	epydoc -n 'bwmon User-space bandwidth monitor' -o docs/ bwmon -v --exclude='.*_test'

clean:
	find -name '*.pyc' -exec rm '{}' \;

.PHONY: test clean docs
.DEFAULT: test

