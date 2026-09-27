"""
Regression tests for confirmed, still-open bugs.

They run against a real (hidden) Tk window because the bugs are about timing
between Tk callbacks. Each test is marked xfail(strict=True): it is expected to
fail while the bug exists, and the suite turns red as soon as the bug is fixed,
reminding us to remove the marker and close the issue. raises=AssertionError
makes sure that only the known symptom counts as the expected failure; any
other exception (e.g. a crash while starting the game) fails the test.
"""
import pytest

from tests.helpers import pump_events


def start_vs_computer(game, first="human"):
    game.mode_var.set("PVC")
    game.difficulty_var.set("easy")
    game.first_var.set(first)
    game.start_game()


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="Bug #1: pending computer move is not cancelled on New game")
def test_new_game_during_computer_delay_leaves_board_empty(app):
    root, game, _ = app
    start_vs_computer(game)
    game.buttons[0].invoke()  # human plays X; computer reply scheduled in 400 ms
    game.reset()              # user clicks "New game" before the reply

    pump_events(root, 700)

    assert game.board == [""] * 9
    assert game.current_player == game.human_mark


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="Bug #2: pending computer move fires after returning to Menu")
def test_menu_during_computer_delay_raises_no_error(app):
    root, game, callback_errors = app
    start_vs_computer(game)
    game.buttons[0].invoke()
    game.build_menu()         # user clicks "Menu" before the reply

    pump_events(root, 700)

    assert callback_errors == []
