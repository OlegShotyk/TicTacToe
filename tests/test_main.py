"""
Unit tests for the pure game-logic pieces of TicTacToe (main.py).

These tests avoid opening any real Tkinter window: instances of TicTacToe
are built with object.__new__ (bypassing __init__, which builds GUI
widgets) and given lightweight stub buttons/labels instead.
"""
import random

import pytest

from main import TicTacToe, WIN_LINES
from tests.helpers import make_game


# ---------- check_winner ----------

class TestCheckWinner:
    @pytest.mark.parametrize("line", WIN_LINES)
    def test_detects_win_on_every_winning_line(self, line):
        board = [""] * 9
        for i in line:
            board[i] = "X"
        assert TicTacToe.check_winner(board) == line

    def test_no_winner_on_empty_board(self):
        assert TicTacToe.check_winner([""] * 9) is None

    def test_no_winner_when_line_is_mixed_marks(self):
        board = ["X", "O", "X", "", "", "", "", "", ""]
        assert TicTacToe.check_winner(board) is None

    def test_no_false_positive_on_full_board_without_winner(self):
        # X O X / X O O / O X X -> draw, no line of 3 identical marks
        board = ["X", "O", "X",
                 "X", "O", "O",
                 "O", "X", "X"]
        assert TicTacToe.check_winner(board) is None


# ---------- empty_cells ----------

class TestEmptyCells:
    def test_all_cells_empty_on_fresh_board(self):
        assert TicTacToe.empty_cells([""] * 9) == list(range(9))

    def test_only_unfilled_indices_returned(self):
        board = ["X", "", "O", "", "", "", "", "", ""]
        assert TicTacToe.empty_cells(board) == [1, 3, 4, 5, 6, 7, 8]

    def test_no_empty_cells_on_full_board(self):
        board = ["X"] * 9
        assert TicTacToe.empty_cells(board) == []


# ---------- find_winning_move ----------

class TestFindWinningMove:
    def test_finds_immediate_winning_move(self):
        game = make_game()
        # X X _ -> winning move for X is index 2
        board = ["X", "X", "", "", "", "", "", "", ""]
        assert game.find_winning_move(board, "X") == 2

    def test_returns_none_when_no_winning_move_exists(self):
        game = make_game()
        board = ["X", "O", "", "", "", "", "", "", ""]
        assert game.find_winning_move(board, "X") is None

    def test_does_not_mutate_the_board(self):
        game = make_game()
        board = ["X", "X", "", "", "", "", "", "", ""]
        game.find_winning_move(board, "X")
        assert board == ["X", "X", "", "", "", "", "", "", ""]


# ---------- choose_computer_move ----------

class TestChooseComputerMoveEasy:
    def test_returns_none_when_board_full(self):
        game = make_game(difficulty="easy", board=["X"] * 9)
        assert game.choose_computer_move() is None

    def test_returns_an_empty_cell(self):
        random.seed(0)
        board = ["X", "", "O", "", "", "", "", "", ""]
        game = make_game(difficulty="easy", board=board)
        move = game.choose_computer_move()
        assert move in TicTacToe.empty_cells(board)


class TestChooseComputerMoveMedium:
    def test_takes_winning_move_over_blocking_move(self):
        # Computer (O) can win at 5; human (X) also threatens at 6.
        board = ["O", "O", "",
                 "X", "X", "",
                 "", "", ""]
        game = make_game(difficulty="medium", human_mark="X", computer_mark="O", board=board)
        assert game.choose_computer_move() == 2

    def test_blocks_human_winning_move_when_no_win_available(self):
        # Human (X) threatens to win at 2; computer (O) has no win of its own.
        board = ["X", "X", "",
                 "O", "", "",
                 "", "", ""]
        game = make_game(difficulty="medium", human_mark="X", computer_mark="O", board=board)
        assert game.choose_computer_move() == 2

    def test_picks_random_empty_cell_when_no_win_or_block_available(self):
        board = [""] * 9
        game = make_game(difficulty="medium", human_mark="X", computer_mark="O", board=board)
        move = game.choose_computer_move()
        assert move in range(9)


