.PHONY: sync test typecheck build check

sync:
	uv sync --frozen --all-extras

test: sync
	uv run pytest -v

typecheck: sync
	uv run mypy src/enjilib_jwt --strict

build: sync
	uv build

check: test typecheck build
