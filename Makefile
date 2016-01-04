clear_pyc:
	find . -name '*.pyc' -delete

pylint:
	flake8 rest_arch
	PYTHONPATH="`pwd`/tools/pylint:${PYTHONPATH}" pylint --rcfile tools/pylint/pylintrc rest_arch

unittest: pylint
	mkdir -p .build
	py.test tests -rfExswX --duration=10 --junitxml=.build/unittest.xml --cov rest_arch --cov-report xml -n 4
