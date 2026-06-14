develop:
	uv sync
dist:
	uv build
upload:
	uv publish
clean:
	rm -rf *.egg-info/ dist/ build/
test:
	uv run pytest -vx
