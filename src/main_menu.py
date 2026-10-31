"""Punto di ingresso del menu principale."""

from menu.app import OfflineGames


def main() -> None:
    """Avvia il menu."""
    OfflineGames().start_engine()


if __name__ == "__main__":
    main()
