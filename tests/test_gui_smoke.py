"""
GUI smoke tests: drive the real Tk widgets (hidden window) through the main
user journeys, pressing buttons found by their visible text. They run on every
OS in CI and are the check for platform-specific problems such as bug #4.
"""
import tkinter as tk

import pytest

from tests.helpers import pump_events


def find_widget(parent, text, widget_class=tk.Button):
    """Depth-first search for a widget of `widget_class` with the given text."""
    for child in parent.winfo_children():
        if isinstance(child, widget_class) and child.cget("text") == text:
            return child
        found = find_widget(child, text, widget_class)
        if found is not None:
            return found
    return None


def click(root, text, widget_class=tk.Button):
    widget = find_widget(root, text, widget_class)
    assert widget is not None, f"No {widget_class.__name__} with text {text!r}"
    widget.invoke()
    root.update()


def test_menu_shows_all_options(app):
    root, _, _ = app
    for text in ["Two players", "Vs. computer", "Easy", "Medium", "Hard",
                 "Me (X)", "Computer (X)"]:
        assert find_widget(root, text, tk.Radiobutton) is not None, text
    assert find_widget(root, "Start game") is not None


def test_two_players_full_round_and_new_game(app):
    root, game, errors = app
    click(root, "Two players", tk.Radiobutton)
    click(root, "Start game")
    assert game.status_label.cget("text") == "Player's turn: X"

    for cell in (0, 3, 1, 4, 2):  # X wins on the top row
        game.buttons[cell].invoke()
    assert game.status_label.cget("text") == "Winner: X"
    assert game.buttons[0].cget("bg") == "lightgreen"

    click(root, "New game")  # restores the default button colour (bug #4 area)
    assert game.board == [""] * 9
    assert all(b.cget("text") == "" for b in game.buttons)
    assert errors == []


@pytest.mark.parametrize("difficulty", ["Easy", "Medium", "Hard"])
def test_vs_computer_computer_moves_first(app, difficulty):
    root, game, errors = app
    click(root, "Vs. computer", tk.Radiobutton)
    click(root, difficulty, tk.Radiobutton)
    click(root, "Computer (X)", tk.Radiobutton)
    click(root, "Start game")

    pump_events(root, 1500)  # 400 ms delay + Hard's first-move search

    assert game.board.count("X") == 1
    assert game.status_label.cget("text") == "Your turn (O)"
    assert errors == []


def test_vs_computer_human_move_gets_a_reply(app):
    root, game, errors = app
    click(root, "Vs. computer", tk.Radiobutton)
    click(root, "Me (X)", tk.Radiobutton)
    click(root, "Start game")

    game.buttons[4].invoke()
    pump_events(root, 700)

    assert game.board.count("X") == 1
    assert game.board.count("O") == 1
    assert errors == []


def test_menu_button_returns_to_menu(app):
    root, _, errors = app
    click(root, "Start game")
    pump_events(root, 100)
    click(root, "Menu")
    assert find_widget(root, "Start game") is not None
    assert find_widget(root, "New game") is None
    assert errors == []