class TestChooseComputerMoveHard:
    def test_takes_immediate_winning_move(self):
        board = ["O", "O", "",
                 "X", "X", "",
                 "", "", ""]
        game = make_game(difficulty="hard", human_mark="X", computer_mark="O", board=board)
        assert game.choose_computer_move() == 2

    def test_blocks_opponent_winning_move(self):
        board = ["X", "X", "",
                 "O", "", "",
                 "", "", ""]
        game = make_game(difficulty="hard", human_mark="X", computer_mark="O", board=board)
        assert game.choose_computer_move() == 2

    def test_hard_ai_never_loses_against_random_opponent(self):
        """Property test: simulate many full games, hard AI must never lose."""
        random.seed(42)
        for _ in range(30):
            game = make_game(difficulty="hard", human_mark="X", computer_mark="O",
                              board=[""] * 9, current_player="X")
            # Human (X) plays randomly, computer (O) plays hard, X starts.
            while True:
                empties = TicTacToe.empty_cells(game.board)
                if not empties:
                    break
                if game.current_player == game.human_mark:
                    move = random.choice(empties)
                else:
                    move = game.choose_computer_move()
                game.board[move] = game.current_player
                if TicTacToe.check_winner(game.board):
                    break
                game.current_player = (
                    game.human_mark if game.current_player == game.computer_mark
                    else game.computer_mark
                )

            winner_line = TicTacToe.check_winner(game.board)
            if winner_line:
                winner_mark = game.board[winner_line[0]]
                assert winner_mark != game.human_mark, (
                    "Hard AI lost a game it should never lose:\n"
                    f"{game.board[0:3]}\n{game.board[3:6]}\n{game.board[6:9]}"
                )


# ---------- minimax ----------

class TestMinimax:
    def test_takes_winning_move_when_available(self):
        board = ["O", "O", "",
                 "", "", "",
                 "", "", ""]
        game = make_game(human_mark="X", computer_mark="O")
        score, move = game.minimax(board, "O")
        assert move == 2
        assert score == 1

    def test_blocks_certain_loss(self):
        board = ["X", "X", "",
                 "", "", "",
                 "", "", ""]
        game = make_game(human_mark="X", computer_mark="O")
        score, move = game.minimax(board, "O")
        assert move == 2

    def test_returns_draw_score_for_forced_draw_position(self):
        # X O X / X O O / O X _  -> last cell forces a draw regardless of who plays it
        board = ["X", "O", "X",
                 "X", "O", "O",
                 "O", "X", ""]
        game = make_game(human_mark="X", computer_mark="O")
        score, move = game.minimax(board, "O")
        assert move == 8
        assert score == 0


# ---------- make_move (win / draw detection) ----------

class TestMakeMove:
    def test_marks_board_and_switches_player(self):
        game = make_game(mode="PVP")
        game.make_move(4)
        assert game.board[4] == "X"
        assert game.current_player == "O"
        assert game.game_over is False

    def test_detects_win_and_ends_game(self, monkeypatch):
        shown = {}
        monkeypatch.setattr(
            "main.messagebox.showinfo",
            lambda title, message: shown.setdefault("message", message),
        )
        board = ["X", "X", "",
                 "O", "O", "",
                 "", "", ""]
        game = make_game(mode="PVP", board=board, current_player="X")
        game.make_move(2)  # completes top row for X
        assert game.game_over is True
        assert "Winner" in shown["message"]

    def test_detects_draw_and_ends_game(self, monkeypatch):
        shown = {}
        monkeypatch.setattr(
            "main.messagebox.showinfo",
            lambda title, message: shown.setdefault("message", message),
        )
        # One empty cell left (index 8) that completes a draw, no winner.
        board = ["X", "O", "X",
                 "X", "O", "O",
                 "O", "X", ""]
        game = make_game(mode="PVP", board=board, current_player="X")
        game.make_move(8)
        assert game.game_over is True
        assert shown["message"] == "Draw!"

    def test_does_not_allow_move_after_game_over_via_on_click(self, monkeypatch):
        monkeypatch.setattr("main.messagebox.showinfo", lambda title, message: None)
        game = make_game(mode="PVP", board=[""] * 9)
        game.game_over = True
        game.on_click(0)
        assert game.board[0] == ""
