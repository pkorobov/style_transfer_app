.PHONY: run-server
port="1489"
host="127.0.0.1"
run-server:
	uvicorn server:app --host=$(host) --port=$(port) --reload

.PHONY: run-bot
run-bot:
	python bot_interface.py

.PHONY: run-server-and-bot
run-server-and-bot:
	make run-server & make run-bot

.PHONY: server-example
server-example:
	curl -F "content=@data/golden_gate.jpg" -F "style=@data/brushstrokes.jpg"  http://127.0.0.1:1489/generate  --output result_image.png

.PHONY: lint
lint:
	pylint *.py -v
	pydocstyle -v

.PHONY: tests
tests:
	python -m unittest -v

.PHONY: docs
docs:
	sphinx-build -b html docs/ docs/_build
