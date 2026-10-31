"""Stato e regole di una partita di Sudoku (nessuna dipendenza UI)."""

import numpy as np

from sudoku_game.config import GRID_SIZE, INITIAL_LIVES
from sudoku_game.engine import Board


class GameState:  # pylint: disable=too-many-instance-attributes
    """Stato della partita corrente e operazioni consentite su di esso.

    Raccoglie i dati di una singola partita (griglie, vite, note, selezione):
    il numero di attributi è intrinseco al dominio.
    """

    def __init__(self, solution: Board, grid: Board, difficulty_label: str) -> None:
        self.solution = solution
        self.grid = grid
        self.notes: list[list[set[int]]] = [
            [set() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)
        ]
        self.is_fixed = grid != 0
        self.selected = [GRID_SIZE // 2, GRID_SIZE // 2]
        self.won = False
        self.game_over = False
        self.lives = INITIAL_LIVES
        self.note_mode = False
        self.difficulty_label = difficulty_label

    @property
    def finished(self) -> bool:
        """True se la partita è vinta o persa."""
        return self.won or self.game_over

    def move_selection(self, d_row: int, d_col: int) -> None:
        """Sposta la selezione (con avvolgimento ai bordi)."""
        self.selected[0] = (self.selected[0] + d_row) % GRID_SIZE
        self.selected[1] = (self.selected[1] + d_col) % GRID_SIZE

    def toggle_note_mode(self) -> None:
        """Attiva/disattiva la modalità annotazione."""
        self.note_mode = not self.note_mode

    def erase_selected(self) -> None:
        """Cancella la cella selezionata se non è un numero fisso."""
        row, col = self.selected
        if not self.is_fixed[row, col]:
            self.grid[row, col] = 0
            self.notes[row][col].clear()

    def input_number(self, value: int) -> None:
        """Inserisce un numero (o una nota) nella cella selezionata."""
        row, col = self.selected
        if self.is_fixed[row, col] or self.grid[row, col] == value:
            return
        if self.note_mode:
            self.notes[row][col] ^= {value}
            return
        self.grid[row, col] = value
        self.notes[row][col].clear()
        if value != self.solution[row, col]:
            self.lives -= 1
            self.game_over = self.lives <= 0
        elif np.array_equal(self.grid, self.solution):
            self.won = True
