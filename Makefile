PYCACH_FILES = $$(find . -type d -name "__pycache__")
MYPY_FILES =  $$(find . -type d -name ".mypy_cache")

install:
	@uv sync

run:
	@uv run fly_in.py

debug:
	@uv run -m pdb fly_in.py


clean:
	@rm -rf $(PYCACH_FILES) $(MYPY_FILES)


lint:
	@uv run flake8 --exclude=.venv,MLX .
	@uv run mypy --exclude=MLX/libmlx.pyi . --warn-return-any \
	--warn-unused-ignores --ignore-missing-imports \
	--disallow-untyped-defs --check-untyped-defs

mlxlib:
	git clone https://github.com/codam-coding-college/MLX42.git /tmp/mlx42
	cmake -S /tmp/mlx42 -B /tmp/mlx42/build -DBUILD_SHARED_LIBS=ON && cmake --build /tmp/mlx42/build --parallel
	mv /tmp/mlx42/build/libmlx42.* ./
