setup:
	@python setup.py sdist bdist_wheel
compile:
	@bash compile.sh
push:
	@git add . && git commit -m "AUTOMATICALLY UPDATE" && git push