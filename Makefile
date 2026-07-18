PYCACH_FILES = $$(find . -type d -name "__pycache__")
MYPY_FILES =  $$(find . -type d -name ".mypy_cache")

install:
	uv sync

run:
	uv run fly_in.py

debug:
	uv run -m pdb fly_in.py


clean:
	rm -rf $(PYCACH_FILES) $(MYPY_FILES)


lint:
	uv tool run flake8 --exclude=.venv,MLX .
	uv tool run mypy . --warn-return-any \
	--warn-unused-ignores --ignore-missing-imports \
	--disallow-untyped-defs --check-untyped-defs
