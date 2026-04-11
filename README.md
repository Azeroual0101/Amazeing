*This project has been created as part of the 42 curriculum by [mobougha] & [abdazero].*

# A-Maze-ing

## Description
A-Maze-ing is a Python-based maze generation and visualization tool. The primary goal of this project is to create complex, solvable mazes based on user-defined configurations, featuring a mandatory "42" pattern embedded into the center of the grid. The application provides a command-line interface and a terminal-based visualizer to explore the generated mazes.

## Instructions

### Prerequisites
- Python 3.8 or higher.
- A terminal with ANSI color support (standard on Linux/macOS).

### Execution
Run the application using the provided `Makefile` or directly with Python by passing a configuration file:
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
The configuration file (`config.txt`) must follow a strict `KEY=VALUE` format. Blank lines and lines starting with `#` are ignored. Values can have optional leading/trailing whitespace.

### Format Example
```ini
# Grid dimensions (min 12x12 for '42' pattern)
WIDTH=20
HEIGHT=20

# Starting and ending coordinates (x,y)
ENTRY=0,0
EXIT=19,19

# Path to save the hex-encoded maze
OUTPUT_FILE=maze.txt

PERFECT=false

# Optional seed for reproducible generation
SEED=my_unique_seed_123
```

### Supported Keys
| Key | Description | Requirement |
| :--- | :--- | :--- |
| `WIDTH` | Number of columns | Integer > 0 |
| `HEIGHT` | Number of rows | Integer > 0 |
| `ENTRY` | Starting coordinates | Valid `x,y` |
| `EXIT` | Final coordinates | Valid `x,y` |
| `OUTPUT_FILE` | Hex output path | Valid filename |
| `PERFECT` | Loop generation | `true` or `false` |
| `SEED` | Random seed | Optional string/int |

## Technical Choices

### Maze Generation Algorithm
I chose the **Iterative Depth-First Search (DFS)** algorithm.

### Why this algorithm?
- **Solvability:** It guarantees every cell is reachable and there is exactly one path between any two points (in "perfect" mode).
- **Aesthetics:** DFS creates long, winding corridors and deep "dead ends," which are more challenging and visually interesting than other algorithms.

### Reusability
The project is architected with a strict separation of concerns, making significant parts of the code reusable:

- **`mazegen` Package:** The generation and rendering logic are encapsulated in a standalone package.
- **`MazeGenerator` Class:** This core logic is entirely decoupled from the display. It can be imported into any other Python project to generate grids or solve paths.
- **Hex Encoding logic:** The `save_maze` function adheres to the standard 4-bit wall encoding format (N=1, E=2, S=4, W=8), making the output compatible with professional hex-grid tools.

#### How to Reuse (Example Script)
```python
from mazegen.maze_generator import MazeGenerator, MazeParams

# Configure parameters
params = MazeParams(width=20, height=20, entry=(0,0), exit=(19,19), perfect=True)

# Generate and solve
gen = MazeGenerator(params)
gen.generate()
path = gen.solve()

# Access the raw grid (hex values)
print(gen.grid)
```

## Resources
- [Wikipedia: Maze Generation Algorithms](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Python Random Module Documentation](https://docs.python.org/3/library/random.html)

### AI Usage
- help clarif

## Team & Project Management

### Roles
- **[mobougha]:** Responsible for maze generation and configuration parsing logic.
- **[abdazero]:** Responsible for the pathfinding (solving) algorithms and the terminal display/renderer.

### Planning & Evolution
- **Initial Plan:** Build a simple DFS generator that outputs text.
- **Mid-Project:** Realized the need for an iterative approach to support larger grids and added the BFS solver to verify validity.
- **Final Phase:** Integrated the visualizer and the mandatory "42" pattern logic.

# Amazeing
