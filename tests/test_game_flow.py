"""
Unit tests for game flow: status line, end-of-round messages, who moves first,
click handling, computer turn scheduling and the menu's option toggling.

All GUI objects are stubs (see tests/helpers.py), so no window is opened.
"""
import tkinter as tk

import pytest

from tests.helpers import StubWidget, make_game


@pytest.fixture
def popups(monkeypatch):
    """Capture messagebox.showinfo calls instead of opening a dialog."""
    shown = []
    monkeypatch.setattr(
        "main.messagebox.showinfo",
        lambda title, message: shown.append((title, message)),
    )
    return shown


def win_top_row_for(game, mark):
    """Put two of `mark` on the top row so that index 2 wins."""
    game.board[0] = game.board[1] = mark
    game.current_player = mark


# ---------- update_status (R5) ----------

class TestUpdateStatus:
    def test_pvp_shows_whose_turn(self):
        game = make_game(mode="PVP", current_player="O")
        game.update_status()
        assert game.status_label.last("text") == "Player's turn: O"

    def test_pvc_human_turn(self):
        game = make_game(mode="PVC", human_mark="X", computer_mark="O", current_player="X")
        game.update_status()
        assert game.status_label.last("text") == "Your turn (X)"

    def test_pvc_computer_turn(self):
        game = make_game(mode="PVC", human_mark="X", computer_mark="O", current_player="O")
        game.update_status()
        assert game.status_label.last("text") == "Computer's turn... (O)"


# ---------- end of round (R3, R4, R6) ----------

class TestEndOfRound:
    @pytest.mark.parametrize("mark", ["X", "O"])
    def test_pvp_win_announces_winning_mark(self, popups, mark):
        game = make_game(mode="PVP")
        win_top_row_for(game, mark)
        game.make_move(2)
        assert popups == [("Game over", f"Winner: {mark}")]
        assert game.status_label.last("text") == f"Winner: {mark}"

    @pytest.mark.parametrize("human_mark, computer_mark", [("X", "O"), ("O", "X")])
    def test_pvc_human_win(self, popups, human_mark, computer_mark):
        game = make_game(mode="PVC", human_mark=human_mark, computer_mark=computer_mark)
        win_top_row_for(game, human_mark)
        game.make_move(2)
        assert popups == [("Game over", "You win!")]
        assert game.status_label.last("text") == "You win!"

    @pytest.mark.parametrize("human_mark, computer_mark", [("X", "O"), ("O", "X")])
    def test_pvc_computer_win(self, popups, human_mark, computer_mark):
        game = make_game(mode="PVC", human_mark=human_mark, computer_mark=computer_mark)
        win_top_row_for(game, computer_mark)
        game.make_move(2)
        assert popups == [("Game over", "The computer wins!")]

    @pytest.mark.parametrize("mode", ["PVP", "PVC"])
    def test_draw_message_in_both_modes(self, popups, mode):
        board = ["X", "O", "X",
                 "X", "O", "O",
                 "O", "X", ""]
        game = make_game(mode=mode, board=board, current_player="X")
        game.make_move(8)
        assert popups == [("Game over", "Draw!")]

    def test_winning_line_is_highlighted(self, popups):
        game = make_game(mode="PVP")
        win_top_row_for(game, "X")
        game.make_move(2)
        for i in range(9):
            expected = "lightgreen" if i in (0, 1, 2) else None
            assert game.buttons[i].last("bg") == expected

    def test_popup_shown_exactly_once_per_round(self, popups):
        game = make_game(mode="PVP")
        win_top_row_for(game, "X")
        game.make_move(2)
        game.on_click(5)  # clicks after the round ended are ignored
        assert len(popups) == 1


# ---------- make_move rendering (R1) ----------

class TestMakeMoveRendering:
    @pytest.mark.parametrize("mark, colour", [("X", "blue"), ("O", "red")])
    def test_mark_drawn_on_button_in_its_colour(self, mark, colour):
        game = make_game(current_player=mark)
        game.make_move(4)
        assert game.buttons[4].last("text") == mark
        assert game.buttons[4].last("fg") == colour

    def test_players_alternate(self):
        game = make_game()
        played = []
        for cell in (0, 4, 8):
            played.append(game.current_player)
            game.make_move(cell)
        assert played == ["X", "O", "X"]


