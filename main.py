import pygame

from ui.application import Application


def main() -> None:
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


if __name__ == "__main__":
    main()
