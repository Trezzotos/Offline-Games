"""Regole e stato di una partita di Battleship (logica pura, senza Pygame)."""

from __future__ import annotations

import random
from enum import Enum

from battleship_game.ai import HuntTargetStrategy, ShootingStrategy
from battleship_game.config import FLEET_SIZES, Coord
from battleship_game.model import Board, Orientation, ShotResult
from battleship_game.placement import FleetPlacer, RandomFleetPlacer


class Phase(Enum):
    """Fasi della partita."""

    PLACEMENT = "placement"
    BATTLE = "battle"
    GAME_OVER = "game_over"


class BattleshipGame:
    """Gestisce piazzamento, turni e condizioni di vittoria."""

    WIN_TEXT = "YOU WIN!"
    LOSE_TEXT = "YOU LOSE!"

    def __init__(
        self,
        placer: FleetPlacer | None = None,
        strategy: ShootingStrategy | None = None,
        rng: random.Random | None = None,
    ) -> None:
        rng = rng or random.Random()
        self._placer = placer or RandomFleetPlacer(rng)
        self._strategy = strategy or HuntTargetStrategy(rng)
        self.player_board = Board(FLEET_SIZES)
        self.enemy_board = Board(FLEET_SIZES)
        self.orientation = Orientation.HORIZONTAL
        self.player_turn = True
        self.winner_text = ""
        self._placer.place_fleet(self.enemy_board)

    # --- Stato -----------------------------------------------------------
    @property
    def ships_placed(self) -> int:
        """Numero di navi del giocatore già posizionate."""
        return self.player_board.placed_count

    @property
    def phase(self) -> Phase:
        """Fase corrente della partita."""
        if self.winner_text:
            return Phase.GAME_OVER
        if self.ships_placed < len(self.player_board.ships):
            return Phase.PLACEMENT
        return Phase.BATTLE

    @property
    def is_game_over(self) -> bool:
        """True se la partita è conclusa."""
        return self.phase is Phase.GAME_OVER

    @property
    def is_enemy_turn(self) -> bool:
        """True se il nemico deve ancora sparare."""
        return not self.player_turn and not self.is_game_over

    @property
    def current_ship_length(self) -> int | None:
        """Lunghezza della nave da piazzare (None a piazzamento concluso)."""
        if self.ships_placed >= len(self.player_board.ships):
            return None
        return self.player_board.ships[self.ships_placed].dimension

    @property
    def player_lives(self) -> int:
        """Celle di nave ancora integre del giocatore."""
        return self.player_board.remaining_ship_cells

    @property
    def enemy_lives(self) -> int:
        """Celle di nave ancora integre del nemico."""
        return self.enemy_board.remaining_ship_cells

    # --- Azioni del giocatore ----------------------------------------------
    def rotate(self) -> None:
        """Ruota la nave in fase di piazzamento."""
        self.orientation = self.orientation.toggled()

    def can_place_current(self, row: int, col: int) -> bool:
        """True se la nave corrente può essere posata in (row, col)."""
        length = self.current_ship_length
        if length is None:
            return False
        return self.player_board.can_place(row, col, length, self.orientation)

    def place_current_ship(self, row: int, col: int) -> bool:
        """Posa la nave corrente; restituisce True se il piazzamento riesce."""
        if self.phase is not Phase.PLACEMENT:
            return False
        if not self.player_board.place_ship(
            self.ships_placed, row, col, self.orientation
        ):
            return False
        return True

    def player_shoot(self, row: int, col: int) -> ShotResult | None:
        """Il giocatore spara sulla plancia nemica (None se il colpo non è valido)."""
        if self.phase is not Phase.BATTLE or not self.player_turn:
            return None
        if not self.enemy_board.in_bounds(row, col):
            return None
        if self.enemy_board.cell(row, col).is_hit:
            return None
        result = self.enemy_board.receive_shot(row, col)
        if result.hit:
            if self.enemy_board.all_sunk():
                self.winner_text = self.WIN_TEXT
        else:
            self.player_turn = False
        return result

    # --- Turno nemico --------------------------------------------------------
    def enemy_shoot(self) -> ShotResult | None:
        """Il nemico spara sulla plancia del giocatore."""
        shot = self._strategy.choose_shot(self.player_board)
        if shot is None:
            self.player_turn = True
            return None
        result = self.player_board.receive_shot(*shot)
        self._strategy.record_result(result)
        if not result.hit:
            self.player_turn = True
        elif self.player_board.all_sunk():
            self.winner_text = self.LOSE_TEXT
            self.player_turn = True
        return result

    # --- Utilità ---------------------------------------------------------------
    def preview_cells(self, row: int, col: int) -> tuple[list[Coord], bool]:
        """Celle di anteprima della nave corrente e relativa validità."""
        length = self.current_ship_length
        if length is None or not self.player_board.in_bounds(row, col):
            return [], False
        cells = [
            (r, c)
            for r, c in self.orientation.cells(row, col, length)
            if self.player_board.in_bounds(r, c)
        ]
        return cells, self.can_place_current(row, col)

    def reset(self) -> None:
        """Avvia una nuova partita."""
        self.player_board = Board(FLEET_SIZES)
        self.enemy_board = Board(FLEET_SIZES)
        self.orientation = Orientation.HORIZONTAL
        self.player_turn = True
        self.winner_text = ""
        self._strategy.reset()
        self._placer.place_fleet(self.enemy_board)
