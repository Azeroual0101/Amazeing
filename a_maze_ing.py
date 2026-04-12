from __future__ import annotations

import random
import sys
from dataclasses import dataclass
from typing import Optional

from mazegen.maze_generator import MazeGenerator
from renderer import MazeRenderer


@dataclass(frozen=True)
class Config:
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: Optional[int] = None


def _parse_bool(value: str) -> bool:
    v = value.strip().lower()
    if v in {"true", "1", "yes", "y"}:
        return True
    if v in {"false", "0", "no", "n"}:
        return False
    raise ValueError(f"Invalid boolean value: {value!r} (expected True/False)")


def _parse_xy(value: str) -> tuple[int, int]:
    # Handle optional spaces around comma
    parts = [p.strip() for p in value.split(",")]
    if len(parts) != 2:
        raise ValueError(f"Invalid coordinate {value!r} (expected 'x,y')")
    try:
        return (int(parts[0]), int(parts[1]))
    except ValueError:
        raise ValueError(f"Invalid integer in coordinate: {value!r}")


def parse_config(file_path: str) -> Config:
    """Parse configuration from file with robust error handling."""
    raw: dict[str, str] = {}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for lineno, line in enumerate(f, start=1):
                # Remove comments and whitespace
                s = line.split("#")[0].strip()
                if not s:
                    continue
                if "=" not in s:
                    raise ValueError(
                        f"{file_path}:{lineno}: invalid line "
                        f"(missing '='): {line.strip()!r}"
                    )

                key, value = s.split("=", 1)
                key = key.strip()
                value = value.strip()

                if not key:
                    raise ValueError(f"{file_path}:{lineno}: empty key")
                if key in raw:
                    raise ValueError(
                        f"{file_path}:{lineno}: duplicate key: {key}"
                    )

                raw[key] = value
    except FileNotFoundError:
        raise ValueError(f"Configuration file not found: {file_path}")

    required = [
        "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"
    ]
    for k in required:
        if k not in raw:
            raise ValueError(f"Missing mandatory configuration key: {k}")

    try:
        width = int(raw["WIDTH"])
        height = int(raw["HEIGHT"])
        entry = _parse_xy(raw["ENTRY"])
        exit_ = _parse_xy(raw["EXIT"])
        output_file = raw["OUTPUT_FILE"]
        perfect = _parse_bool(raw["PERFECT"])
    except ValueError as e:
        raise ValueError(f"Configuration error: {e}")

    seed: Optional[int] = None
    if "SEED" in raw and raw["SEED"].strip():
        try:
            seed = int(raw["SEED"])
        except ValueError:
            # Fallback for non-integer seeds
            seed = sum(ord(c) for c in raw["SEED"])

    if width <= 0 or height <= 0:
        raise ValueError(f"WIDTH ({width}) and HEIGHT ({height}) must be > 0")
    if entry == exit_:
        raise ValueError(f"ENTRY and EXIT must be different: {entry}")

    ex, ey = entry
    xx, xy = exit_
    if not (0 <= ex < width and 0 <= ey < height):
        raise ValueError(f"ENTRY out of bounds: {entry} for {width}x{height}")
    if not (0 <= xx < width and 0 <= xy < height):
        raise ValueError(f"EXIT out of bounds: {exit_} for {width}x{height}")

    if not output_file:
        raise ValueError("OUTPUT_FILE must not be empty")

    return Config(
        width=width,
        height=height,
        entry=entry,
        exit=exit_,
        output_file=output_file,
        perfect=perfect,
        seed=seed,
    )




def main() -> None:
    """Entry point for the maze generator application."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return

    try:
        cfg = parse_config(sys.argv[1])
    except (OSError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    # --- Deterministic seed sequence ---
    # A separate Random instance (master_rng) produces a fixed sequence of
    # per-maze seeds.  This guarantees that across program restarts the
    # nth generated maze is always identical, while each successive maze
    # within a single run is still different.
    # When no seed is configured, master_rng is None and every maze is
    # purely random.
    if cfg.seed is not None:
        master_rng: Optional[random.Random] = random.Random(cfg.seed)
    else:
        master_rng = None

    def _next_seed() -> Optional[int]:
        """Return the next deterministic seed, or None for random."""
        if master_rng is not None:
            return master_rng.randint(0, 2**31)
        return None

    def _make_maze() -> tuple[MazeGenerator, Optional[str]]:
        """Build a new maze and solve it."""
        gen = MazeGenerator(
            width=cfg.width,
            height=cfg.height,
            entry=cfg.entry,
            exit=cfg.exit,
            perfect=cfg.perfect,
            seed=_next_seed(),
        )
        gen.generate()
        path = gen.solve()
        return gen, path

    try:
        gen, path_str = _make_maze()
        gen.save_maze(cfg.output_file, path_str)
        print(f"Maze successfully generated and saved to {cfg.output_file}")
    except (OSError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    if path_str is None:
        print("Warning: No path found from entry to exit!")

    renderer = MazeRenderer(gen.grid, cfg.entry, cfg.exit, gen.pattern_cells)
    renderer.set_status(gen.warning)
    renderer.set_path(path_str)

    try:
        while True:
            renderer.display()
            key = renderer.wait_key()
            if key == 'R':
                gen, path_str = _make_maze()
                gen.save_maze(cfg.output_file, path_str or "")

                renderer = MazeRenderer(
                    gen.grid, cfg.entry, cfg.exit, gen.pattern_cells
                )
                renderer.set_status(gen.warning)
                renderer.set_path(path_str)
            elif key == 'P':
                renderer.toggle_path()
            elif key == 'C':
                renderer.cycle_color()
            elif key == 'Q':
                print("Goodbye!")
                break
    except KeyboardInterrupt:
        print("\nInterrupted by user. Goodbye!")


if __name__ == "__main__":
    main()
