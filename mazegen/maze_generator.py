from __future__ import annotations

import random
from collections import deque

from typing import Optional, Generator, Deque, Set, Tuple

# Direction bit constants (N=1, E=2, S=4, W=8)
N = 1
E = 2
S = 4
W = 8

# Direction vectors, bitmask, and direction labels
DIRS = [
    (0, -1, N, 'N'),   # North
    (1, 0, E, 'E'),    # East
    (0, 1, S, 'S'),    # South
    (-1, 0, W, 'W'),   # West
]

# Opposite wall mapping
OPPOSITE = {N: S, S: N, E: W, W: E}


class MazeGenerator:
    """DFS-based maze generator with integrated BFS solver.

    The grid uses 4-bit wall encoding per cell:
      - Bit 0 (N=1): North wall closed
      - Bit 1 (E=2): East wall closed
      - Bit 2 (S=4): South wall closed
      - Bit 3 (W=8): West wall closed
    A value of 15 (0xF) means all walls are closed.

    Usage::

        gen = MazeGenerator(width=20, height=20, entry=(0,0), exit=(19,19),
                            perfect=True)
        gen.generate()
        path = gen.solve()  # -> 'NESSWN...' or None
    """

    def __init__(self, width: int, height: int,
                 entry: tuple[int, int], exit: tuple[int, int],
                 perfect: bool, seed: Optional[int] = None) -> None:
        """Initialize the maze generator.

        Args:
            width: Number of columns in the maze.
            height: Number of rows in the maze.
            entry: (x, y) coordinates of the maze entrance.
            exit: (x, y) coordinates of the maze exit.
            perfect: If True, generate a perfect maze (no loops).
            seed: Optional RNG seed for reproducibility.
        """
        self.width: int = width
        self.height: int = height
        self.entry: tuple[int, int] = entry
        self.exit: tuple[int, int] = exit
        self.perfect: bool = perfect
        self.seed: Optional[int] = seed
        # Always reset the random seed. None = system/random time.
        # We check 'is not None' because '0' is a valid seed but evaluates to False.
        if self.seed is not None:
            random.seed(self.seed)

        self.warning: str = ""

        self.grid: list[list[int]] = [
            [15 for _ in range(self.width)]
            for _ in range(self.height)
        ]
        self.blocked: set[tuple[int, int]] = set()

        self.pattern: list[list[bool]] = [
            [False for _ in range(self.width)]
            for _ in range(self.height)
        ]
        self.pattern_cells: list[tuple[int, int]] = []

    def _in_bounds(self, x: int, y: int) -> bool:
        """Return True if (x, y) is within the maze grid."""
        return 0 <= x < self.width and 0 <= y < self.height

    def _neighbors(self, x: int, y: int) -> \
            Generator[tuple[int, int, int, str], None, None]:
        """Yield valid neighboring cells and their wall bits."""
        for dx, dy, wall, label in DIRS:
            nx, ny = x + dx, y + dy
            if self._in_bounds(nx, ny):
                yield nx, ny, wall, label

    def _carve_between(self, x: int, y: int, nx: int, ny: int,
                       wall: int) -> None:
        """Open the wall between (x,y) and its neighbor (nx, ny)."""
        self.grid[y][x] &= ~wall
        self.grid[ny][nx] &= ~OPPOSITE[wall]

    def _seal_cell(self, x: int, y: int) -> None:
        """Fully close a cell (all 4 walls = 1) and seal adjacent neighbors.

        This ensures the 42-pattern cells appear truly "blocked off" with
        consistent, coherent wall state between cell and its neighbors.
        """
        self.grid[y][x] = 15  # close all walls of this cell
        # For each neighbor, close the wall on their side facing this cell
        for dx, dy, wall, label in DIRS:
            nx, ny = x + dx, y + dy
            if self._in_bounds(nx, ny):
                # close the neighbor's wall that faces (x,y)
                self.grid[ny][nx] |= OPPOSITE[wall]

    def generate(self) -> None:
        """Generate the maze using DFS, then embed the '42' pattern.

        Generates a perfect or imperfect maze (with loops) depending on
        the ``perfect`` flag in :attr:`params`. The '42' pattern is drawn
        after generation by sealing the corresponding cells.
        """
        self.add_42_pattern()
        self.blocked = set(self.pattern_cells)

        self._dfs_from_entry()

        if not self.perfect:
            self._add_loops(loop_factor=0.08)

        # Re-seal all 42 cells after DFS (DFS may have opened their walls)
        for px, py in self.pattern_cells:
            self._seal_cell(px, py)

    def _dfs_from_entry(self) -> None:
        """Run iterative DFS from the entry point to carve paths."""
        ex, ey = self.entry
        visited: set[tuple[int, int]] = set(self.blocked)

        stack = [(ex, ey)]
        visited.add((ex, ey))

        while stack:
            x, y = stack[-1]
            neigh = [(nx, ny, w, l) for nx, ny, w, l
                     in self._neighbors(x, y)
                     if (nx, ny) not in visited]
            if not neigh:
                stack.pop()
                continue
            nx, ny, wall, label = random.choice(neigh)
            visited.add((nx, ny))
            self._carve_between(x, y, nx, ny, wall)
            stack.append((nx, ny))

    def _add_loops(self, loop_factor: float) -> None:
        """Add extra random openings to create cycles (imperfect maze)."""
        w, h = self.width, self.height
        attempts = max(1, int(w * h * loop_factor))

        for _ in range(attempts):
            x = random.randrange(w)
            y = random.randrange(h)
            if (x, y) in self.blocked:
                continue
            neigh = [(nx, ny, wall, label)
                     for nx, ny, wall, label in self._neighbors(x, y)
                     if (nx, ny) not in self.blocked]
            if not neigh:
                continue
            nx, ny, wall, label = random.choice(neigh)
            self._carve_between(x, y, nx, ny, wall)

    def add_42_pattern(self) -> None:
        """Mark the cells that form the '42' pattern.

        This only registers the cells; call :meth:`generate` to both
        mark and physically seal them in the grid.

        Raises:
            ValueError: If ENTRY or EXIT overlaps with the '42' cells.
        """
        w, h = self.width, self.height
        if w < 12 or h < 12:
            self.warning = "Maze too small for '42' pattern (need >= 12x12)"
            return

        pattern_w = 9
        pattern_h = 7
        start_x = (w - pattern_w) // 2
        start_y = (h - pattern_h) // 2

        def mark(px: int, py: int) -> None:
            if 0 <= px < w and 0 <= py < h:
                self.pattern[py][px] = True
                if (px, py) not in self.pattern_cells:
                    self.pattern_cells.append((px, py))

        # -------- DRAW 4 --------
        for i in range(4):
            mark(start_x, start_y + i)         # Left bar
        for i in range(7):
            mark(start_x + 3, start_y + i)     # Right bar
        for j in range(1, 3):
            mark(start_x + j, start_y + 3)     # Horizontal bar

        # -------- DRAW 2 --------
        ox = start_x + 5
        for j in range(4):
            mark(ox + j, start_y)              # Top bar
            mark(ox + j, start_y + 3)          # Middle bar
            mark(ox + j, start_y + 6)          # Bottom bar
        for i in range(1, 3):
            mark(ox + 3, start_y + i)          # Top-right vertical
        for i in range(4, 6):
            mark(ox, start_y + i)              # Bottom-left vertical

        # OVERLAP CHECK
        entry = self.entry
        exit_ = self.exit
        if entry in self.pattern_cells:
            raise ValueError(
                f"ENTRY {entry} overlaps with mandatory 42 pattern"
            )
        if exit_ in self.pattern_cells:
            raise ValueError(
                f"EXIT {exit_} overlaps with mandatory 42 pattern"
            )

    def solve(self) -> Optional[str]:
        """Find the shortest path using BFS.

        Returns:
            A string of directions ('N', 'E', 'S', 'W') from entry to exit,
            or ``None`` if no path exists.
        """
        h, w = self.height, self.width
        sx, sy = self.entry
        ex, ey = self.exit

        queue: Deque[Tuple[int, int, str]] = deque([(sx, sy, "")])
        visited: Set[Tuple[int, int]] = {(sx, sy)}

        while queue:
            x, y, path = queue.popleft()
            if (x, y) == (ex, ey):
                return path

            for dx, dy, wall_bit, label in DIRS:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    if ((self.grid[y][x] & wall_bit) == 0
                            and (nx, ny) not in visited):
                        visited.add((nx, ny))
                        queue.append((nx, ny, path + label))
        return None

    def save_maze(self, file_path: str, path: Optional[str] = None) -> None:
        """Save the maze to a file in the required hexadecimal format.

        Args:
            file_path: Destination file path for the saved maze.
            path: Optional solution path string (e.g. 'NESSWN...');
                  if *None*, :meth:`solve` is called automatically.
        """
        if path is None:
            path = self.solve()

        with open(file_path, "w", encoding="utf-8") as f:
            for row in self.grid:
                f.write("".join(f"{cell:X}" for cell in row) + "\n")

            f.write("\n")
            f.write(f"{self.entry[0]},{self.entry[1]}\n")
            f.write(f"{self.exit[0]},{self.exit[1]}\n")
            f.write(f"{path if path else ''}\n")