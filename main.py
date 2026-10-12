import pygame

from ui.application import Application


def main() -> None:
    """Start the Fly-In application and handle runtime interruptions."""
    app: Application | None = None

    try:
        app = Application()
        app.run()
    except KeyboardInterrupt:
        if app is not None:
            app._running = False

        try:
            pygame.quit()
        except Exception:
            pass

        print("\nSimulation interrupted by user.")
    except Exception as exc:
        try:
            pygame.quit()
        except Exception:
            pass

        print(f"\nThe simulation could not start correctly: {exc}")


if __name__ == "__main__":
    main()
