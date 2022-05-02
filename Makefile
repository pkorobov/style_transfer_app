.PHONY: project-demo
project-demo: tests lint docs create-wheel

.PHONY: run-app
run-app:
	python3 -m style_transfer_app

.PHONY: run-server-only
port="1489"
host="127.0.0.1"
run-server-only:
	uvicorn style_transfer_app.server:app --host=$(host) --port=$(port) --reload

.PHONY: server-example
server-example:
	curl -F "content=@data/golden_gate.jpg" -F "style=@data/brushstrokes.jpg"  http://127.0.0.1:1489/generate  --output result_image.png

.PHONY: create-wheel
create-wheel:
	pip3 install build -U
	python3 -m build

.PHONY: install-wheel
install-wheel: dist
	pip3 install dist/style_transfer_app-0.0.1-py3-none-any.whl

.PHONY: lint
lint:
	pylint */*.py -v
	pydocstyle */*.py -v

.PHONY: tests
tests:
	python3 -m unittest -v

.PHONY: docs
docs:
	sphinx-build -b html docs/ docs/_build

.PHONY: gitclean
gitclean:
	git clean -xdf
