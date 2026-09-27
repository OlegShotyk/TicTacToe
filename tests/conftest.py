import tkinter as tk

import pytest

import main


@pytest.fixture
def app(monkeypatch):
    """A real TicTacToe app in a hidden Tk window.

    Yields (root, game, callback_errors); exceptions raised inside Tk
    callbacks are collected in callback_errors instead of being printed.
    """
    monkeypatch.setattr(main.messagebox, "showinfo", lambda *a, **k: None)
    try:
        root = tk.Tk()
    except tk.TclError as exc:  # e.g. a machine without a display
        pytest.skip(f"Tk is not available: {exc}")
    root.withdraw()
    callback_errors = []
    root.report_callback_exception = lambda exc_type, exc, tb: callback_errors.append(exc)
    game = main.TicTacToe(root)
    yield root, game, callback_errors
    root.destroy()
