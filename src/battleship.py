"""Punto di ingresso di Battleship."""

from battleship_game.app import BattleshipApp


def main() -> None:
    """Avvia il gioco."""
    BattleshipApp().run()


if __name__ == "__main__":
    main()
