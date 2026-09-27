"""
Property-based tests (Hypothesis): instead of hand-picked boards, generate
many random *reachable* positions and check rules that must always hold.
"""
from hypothesis import given, settings
from hypothesis import strategies as st

from main import TicTacToe, WIN_LINES
from tests.helpers import make_game


@st.composite
def game_positions(draw, allow_finished=True, min_moves=0):
    """A position reachable by legal play: X starts, marks alternate,
    play stops as soon as someone wins. Returns (board, player_to_move)."""
    order = draw(st.permutations(range(9)))
    n_moves = draw(st.integers(min_value=min_moves, max_value=9))
    board = [""] * 9
    player = "X"
    for cell in order[:n_moves]:
        board[cell] = player
        finished = TicTacToe.check_winner(board) or "" not in board
        if finished and not allow_finished:
            board[cell] = ""  # stop one move before the game ends
            break
        player = "O" if player == "X" else "X"
        if finished:
            break
    return board, player


def winning_cells(board, mark):
    return {i for i in TicTacToe.empty_cells(board)
            if TicTacToe.check_winner(board[:i] + [mark] + board[i + 1:])}


@given(game_positions())
def test_empty_cells_are_exactly_the_unmarked_cells(position):
    board, _ = position
    empty = TicTacToe.empty_cells(board)
    assert empty == sorted(empty)
    assert set(empty) == {i for i in range(9) if board[i] == ""}


@given(game_positions())
def test_check_winner_returns_a_real_line_of_one_mark(position):
    board, _ = position
    line = TicTacToe.check_winner(board)
    if line is not None:
        assert line in WIN_LINES
        assert board[line[0]] in ("X", "O")
        assert board[line[0]] == board[line[1]] == board[line[2]]


@given(game_positions(), st.sampled_from(["X", "O"]))
def test_find_winning_move_is_correct_and_side_effect_free(position, mark):
    board, _ = position
    before = list(board)
    move = make_game().find_winning_move(board, mark)
    assert board == before
    if move is None:
        assert winning_cells(board, mark) == set()
    else:
        assert move in winning_cells(board, mark)


@settings(max_examples=60, deadline=None)  # hard difficulty runs full minimax
@given(game_positions(allow_finished=False), st.sampled_from(["easy", "medium", "hard"]))
def test_computer_always_picks_an_empty_cell(position, difficulty):
    board, to_move = position
    human = "O" if to_move == "X" else "X"
    game = make_game(difficulty=difficulty, board=list(board),
                     human_mark=human, computer_mark=to_move, current_player=to_move)
    move = game.choose_computer_move()
    assert move in TicTacToe.empty_cells(board)
    assert game.board == board  # choosing a move must not change the real board


# A win or a threat needs at least two marks of one player, i.e. 3+ moves.
@settings(deadline=None)
@given(game_positions(allow_finished=False, min_moves=3))
def test_medium_wins_when_it_can_and_blocks_otherwise(position):
    """R10: take a win if one exists; otherwise block the opponent's
    immediate win (when there is exactly one to block)."""
    board, to_move = position
    human = "O" if to_move == "X" else "X"
    game = make_game(difficulty="medium", board=list(board),
                     human_mark=human, computer_mark=to_move)
    move = game.choose_computer_move()

    own_wins = winning_cells(board, to_move)
    threats = winning_cells(board, human)
    if own_wins:
        assert move in own_wins
    elif len(threats) == 1:
        assert move in threats


@settings(deadline=None)
@given(game_positions(allow_finished=False, min_moves=3))
def test_hard_keeps_the_best_achievable_result(position):
    """R11: Hard plays optimally - its move keeps the best result the
    position allows. In particular it never throws away a win and always
    blocks an immediate threat unless the position is already lost.

    (A lost position - e.g. the opponent already has a fork - can only be
    generated here, never reached in a real game against Hard, as proven by
    test_ai_exhaustive.py. There every move loses and Hard picks the first.)"""
    board, to_move = position
    human = "O" if to_move == "X" else "X"
    game = make_game(difficulty="hard", board=list(board),
                     human_mark=human, computer_mark=to_move)
    move = game.choose_computer_move()

    best_value, _ = game.minimax(list(board), to_move)
    after = board[:move] + [to_move] + board[move + 1:]
    move_value, _ = game.minimax(after, human)
    assert move_value == best_value

    own_wins = winning_cells(board, to_move)
    threats = winning_cells(board, human)
    if own_wins:
        assert move_value == 1
    elif len(threats) == 1 and best_value > -1:
        assert move in threats
