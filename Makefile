develop:
	uv sync
dist:
	uv build
upload:
	uv build
	uv publish --keyring-provider subprocess -u __token__
clean:
	rm -rf *.egg-info/ dist/ build/
test:
	uv run pytest -vx
