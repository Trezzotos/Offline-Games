"""Punto di ingresso di Battleship."""

from __future__ import annotations

from battleship_game.app import BattleshipApp


def main() -> None:
    """Avvia il gioco."""
    BattleshipApp().run()


if __name__ == "__main__":
    main()
