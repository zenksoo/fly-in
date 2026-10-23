*This project has been created as part of the 42 curriculum by amissa*

# Fly-In

## Description

Fly-In is a Python simulation that routes a fleet of drones through a network of
connected hubs. It parses a graph from a text map, plans a turn-by-turn route
for every drone, writes the resulting movements to a solution file, and
visualizes the simulation in an MLX42 window.

The project was designed for the Fly-in subject: all drones must travel from a
unique `start_hub` to a unique `end_hub` while respecting blocked hubs, hub
occupancy limits, connection capacities, and the extra movement cost of
restricted hubs.

## Features

- Input-map parsing and validation with Pydantic models.
- Undirected graph construction without a third-party graph library.
- Heap-based weighted pathfinding for each drone.
- Turn scheduling with waiting steps when a hub or connection is unavailable.
- Hub occupancy and connection-capacity checks.
- Two-turn movement representation for restricted destinations.
- MLX42 visualization of hubs, links, capacities, drone positions, and turns.
- Keyboard controls for starting, pausing, resetting, and changing animation
  speed.
- Type annotations, Flake8 checks, and mypy checks through the Makefile.

## Requirements

- Linux or macOS.
- Python 3.10 or later
- [`uv`](https://docs.astral.sh/uv/) for dependency installation and execution.
- A graphical session supported by MLX42.
- Git, CMake, and a C/C++ compiler if the bundled MLX42 shared library must be
  rebuilt.

Python dependencies are declared in [`pyproject.toml`](pyproject.toml):
Pydantic, Pillow, NumPy, Flake8, and mypy. The local
[`MLX/libmlx.py`](MLX/libmlx.py) module provides the ctypes declarations used to
load MLX42.

## Instructions

### Install dependencies

Install the Python dependencies with:

```sh
make install
```

This runs `uv sync` and creates or updates the project environment.

The repository includes `libmlx42.so` for Linux and `libmlx42.dylib` for macOS.
If the shared library needs to be rebuilt, run:

```sh
make mlxlib
make install
```

`make mlxlib` clones MLX42 into `/tmp/mlx42`, builds it with CMake, and moves
the resulting shared library into the repository root. If your platform or
environment already provides a compatible MLX42 library, use that library
instead.

### Run the application

Run the default map with:

```sh
make run
```

The default invocation reads `Maps/custom/fly-in.txt`, writes
`simulation_output.txt`, prints the generated solution, and opens the MLX42
window.

The entry point can also be run directly:

```sh
uv run fly_in.py
```

Command-line options:

| Option | Default | Description |
| --- | --- | --- |
| `-m`, `--map` | `Maps/custom/fly-in.txt` | Path to the input map |
| `-o`, `--output` | `simulation_output.txt` | Path to the generated solution |
| `-h`, `--help` | — | Show the command-line help |

For example:

```sh
uv run fly_in.py \
  --map Maps/easy/01_linear_path.txt \
  --output /tmp/linear-solution.txt
```

The map path must point to an existing file. The output path may be new, but it
must not point to a directory. Parser and command-line errors are printed to
stderr and cause a non-zero exit status.

### Development commands

```sh
make debug   # Run through Python's built-in pdb debugger
make lint    # Run Flake8 and the configured mypy checks
make clean   # Remove __pycache__ and .mypy_cache directories
```

The `lint` target runs Flake8 and mypy with the subject's required options:
`--warn-return-any`, `--warn-unused-ignores`, `--ignore-missing-imports`,
`--disallow-untyped-defs`, and `--check-untyped-defs`. The MLX ctypes binding is
excluded from mypy.

## Map format

The first non-comment line must declare a positive number of drones. Hubs must
be declared before the connections that reference them. Hub names cannot
contain whitespace or `-`.

```text
nb_drones:	2

start_hub:	start		0 0 	[color=green]
hub:		junction	1 0 	[zone=priority color=yellow max_drones=2]
end_hub:	goal		2 0 	[color=red]

connection:	start-junction		[max_link_capacity=2]
connection:	junction-goal		[max_link_capacity=2]
```

### Hub declarations

```text
start_hub: <name> <x> <y> [metadata]
hub:       <name> <x> <y> [metadata]
end_hub:   <name> <x> <y> [metadata]
```

Coordinates are integer values. A valid map has exactly one start hub and one
end hub. Metadata is optional and is written as space-separated `key=value`
pairs inside one bracketed block. Supported hub metadata is:

| Key | Default | Meaning |
| --- | --- | --- |
| `zone` | `normal` | `normal`, `blocked`, `restricted`, or `priority` |
| `color` | `green` | A color name defined by `Utils/Types.py` |
| `max_drones` | `1` | Maximum occupancy of the hub; must be positive |

Zone behavior:

- `normal`: destination movement costs one turn.
- `priority`: destination movement costs one turn and is preferred during
  path selection.
- `restricted`: destination movement costs two turns.
- `blocked`: cannot be entered and is removed from the routing graph.

The start hub is where every drone is initialized. The end hub accepts all
drones in the visualizer. Regular hubs use their configured `max_drones`
capacity.

### Connections

```text
connection: <hub-name>-<hub-name> [max_link_capacity=<positive integer>]
```

Connections are bidirectional. `max_link_capacity` defaults to `1` and limits
the number of drones using the connection at the same time. Connection
metadata may contain only `max_link_capacity`.

Blank lines and text after `#` are ignored. The parser rejects malformed
declarations, missing or duplicate hubs, duplicate connections, unknown hubs,
self-connections, invalid zone or color names, and non-positive capacities.

## Example

Using the map above with two drones, the generated solution has the following
shape:

```text
D1-junction	D2-junction
D1-goal		D2-goal
```

Each line represents one simulation turn. Each movement is space-separated.
`D<ID>-<hub>` means that the drone arrived at a hub. A restricted movement is
represented by two events:

```text
D1-junction-restricted
D1-restricted
```

The first event shows the drone in transit on the connection; the second shows
its arrival at the restricted hub. Drones that wait do not appear on that
turn's output line. The output file is overwritten on each run and is also
printed to the terminal before the graphical event loop starts.

## Algorithm and implementation

The main implementation is split into four stages:

1. [`MapParser`](Parser/Parser.py) reads the map in declaration order,
   validates syntax and metadata, and creates typed `Hub` and `Connection`
   models.
2. [`GraphBuilder`](PathFinding/dijkstra_algo.py) creates an undirected
   adjacency list and excludes blocked hubs.
3. [`PathFinding`](PathFinding/dijkstra_algo.py) uses a heap-based,
   Dijkstra-style search to plan a route for each drone. Normal and priority
   destinations add one turn; restricted destinations add two. If a movement
   cannot currently be scheduled, the search inserts a waiting step and retries
   the route under the updated turn state.
4. The scheduled steps are grouped by turn and consumed by
   [`DroneSimulation`](Simulation/drone_simulation.py), which drives both the
   text output and the animation.

The scheduler checks destination occupancy and connection occupancy before
accepting a move. It allows drones to move simultaneously when capacities
permit, and restricted crossings occupy a connection during transit before the
drone reaches its destination on the following turn.


## Visualization

The graphical interface is implemented with MLX42 and configured by
[`config.toml`](config.toml). It:

- lays out hubs using the integer coordinates from the map;
- uses different artwork for normal, blocked, restricted, and priority zones;
- draws bidirectional connections with a width based on link capacity;
- displays hub names, occupancy/capacity labels, and connection capacities;
- assigns colored drone sprites and animates their planned movements;
- optionally draws each drone's traveled path;
- displays the current turn and animation speed.

Keyboard controls:

| Key | Action |
| --- | --- |
| `Space` | Start or pause the animation |
| `R` | Reset all drones and the turn counter |
| `Left` | Decrease animation speed, down to the minimum |
| `Right` | Increase animation speed, up to the maximum |
| `E` | Exit the window |

The visualization is not only decorative: it makes occupancy, link capacity,
waiting, restricted transit, simultaneous movement, and the final delivery
state visible while the text solution remains available for inspection.

## Project layout

```text
fly_in.py                 CLI entry point and simulation orchestration
Parser/                   Map syntax and validation
PathFinding/              Graph construction and route planning
Simulation/               Animation state and turn progression
Visualizer/               MLX42 window, rendering, and keyboard controls
MLX/                      ctypes bindings for MLX42
MLXCanvas/                Image, text, pixel, and drawing helpers
Utils/                    Typed domain models and enums
CExceptions/              Project-specific parser and runtime errors
Maps/                     Easy, medium, hard, custom, and invalid examples
Assets/                   Fonts, hub artwork, drone artwork, and banner
config.toml               Window and layout configuration
Makefile                  Install, run, debug, clean, lint, and mlxlib targets
simulation_output.txt     Generated turn-by-turn solution
```

## Sample maps

The repository includes:

- `Maps/easy/` for simple paths and basic capacity behavior;
- `Maps/medium/` for dead ends, loops, and priority routing;
- `Maps/hard/` for larger routing and capacity challenges;
- `Maps/challenger/` for the optional `The Impossible Dream` challenge;
- `Maps/custom/` for focused scenarios such as bottlenecks, waiting, and
  restricted movement;
- `Maps/invalid_maps/` for parser and connectivity error cases.

## Resources

- [Python `argparse` documentation](https://docs.python.org/3/library/argparse.html) : command-line parsing.
- [Python `heapq` documentation](https://docs.python.org/3/library/heapq.html) : priority-queue operations used by pathfinding.
- [Python `tomllib` documentation](https://docs.python.org/3/library/tomllib.html)
 : TOML configuration loading.
- [Pydantic documentation](https://pydantic.dev/docs/validation/latest/get-started/) : typed data models and
  validation.
- [Pillow documentation](https://pillow.readthedocs.io/) : image loading and
  conversion.
- [MLX42 documentation](https://github.com/codam-coding-college/MLX42) | [MinilibX-42-Pyhton-Documentation](https://github.com/SaraFreitas-dev/MinilibX-42-Pyhton-Documentation/tree/main) :
  windowing, images, input events, and rendering.
- [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
 : shortest-path algorithm background.
- [Line Drawing Algo](https://en.wikipedia.org/wiki/Line_drawing_algorithm) : for drawing line in 2d space
### AI usage

AI assistance was used to review the subject requirements, organize this README, and explain the existing implementation.
