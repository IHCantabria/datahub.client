.ONESHELL:
.PHONY: all init venv clean new_venv test black release

SHELL=/bin/bash

VENV_NAME?=env
VENV_ACTIVATE=$(shell pwd)/${VENV_NAME}/bin/activate
RESOURCES=${HOME}/workspace/recursosIT

all:
	@echo "make init"
	@echo "    Create python virtual environment and install dependencies."
	@echo "make run"
	@echo "    Run server."
	@echo "make clean"
	@echo "    Remove python artifacts and virtualenv."
	@echo "make black"
	@echo "    Run Black code style."
	@echo "make release"
	@echo "    Prepare project for tag."


init:
	@which dpkg-buildpackage > /dev/null || echo "dpkg-buildpackage not found. Try run: sudo apt install -y debhelper dh-virtualenv dh-systemd" >&2
	@which python3 > /dev/null || echo "python3 not found. Try run: sudo apt install -y python3 python3-pip" >&2
	@which virtualenv > /dev/null || echo "virtualenv not found. Try run: sudo python3 -m pip install virtualenv" >&2
	@make venv
	@test ${RESOURCES} && make prepare-code


prepare-code:
	
	test -f .vscode || mkdir .vscode
	cp ${RESOURCES}/vscode/*json .vscode
	cp ${RESOURCES}/gitignores/python.gitignore .gitignore


venv: 
	@test -f $(VENV_ACTIVATE) || make new_venv
	

new_venv:
	python -m venv ${VENV_NAME} --clear
	source ${VENV_ACTIVATE}
	python -m pip install setuptools
	python -m pip install wheel pylint black radon pytest pytest-sugar
	@test -f requirements.des.txt 	&&	python -m pip install -r requirements.des.txt


clean:
	find . -name '*.pyc' -exec rm --force {} +
	rm -rf $(VENV_NAME) *.eggs *.egg-info dist build docs/_build .cache


test: venv
	source ${VENV_ACTIVATE}
	python -m pytest


black: venv
	source ${VENV_ACTIVATE}
	python -m black $(shell git ls-files | grep -e "\w*.py\b";git ls-files --others --exclude-standard | grep -e "\w*.py\b")

radon: venv
	source ${VENV_ACTIVATE}
	python -m radon cc $(shell git ls-files | grep -e "\w*.py\b";git ls-files --others --exclude-standard | grep -e "\w*.py\b")

release: venv black radon test
	source ${VENV_ACTIVATE}
	python -m pip freeze > requirements.des.txt
