.PHONY: run lint clean

run:
	uv run python main.py

dry-run:
	uv run python main.py --dry-run

lint:
	uv run ruff check .

fix:
	uv run ruff check --fix .

clean:
	rm -f /var/log/ferakh.log
