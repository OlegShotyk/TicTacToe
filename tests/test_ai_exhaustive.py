"""
Exhaustive verification of requirement R11: the Hard AI never loses.

Tic-tac-toe is small enough to explore every possible game, so instead of
sampling random opponents we let the "human" try every legal move at every
turn and check that no line of play ends in a human win. This is done both
when the AI moves second (plays O) and when it moves first (plays X).
"""
import pytest

from main import TicTacToe
from tests.helpers import make_game


def explore_all_games(human_mark, computer_mark):
    """Play every possible game against the Hard AI.

    Returns (games_played, human_wins, draws, computer_wins, first_losing_board).
    """
    game = make_game(difficulty="hard", human_mark=human_mark, computer_mark=computer_mark)
    ai_cache = {}  # the Hard AI is deterministic, so a board always gets the same answer
    stats = {"games": 0, "human": 0, "draw": 0, "computer": 0}
    losing_board = []

    def ai_move(board):
        key = tuple(board)
        if key not in ai_cache:
            game.board = list(board)
            ai_cache[key] = game.choose_computer_move()
        return ai_cache[key]

    def play(board, to_move):
        winner_line = TicTacToe.check_winner(board)
        if winner_line or "" not in board:
            stats["games"] += 1
            if not winner_line:
                stats["draw"] += 1
            elif board[winner_line[0]] == human_mark:
                stats["human"] += 1
                if not losing_board:
                    losing_board.extend(board)
            else:
                stats["computer"] += 1
            return

        if to_move == computer_mark:
            move = ai_move(board)
            assert board[move] == "", f"AI chose occupied cell {move} on {board}"
            board[move] = computer_mark
            play(board, human_mark)
            board[move] = ""
        else:
            for move in TicTacToe.empty_cells(board):
                board[move] = human_mark
                play(board, computer_mark)
                board[move] = ""

    play([""] * 9, "X")  # X always starts
    return stats, losing_board


def format_board(board):
    cells = [c or "." for c in board]
    return "\n".join(" ".join(cells[r * 3:r * 3 + 3]) for r in range(3))


@pytest.mark.parametrize(
    "human_mark, computer_mark",
    [("X", "O"), ("O", "X")],
    ids=["ai_moves_second", "ai_moves_first"],
)
def test_hard_ai_never_loses_any_possible_game(human_mark, computer_mark):
    stats, losing_board = explore_all_games(human_mark, computer_mark)

    assert stats["games"] > 0
    assert stats["human"] == 0, (
        f"Hard AI lost {stats['human']} of {stats['games']} games, e.g.:\n"
        + format_board(losing_board)
    )
    # Sanity check that the exploration really branched over human choices.
    assert stats["draw"] + stats["computer"] == stats["games"]
    assert stats["games"] > 50
