# Tic-Tac-Toe

A Tic-Tac-Toe desktop game in Python with Tkinter.

- **Two players** on one computer, or **vs. computer**
- Computer difficulty: **Easy** (random), **Medium** (wins / blocks), **Hard** (minimax, never loses)
- Choose who goes first against the computer

## Run

Requires Python 3.10+ with Tkinter (included in the standard Windows/macOS installers).

```
python main.py
```

## Tests

```
pip install -r requirements-dev.txt
pytest
```

The suite contains unit tests, property-based tests (Hypothesis), an exhaustive
test proving the Hard AI never loses, and regression tests for open bugs
(marked `xfail`).

## Test documentation

- [Test strategy](docs/TEST_STRATEGY.md)
- [Requirements and traceability](docs/REQUIREMENTS.md)
- [Exploratory testing: charters and session notes](docs/EXPLORATORY_TESTING.md)
- Bugs: [GitHub Issues](https://github.com/OlegShotyk/TicTacToe/issues)
