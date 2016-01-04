clear_pyc:
	find . -name '*.pyc' -delete

pylint:
	flake8 rest_arch
	PYTHONPATH="`pwd`/tools/pylint:${PYTHONPATH}" pylint --rcfile tools/pylint/pylintrc rest_arch

unittest: pylint
	mkdir -p .build
	py.test tests -rfExswX --duration=10 --junitxml=.build/unittest.xml --cov rest_arch --cov-report xml -n 4

bump:
	@if [ -z "$(ver)" ]; then echo 'usage: make bump ver=VER_NUM'; exit 1; fi
	@./tools/bump.py $(ver)

doc:
	make -C docs html

changelog:
	@git log --first-parent --pretty="format:* %B" v`python setup.py --version`..

