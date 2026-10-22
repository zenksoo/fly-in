*This project has been created as part of the 42 curriculum by amissa*

# Fly-In

## Description

Fly-In is a Python graph-based system for designing and managing the movement
of multiple drones through a connected network of hubs. The graph represents
the operational environment: hubs are vertices with zone types, colors, and
occupancy limits, while connections are bidirectional edges with traversal and
capacity constraints.

The system coordinates a fleet from one `start_hub` to one `end_hub` while
managing shared resources, route selection, movement costs, waiting, and
conflicts between drones. Reaching the end hub is the simulation objective,
but the project focuses on the broader problem of planning and scheduling many
drones safely and efficiently across the graph. Routes are written turn by
turn and animated in an MLX42 window.

The application combines four parts:

- a validated map parser;
- a weighted graph builder and route planner;
- a turn-based movement plan written to a text file;
- an MLX42 visualization showing hubs, links, capacities, drones, and turns.

The implementation is object-oriented and uses Pydantic models for typed map
data. It does not use a graph library.

## Requirements

- Linux or macOS with Python 3.12 or later;
- `uv` for dependency management;
- a working MLX42 shared library named `libmlx42.so` on Linux or
	`libmlx42.dylib` on macOS;
- a graphical session supported by MLX42.

Python dependencies are declared in `pyproject.toml`: Pydantic, Pillow, NumPy,
Flake8, and mypy. The bundled `MLX/libmlx.py` provides the ctypes bindings used
to load MLX42.

## Installation

```sh
make install
```

If MLX42 is not already installed, build the shared library with the project
target. This requires Git, CMake, a C/C++ compiler, and the MLX42 build
dependencies:

```sh
make mlxlib
make install
```

The target builds MLX42 in `/tmp/mlx42` and moves the resulting shared library
to the project root, where the Python binding looks for it first.

## Usage

Run the default map:

```sh
make run
```

The default map is `Maps/custom/fly-in.txt`, and the default output file is
`simulation_output.txt`.

Run another map or choose another output file:

```sh
uv run fly_in.py --map Maps/easy/01_linear_path.txt \
								 --output simulation_output.txt
```

Options:

| Option | Default | Meaning |
| --- | --- | --- |
| `-m`, `--map` | `Maps/custom/fly-in.txt` | Input map path |
| `-o`, `--output` | `simulation_output.txt` | Route output path |

The program validates the input path, parses the map, computes the complete
solution, prints the generated output, and opens the visualizer. Parsing and
invalid-map errors are reported on stderr and return a non-zero exit status.

## Map Format

The first line must define a positive drone count. Hubs must be declared before
their connections, and hub names cannot contain spaces or dashes.

```text
nb_drones: 2
start_hub: start 0 0 [color=green]
hub: junction 1 0 [zone=priority color=yellow max_drones=2]
end_hub: goal 2 0 [color=red]
connection: start-junction [max_link_capacity=2]
connection: junction-goal [max_link_capacity=2]
```

Supported hub types are `normal`, `blocked`, `restricted`, and `priority`.
Normal and priority moves cost one turn; a restricted destination costs two
turns; blocked hubs are excluded from the routing graph. `max_drones` defaults
to `1`, and `max_link_capacity` defaults to `1`. Start and end hubs are treated
as unlimited-capacity locations by the visualizer and route planner.

Comments beginning with `#` and blank lines are ignored. Metadata is written as
space-separated `key=value` pairs inside one bracketed block. In this
implementation, `color` values must be names present in `Utils/Types.py`.

The parser rejects malformed lines, missing or duplicate hubs, duplicate
connections, unknown hubs, self-connections, invalid zone types, and non-
positive capacity values. A valid but disconnected map is reported as an
invalid route during pathfinding.

## Algorithm

`GraphBuilder` creates an undirected adjacency list and removes blocked hubs.
`PathFinding` then plans a route for each drone with a heap-based weighted
search, using movement cost `1` for normal and priority hubs and `2` for
restricted hubs. Priority destinations and the end hub are ordered favorably
when route steps are compared.

While routes are planned, the implementation tracks scheduled movements and
checks hub occupancy and connection capacity. When a move is unavailable, a
drone receives a waiting step. Restricted moves are represented as two output
events: the connection is shown while the drone is in transit, then the
destination hub is shown on arrival. The final plan is grouped into turn lists,
so all movements on one line belong to the same simulation turn.

Path planning is repeated once per drone. For a graph with `V` hubs and `E`
connections, one heap search is approximately `O((V + E) log V)`; total work
scales with the number of drones and the route scheduling checks. The planned
routes are kept in memory and reused by both the output writer and the
visualizer.

## Output Format

`simulation_output.txt` contains one line per simulation turn. Each movement is
space-separated and uses either `D<ID>-<hub>` or `D<ID>-<origin>-<destination>`
while a drone is crossing toward a restricted hub.

For the example map above, a valid output has this shape:

```text
D1-junction D2-junction
D1-goal D2-goal
```

Drones that do not move during a turn are omitted. The generated file is also
printed to the terminal before the MLX event loop starts.

## Visualization

The MLX42 window renders the map using the coordinates from the input file.
Hub artwork changes with the zone type, connections show their capacities,
labels show hub occupancy, and colored drone sprites move along the planned
route. Configuration is read from `config.toml`.

Keyboard controls:

| Key | Action |
| --- | --- |
| `Space` | Start or pause the animation |
| `R` | Reset all drones and the turn counter |
| `Left` | Decrease animation speed |
| `Right` | Increase animation speed |
| `E` | Exit |

## Project Layout

```text
fly_in.py                 CLI entry point and output generation
Parser/                   map syntax and validation
PathFinding/              graph construction and route planning
Simulation/               animation state and turn progression
Visualizer/               MLX42 window and keyboard controls
MLX/                     ctypes bindings for MLX42
MLXCanvas/                image, text, pixel, and drawing helpers
Utils/                    typed domain models and enums
CExceptions/              project-specific parser and runtime errors
Maps/                     sample, challenge, and invalid maps
Assets/                   fonts, hub images, drone image, and banner
config.toml               window and layout configuration
Makefile                  install, run, debug, clean, lint, and mlxlib tasks
```

## Development Commands

```sh
make debug     # Run through Python's debugger
make lint      # Run Flake8 and the required mypy checks
make clean     # Remove __pycache__ and .mypy_cache directories
```

The repository uses Python type hints throughout the application. The MLX
binding directory is excluded from the mypy command because it is a ctypes
foreign-function interface.

## Resources and AI Usage

The main reference is the Fly-in subject provided with this repository. Other
useful references are the Python documentation for `argparse`, `heapq`, and
`tomllib`, the Pydantic validation documentation, the Pillow documentation,
and the MLX42 documentation.

AI was used as a review and documentation aid: to summarize the subject's
README requirements, inspect the existing modules, organize the project
description, and check that the usage examples match the implemented CLI and
map syntax. The implementation and its behavior should still be verified by
the authors with tests and peer review.

## Known Scope

The current application is designed around the MLX42 graphical runtime. The
route file is generated before the window loop starts, while the visual
animation presents that precomputed plan. No automated test suite is currently
included in the repository; the supplied maps under `Maps/` are intended for
manual validation together with `make lint`.