# ---------- setup_new_round / who goes first (R8, R12) ----------

class TestSetupNewRound:
    def test_resets_board_and_buttons(self):
        game = make_game(board=["X", "O", "X", "", "", "", "", "", ""])
        game.game_over = True
        game.setup_new_round()
        assert game.board == [""] * 9
        assert game.game_over is False
        for btn in game.buttons:
            assert btn.last("text") == ""
            assert btn.last("state") == tk.NORMAL

    def test_pvc_human_first_plays_x_and_nothing_is_scheduled(self):
        game = make_game(mode="PVC", first="human")
        game.setup_new_round()
        assert (game.human_mark, game.computer_mark) == ("X", "O")
        assert game.current_player == "X"
        assert game.root.scheduled == []
        assert game.status_label.last("text") == "Your turn (X)"

    def test_pvc_computer_first_plays_x_and_moves_automatically(self):
        game = make_game(mode="PVC", first="computer")
        game.setup_new_round()
        assert (game.human_mark, game.computer_mark) == ("O", "X")
        assert game.current_player == "X"
        assert game.root.scheduled == [(400, game.computer_move)]
        assert game.status_label.last("text") == "Computer's turn... (X)"

    def test_pvp_ignores_who_goes_first_setting(self):
        game = make_game(mode="PVP", first="computer")
        game.setup_new_round()
        assert game.current_player == "X"
        assert game.root.scheduled == []
        assert game.status_label.last("text") == "Player's turn: X"

    def test_reset_starts_a_new_round(self):
        game = make_game(board=["X"] * 9)
        game.reset()
        assert game.board == [""] * 9


# ---------- on_click (R2, R13) ----------

class TestOnClick:
    def test_occupied_cell_cannot_be_overwritten(self):
        game = make_game(mode="PVP", board=["O", "", "", "", "", "", "", "", ""])
        game.on_click(0)
        assert game.board[0] == "O"
        assert game.current_player == "X"

    def test_pvc_human_move_schedules_computer_reply(self):
        game = make_game(mode="PVC")
        game.on_click(4)
        assert game.board[4] == "X"
        assert game.root.scheduled == [(400, game.computer_move)]

    def test_pvc_click_ignored_during_computers_turn(self):
        game = make_game(mode="PVC", current_player="O")
        game.on_click(4)
        assert game.board == [""] * 9

    def test_pvc_no_computer_reply_after_human_wins(self, popups):
        game = make_game(mode="PVC")
        win_top_row_for(game, "X")
        game.on_click(2)
        assert game.game_over is True
        assert game.root.scheduled == []

    def test_pvp_never_schedules_computer(self):
        game = make_game(mode="PVP")
        game.on_click(4)
        game.on_click(0)
        assert game.root.scheduled == []


# ---------- computer_move ----------

class TestComputerMove:
    def test_places_computer_mark_and_hands_turn_back(self):
        game = make_game(mode="PVC", difficulty="hard", current_player="O",
                         board=["X", "", "", "", "", "", "", "", ""])
        game.computer_move()
        assert game.board.count("O") == 1
        assert game.current_player == "X"

    def test_does_nothing_after_game_over(self):
        game = make_game(mode="PVC", current_player="O")
        game.game_over = True
        game.computer_move()
        assert game.board == [""] * 9


# ---------- menu option toggling (R7) ----------

class TestModeChange:
    @pytest.fixture
    def game(self):
        game = make_game()
        game.difficulty_buttons = [StubWidget() for _ in range(3)]
        game.first_buttons = [StubWidget() for _ in range(2)]
        return game

    @pytest.mark.parametrize("mode, state", [("PVC", tk.NORMAL), ("PVP", tk.DISABLED)])
    def test_computer_options_enabled_only_against_computer(self, game, mode, state):
        game.mode_var.set(mode)
        game.on_mode_change()
        for rb in game.difficulty_buttons + game.first_buttons:
            assert rb.last("state") == state
