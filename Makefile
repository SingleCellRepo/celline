setup:
	@python setup.py sdist bdist_wheel
push:
	@git add . && git commit -m "AUTOMATICALLY UPDATE" && git push