"""
Shared test doubles for building TicTacToe instances without a real Tk window.

TicTacToe.__init__ builds GUI widgets, so tests create instances with
object.__new__ and attach lightweight stubs instead.
"""
import time

from main import TicTacToe


class StubWidget:
    """Minimal stand-in for a tk.Button / tk.Label: records config() calls."""

    def __init__(self):
        self.config_calls = []

    def config(self, **kwargs):
        self.config_calls.append(kwargs)

    def last(self, key):
        """Most recent value passed to config() for the given option."""
        for call in reversed(self.config_calls):
            if key in call:
                return call[key]
        return None


class StubVar:
    """Stand-in for tk.StringVar."""

    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class StubRoot:
    """Stand-in for tk.Tk that records after() calls instead of scheduling them."""

    def __init__(self):
        self.scheduled = []

    def after(self, delay_ms, callback):
        self.scheduled.append((delay_ms, callback))
        return f"after#{len(self.scheduled)}"


def make_game(mode="PVP", human_mark="X", computer_mark="O", difficulty="medium",
              board=None, current_player="X", first="human"):
    game = object.__new__(TicTacToe)
    game.root = StubRoot()
    game.board = board if board is not None else [""] * 9
    game.current_player = current_player
    game.buttons = [StubWidget() for _ in range(9)]
    game.status_label = StubWidget()
    game.game_over = False
    game.mode = mode
    game.difficulty = difficulty
    game.human_mark = human_mark
    game.computer_mark = computer_mark
    game.mode_var = StubVar(mode)
    game.difficulty_var = StubVar(difficulty)
    game.first_var = StubVar(first)
    return game


def pump_events(root, ms):
    """Process Tk events for `ms` milliseconds so after() callbacks can fire."""
    end = time.monotonic() + ms / 1000
    while time.monotonic() < end:
        root.update()
        time.sleep(0.01)
