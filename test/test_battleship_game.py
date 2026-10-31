"""Test delle regole di gioco di Battleship."""

import random
from collections.abc import Sequence

from battleship_game.game import BattleshipGame, Phase
from battleship_game.model import Orientation, ShotResult


class FixedStrategy:
    """Strategia di tiro deterministica per i test."""

    def __init__(self, shots: Sequence[tuple[int, int] | None]) -> None:
        self.shots = list(shots)
        self.results: list[ShotResult] = []
        self.reset_calls = 0

    def choose_shot(self, _board: object) -> tuple[int, int] | None:
        """Restituisce il prossimo colpo programmato."""
        return self.shots.pop(0)

    def record_result(self, result: ShotResult) -> None:
        """Memorizza l'esito."""
        self.results.append(result)

    def reset(self) -> None:
        """Conta i reset."""
        self.reset_calls += 1


def place_all(game: BattleshipGame) -> None:
    """Piazza tutte le navi del giocatore in righe separate."""
    for row in range(5):
        assert game.place_current_ship(row * 2, 0)


def test_initial_state() -> None:
    """Stato iniziale: piazzamento, 16 vite, nemico già piazzato."""
    game = BattleshipGame(rng=random.Random(1))
    assert game.phase is Phase.PLACEMENT
    assert game.player_lives == 16 and game.enemy_lives == 16
    assert game.current_ship_length == 2
    assert game.player_turn and not game.is_enemy_turn
    assert sum(c.has_ship for r in game.enemy_board.grid for c in r) == 16


def test_rotate_and_place_ships() -> None:
    """La rotazione cambia orientamento; il piazzamento avanza fino alla battaglia."""
    game = BattleshipGame(rng=random.Random(1))
    game.rotate()
    assert game.orientation is Orientation.VERTICAL
    game.rotate()
    place_all(game)
    assert game.phase is Phase.BATTLE
    assert game.current_ship_length is None
    assert not game.can_place_current(0, 5)
    assert not game.place_current_ship(0, 5)


def test_invalid_placement_is_rejected() -> None:
    """Posizioni fuori plancia o sovrapposte vengono rifiutate."""
    game = BattleshipGame(rng=random.Random(1))
    assert not game.place_current_ship(0, 9)
    assert game.place_current_ship(0, 0)
    assert not game.can_place_current(0, 1)
    assert game.ships_placed == 1


def test_preview_cells() -> None:
    """Anteprima: celle visibili e validità."""
    game = BattleshipGame(rng=random.Random(1))
    assert game.preview_cells(0, 0) == ([(0, 0), (0, 1)], True)
    assert game.preview_cells(0, 9) == ([(0, 9)], False)
    assert game.preview_cells(-1, 0) == ([], False)
    place_all(game)
    assert game.preview_cells(0, 0) == ([], False)


def test_player_shoot_requires_battle_phase_and_turn() -> None:
    """Non si può sparare durante il piazzamento né fuori turno."""
    game = BattleshipGame(rng=random.Random(1))
    assert game.player_shoot(0, 0) is None
    place_all(game)
    game.player_turn = False
    assert game.player_shoot(0, 0) is None


def test_player_miss_passes_turn_and_repeated_cell_rejected() -> None:
    """Un colpo a vuoto passa il turno; un colpo ripetuto o fuori griglia è ignorato."""
    game = BattleshipGame(rng=random.Random(1))
    place_all(game)
    row, col = next(
        (r, c)
        for r in range(10)
        for c in range(10)
        if not game.enemy_board.cell(r, c).has_ship
    )
    result = game.player_shoot(row, col)
    assert result is not None and not result.hit
    assert game.is_enemy_turn
    game.player_turn = True
    assert game.player_shoot(row, col) is None
    assert game.player_shoot(10, 10) is None


def test_player_hit_keeps_turn_and_wins() -> None:
    """Colpire tiene il turno; affondare tutto vince."""
    game = BattleshipGame(rng=random.Random(1))
    place_all(game)
    targets = [
        (r, c)
        for r in range(10)
        for c in range(10)
        if game.enemy_board.cell(r, c).has_ship
    ]
    for coord in targets[:-1]:
        result = game.player_shoot(*coord)
        assert result is not None and result.hit
        assert game.player_turn
    assert game.phase is Phase.BATTLE
    game.player_shoot(*targets[-1])
    assert game.is_game_over
    assert game.winner_text == BattleshipGame.WIN_TEXT
    assert game.enemy_lives == 0


def test_enemy_shoot_miss_returns_turn_to_player() -> None:
    """Il nemico a vuoto restituisce il turno."""
    strategy = FixedStrategy([(9, 9)])
    game = BattleshipGame(strategy=strategy, rng=random.Random(1))
    place_all(game)
    game.player_turn = False
    result = game.enemy_shoot()
    assert result is not None and not result.hit
    assert game.player_turn
    assert strategy.results == [result]


def test_enemy_hit_keeps_turn_then_wins() -> None:
    """Il nemico a segno continua; affondare l'intera flotta causa la sconfitta."""
    strategy = FixedStrategy([(0, 0)])
    game = BattleshipGame(strategy=strategy, rng=random.Random(1))
    place_all(game)
    game.player_turn = False
    game.enemy_shoot()
    assert game.is_enemy_turn
    assert not game.is_game_over

    remaining = [
        (r * 2, c)
        for r in range(5)
        for c in range(5)
        if c < game.player_board.ships[r].dimension
    ]
    remaining.remove((0, 0))
    strategy.shots = list(remaining)
    while not game.is_game_over:
        game.enemy_shoot()
    assert game.winner_text == BattleshipGame.LOSE_TEXT
    assert game.player_turn


def test_enemy_without_targets_passes_turn() -> None:
    """Senza bersagli il turno torna al giocatore."""
    game = BattleshipGame(strategy=FixedStrategy([None]), rng=random.Random(1))
    place_all(game)
    game.player_turn = False
    assert game.enemy_shoot() is None
    assert game.player_turn


def test_reset_restores_initial_state() -> None:
    """Il reset riporta tutto allo stato iniziale e resetta la strategia."""
    strategy = FixedStrategy([])
    game = BattleshipGame(strategy=strategy, rng=random.Random(1))
    place_all(game)
    game.winner_text = "X"
    game.player_turn = False
    game.rotate()
    game.reset()
    assert game.phase is Phase.PLACEMENT
    assert game.ships_placed == 0 and game.player_turn
    assert game.orientation is Orientation.HORIZONTAL
    assert game.winner_text == ""
    assert game.player_lives == 16 and game.enemy_lives == 16
    assert strategy.reset_calls == 1
