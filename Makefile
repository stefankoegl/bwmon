
test:
	python runmonitor.py

clean:
	find -name '*.pyc' -exec rm '{}' \;

.PHONY: test clean
.DEFAULT: test

