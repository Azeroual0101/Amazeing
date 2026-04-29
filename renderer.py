"""
Terminal renderer with colored walls, path highlighting, and keyboard controls.
"""

import os
import sys
from typing import List, Tuple, Optional


COLORS = {
    'reset': '\033[0m',
    'wall': '\033[90m',      # grey
    'path': '\033[92m',      # green
    'entry': '\033[94m',     # blue
    'exit': '\033[93m',      # yellow
    'pattern': '\033[91m',   # red for "42" cells
}


class MazeRenderer:
    """Handles ASCII rendering and user interaction."""

    def __init__(self,
                 grid: List[List[int]],
                 entry: Tuple[int, int],
                 exit_: Tuple[int, int],
                 pattern_cells: List[Tuple[int, int]]) -> None:
        """Initialize renderer with maze grid and key locations."""
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0])
        self.entry = entry
        self.exit = exit_
        self.pattern_cells = set(pattern_cells)
        self.show_path = False
        self.path_directions: Optional[str] = None
        self.wall_color = COLORS['wall']
        self.status_msg: str = ""

    def set_status(self, msg: str) -> None:
        """Set a status/warning message to display."""
        self.status_msg = msg

    def set_path(self, path: Optional[str]) -> None:
        """Set the shortest path to display."""
        self.path_directions = path
        self.show_path = True

    def toggle_path(self) -> None:
        """Show/hide the path."""
        self.show_path = not self.show_path

    def cycle_color(self) -> None:
        """Cycle through wall colors."""
        colors = [
            COLORS['wall'], '\033[96m', '\033[95m', '\033[93m', '\033[91m'
        ]
        current = (colors.index(self.wall_color)
                   if self.wall_color in colors else 0)
        next_color = colors[(current + 1) % len(colors)]
        self.wall_color = next_color

    def _is_on_path(self, x: int, y: int) -> bool:
        """Check if cell (x,y) lies on the computed path."""
        if not self.show_path or not self.path_directions:
            return False
        cx, cy = self.entry
        if (cx, cy) == (x, y):
            return True
        for d in self.path_directions:
            if d == 'N':
                cy -= 1
            elif d == 'S':
                cy += 1
            elif d == 'E':
                cx += 1
            elif d == 'W':
                cx -= 1
            if (cx, cy) == (x, y):
                return True
        return False

    def display(self) -> None:
        """Clear screen and draw the maze."""
        os.system('cls' if os.name == 'nt' else 'clear')
        wc = self.wall_color
        res = COLORS['reset']

        for y in range(self.height):
            top = ""
            for x in range(self.width):
                cell = self.grid[y][x]
                if cell & 1:
                    top += f"{wc}+---{res}"
                else:
                    top += f"{wc}+{res}   "
            print(top + f"{wc}+{res}")

            middle = ""
            for x in range(self.width):
                cell = self.grid[y][x]
                if cell & 8:
                    middle += f"{wc}|{res}"
                else:
                    middle += " "
                if (x, y) == self.entry:
                    middle += f"{COLORS['entry']} E {COLORS['reset']}"
                elif (x, y) == self.exit:
                    middle += f"{COLORS['exit']} X {COLORS['reset']}"
                elif (x, y) in self.pattern_cells:
                    middle += f"{wc}###{res}"
                elif self._is_on_path(x, y):
                    middle += f"{COLORS['path']} * {COLORS['reset']}"
                else:
                    middle += "   "
            middle += f"{wc}|{res}"
            print(middle)
        bottom = (f"{wc}+---{res}" * self.width) + f"{wc}+{res}"
        print(bottom)
        print("\nCommands: [R]egen  [P]ath  [C]olor  [Q]uit")
        if self.status_msg:
            print(
                f"{COLORS['pattern']}Warning: "
                f"{self.status_msg}{COLORS['reset']}"
            )

    def wait_key(self) -> str:
        """Wait for a single key press and return it as uppercase."""
        if sys.platform == 'win32':
            import msvcrt
            ch_bytes = msvcrt.getch()
            if ch_bytes == b'\x03':
                raise KeyboardInterrupt
            try:
                return ch_bytes.decode().upper()
            except (UnicodeDecodeError, AttributeError):
                return ""
        else:
            import termios
            import tty
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                if ch == '\x03':
                    raise KeyboardInterrupt
                return ch.upper()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
