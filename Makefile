setup:
	@python setup.py sdist bdist_wheel
compile:
	@bash compile.sh
push:
	@git add . && git commit -m "AUTOMATICALLY UPDATE" && git push
createenv:
	@micromamba create -n celline && python -m ipykernel install --user --name celline --display-name "Python (celline)"