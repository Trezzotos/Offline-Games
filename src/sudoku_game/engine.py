"""Motore logico del Sudoku: generazione e risoluzione (nessuna dipendenza UI)."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

import numpy as np

from sudoku_game.config import BOX_SIZE, DEFAULT_REMOVED_CELLS, DIFFICULTIES, GRID_SIZE

if TYPE_CHECKING:
    import numpy.typing as npt

    Board = npt.NDArray[np.int8]
else:  # a runtime serve solo il nome: nessuna dipendenza da numpy.typing
    Board = np.ndarray


class SudokuEngine:
    """Genera e risolve griglie Sudoku."""

    @staticmethod
    def find_empty(board: Board) -> tuple[int, int] | None:
        """Trova la prima cella vuota nella griglia."""
        empties = np.argwhere(board == 0)
        if empties.size == 0:
            return None
        row, col = empties[0]
        return int(row), int(col)

    @staticmethod
    def is_valid(board: Board, row: int, col: int, num: int) -> bool:
        """Verifica se l'inserimento rispetta le regole di riga, colonna e box."""
        if num in board[row, :] or num in board[:, col]:
            return False
        r_s, c_s = (row // BOX_SIZE) * BOX_SIZE, (col // BOX_SIZE) * BOX_SIZE
        return num not in board[r_s : r_s + BOX_SIZE, c_s : c_s + BOX_SIZE]

    def solve(self, board: Board) -> bool:
        """Risolve la griglia con backtracking (ordine dei numeri casuale)."""
        empty = self.find_empty(board)
        if empty is None:
            return True
        row, col = empty
        for num in np.random.permutation(range(1, GRID_SIZE + 1)):
            if self.is_valid(board, row, col, int(num)):
                board[row, col] = num
                if self.solve(board):
                    return True
                board[row, col] = 0
        return False

    def generate_puzzle(self, difficulty: str) -> tuple[Board, Board]:
        """Restituisce (soluzione, schema di gioco) per la difficoltà richiesta."""
        board: Board = np.zeros((GRID_SIZE, GRID_SIZE), dtype="int8")
        self.solve(board)
        full_board = board.copy()
        attempts = DIFFICULTIES.get(difficulty, DEFAULT_REMOVED_CELLS)
        while attempts > 0:
            i, j = random.randint(0, 8), random.randint(0, 8)
            if board[i, j] != 0:
                board[i, j] = 0
                attempts -= 1
        return full_board, board
