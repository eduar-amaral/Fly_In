from __future__ import annotations

import sys
from pathlib import Path

from simulation.runner import TerminalRunner


def main() -> None:
    """Choose the execution mode based on the provided CLI arguments."""
    if len(sys.argv) == 1:
        from ui.application import GuiRunner

        GuiRunner().run()
        return

    map_path = Path(sys.argv[1])

    if not map_path.exists():
        raise SystemExit(f"Map not found: {map_path}")

    try:
        TerminalRunner(map_path).run()
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
    except Exception as exc:
        print(f"\nThe simulation could not start correctly: {exc}")


if __name__ == "__main__":
    main()
