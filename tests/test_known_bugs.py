"""
Regression tests for confirmed, still-open bugs.

They run against a real (hidden) Tk window because the bugs are about timing
between Tk callbacks. Each test is marked xfail(strict=True): it is expected to
fail while the bug exists, and the suite turns red as soon as the bug is fixed,
reminding us to remove the marker and close the issue.
"""
import time
import tkinter as tk

import pytest

import main


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr(main.messagebox, "showinfo", lambda *a, **k: None)
    try:
        root = tk.Tk()
    except tk.TclError as exc:  # e.g. CI machine without a display
        pytest.skip(f"Tk is not available: {exc}")
    root.withdraw()
    callback_errors = []
    root.report_callback_exception = lambda exc_type, exc, tb: callback_errors.append(exc)
    game = main.TicTacToe(root)
    yield root, game, callback_errors
    root.destroy()


def pump_events(root, ms):
    """Process Tk events for `ms` milliseconds so after() callbacks can fire."""
    end = time.monotonic() + ms / 1000
    while time.monotonic() < end:
        root.update()
        time.sleep(0.01)


def start_vs_computer(game, first="human"):
    game.mode_var.set("PVC")
    game.difficulty_var.set("easy")
    game.first_var.set(first)
    game.start_game()


@pytest.mark.xfail(strict=True, reason="Bug #1: pending computer move is not cancelled on New game")
def test_new_game_during_computer_delay_leaves_board_empty(app):
    root, game, _ = app
    start_vs_computer(game)
    game.buttons[0].invoke()  # human plays X; computer reply scheduled in 400 ms
    game.reset()              # user clicks "New game" before the reply

    pump_events(root, 700)

    assert game.board == [""] * 9
    assert game.current_player == game.human_mark


@pytest.mark.xfail(strict=True, reason="Bug #2: pending computer move fires after returning to Menu")
def test_menu_during_computer_delay_raises_no_error(app):
    root, game, callback_errors = app
    start_vs_computer(game)
    game.buttons[0].invoke()
    game.build_menu()         # user clicks "Menu" before the reply

    pump_events(root, 700)

    assert callback_errors == []
