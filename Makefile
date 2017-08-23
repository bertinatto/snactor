.PHONY: clean
all: test

.PHONY: clean
clean:
	@rm -rf build/ dist/ *.egg-info
	@find . -name '__pycache__' -exec rm -fr {} +
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +

.PHONY: test
test:
	@make clean
	@python -m unittest discover

.PHONY: setup-env
setup-env:
	@pip install -r deps/dev.txt
