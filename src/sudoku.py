"""Punto di ingresso del Sudoku."""

from __future__ import annotations

from sudoku_game.app import SudokuGame


def main() -> None:
    """Avvia il gioco."""
    SudokuGame().run()


if __name__ == "__main__":
    main()
