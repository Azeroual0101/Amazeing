*This project has been created as part of the 42 curriculum by [mobougha] & [abdazero].*

# A-Maze-ing

## Description
A-Maze-ing is a Python-based maze generation and visualization tool. The primary goal of this project is to create complex, solvable mazes based on user-defined configurations, featuring a mandatory "42" pattern embedded into the center of the grid. The application provides a command-line interface and a terminal-based visualizer to explore the generated mazes.

## Instructions

### Prerequisites
- Python 3.10 or higher.
- A terminal with ANSI color support (standard on Linux/macOS; Windows Terminal supported).

### Installation
Install the project as an editable package using the provided `Makefile`:
```bash
make install
# Equivalent to: pip install -e .
```

### Execution
Run the application using the `Makefile` or directly with Python by passing a configuration file:
```bash
make run
# OR
python3 a_maze_ing.py config.txt
```

### Visualizer Controls
Once the visualizer is open:
- `P`: Toggle the solution path visibility.
- `R`: Regenerate the maze (follows the seed if provided).
- `C`: Cycle through different UI color schemes.
- `Q`: Quit the application.

## Config File Structure
The configuration file (`config.txt`) must follow a strict `KEY=VALUE` format. Blank lines and lines starting with `#` are ignored. Inline comments (`# ...`) are also stripped. Keys are case-sensitive; values allow optional leading/trailing whitespace.

### Format Example
```ini
# Grid dimensions (min 12x12 for '42' pattern)
WIDTH=16
HEIGHT=16

# Starting and ending coordinates (x,y)
ENTRY=1,1
EXIT=14,14

# Path to save the hex-encoded maze
OUTPUT_FILE=maze.txt

PERFECT=true

# Optional seed for reproducible generation
SEED=100
```

### Supported Keys
| Key | Description | Requirement |
| :--- | :--- | :--- |
| `WIDTH` | Number of columns | Integer > 0 |
| `HEIGHT` | Number of rows | Integer > 0 |
| `ENTRY` | Starting coordinates | Valid `x,y` within bounds |
| `EXIT` | Final coordinates | Valid `x,y` within bounds |
| `OUTPUT_FILE` | Hex output path | Non-empty filename |
| `PERFECT` | Perfect maze (no loops) | `true` or `false` |
| `SEED` | Random seed | Optional integer (non-int strings are hashed) |

### Validation Rules
- **ENTRY ≠ EXIT**: The starting and ending coordinates must differ.
- **Bounds check**: Both ENTRY and EXIT must be within the grid (`0 ≤ x < WIDTH`, `0 ≤ y < HEIGHT`).
- **No overlap with 42 pattern**: ENTRY and EXIT must not overlap with the embedded "42" cells.
- **No duplicate keys**: Each key can only appear once.

## Project Structure
```
A-Maze-ing/
├── a_maze_ing.py         # Main entry point (config parsing, app loop)
├── renderer.py           # Terminal-based maze renderer (ANSI colors, key input)
├── config.txt            # Default configuration file
├── Makefile              # Build automation (install, run, lint, clean)
├── pyproject.toml        # PEP 517/518 packaging configuration
└── mazegen/              # Core generation & solving library
    ├── __init__.py       # Public API exports (MazeGenerator)
    └── maze_generator.py # MazeGenerator class (DFS generation, BFS solver, save)
```

## Technical Choices

### Maze Generation Algorithm
We chose the **Iterative Depth-First Search (DFS)** algorithm.

### Why this algorithm?
- **Solvability:** It guarantees every cell is reachable and there is exactly one path between any two points (in "perfect" mode).
- **Aesthetics:** DFS creates long, winding corridors and deep "dead ends," which are more challenging and visually interesting than other algorithms.
- **Loop support:** When `PERFECT=false`, a second pass adds random wall openings (~8% of cells) to create cycles.

### 42 Pattern Integration
The mandatory "42" pattern is embedded at the center of the grid. Pattern cells are first registered, then treated as **blocked** during DFS traversal. After maze generation, all pattern cells are fully **sealed** (all 4 walls closed), ensuring a coherent visual representation and correct wall state with adjacent cells.

### Pathfinding: BFS Solver
The `solve()` method uses **Breadth-First Search (BFS)**, which guarantees finding the **shortest path** from ENTRY to EXIT. It respects the wall encoding of each cell and returns a direction string (`'NESSWN...'`) or `None` if no path exists.

### Hex Encoding
The grid uses a standard **4-bit wall encoding** per cell:
| Bit | Direction | Value |
| --- | --------- | ----- |
| 0   | North     | 1     |
| 1   | East      | 2     |
| 2   | South     | 4     |
| 3   | West      | 8     |

A value of `F` (15) means all walls are closed. The output file stores one hex character per cell, making it compatible with standard maze tools.

### Reusability
The project is architected with a strict separation of concerns, making significant parts of the code reusable:

- **`mazegen` Package:** The generation, solving, and saving logic are encapsulated in a standalone, installable package.
- **`MazeGenerator` Class:** This core class is entirely decoupled from the display. It can be imported into any other Python project to generate grids, solve paths, and save results.
- **`save_maze()` method:** Integrated directly into `MazeGenerator`, producing the standard hex-encoded output file with entry/exit coordinates and the solution path.

#### How to Reuse (Example Script)
```python
from mazegen import MazeGenerator

# Create a generator with direct parameters
gen = MazeGenerator(
    width=20,
    height=20,
    entry=(0, 0),
    exit=(19, 19),
    perfect=True,
    seed=42,
)

# Generate the maze and solve it
gen.generate()
path = gen.solve()  # -> 'NESSWN...' or None

# Save to file (hex grid + coordinates + path)
gen.save_maze("my_maze.txt", path)

# Access the raw grid (list[list[int]] of hex values)
print(gen.grid)
```

## Makefile Targets
| Target | Command | Description |
| :----- | :------ | :---------- |
| `make install` | `pip install -e .` | Install the project in editable mode |
| `make run` | `python3 a_maze_ing.py config.txt` | Run the maze generator |
| `make debug` | `python3 -m pdb a_maze_ing.py config.txt` | Run with Python debugger |
| `make lint` | `flake8 . && mypy ...` | Run linting and type checking |
| `make clean` | removes build artifacts | Clean generated files |
| `make build` | `python3 -m build` | Build distribution packages |

## Resources
- [Wikipedia: Maze Generation Algorithms](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Python Random Module Documentation](https://docs.python.org/3/library/random.html)

### AI Usage
- Help clarifying algorithm choices and debugging edge cases.

## Team & Project Management

### Roles
- **[mobougha]:** Responsible for maze generation and configuration parsing logic.
- **[abdazero]:** Responsible for the pathfinding (solving) algorithms and the terminal display/renderer.

### Planning & Evolution
- **Initial Plan:** Build a simple DFS generator that outputs text.
- **Mid-Project:** Realized the need for an iterative approach to support larger grids and added the BFS solver to verify validity.
- **Final Phase:** Integrated the visualizer, the mandatory "42" pattern logic, and encapsulated `save_maze` within `MazeGenerator` for better OOP design.
