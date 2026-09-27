# Exploratory Testing - Charters and Session Notes

Exploratory testing looks for problems that scripted tests do not anticipate.
Each session follows a **charter**: *explore <area> with <resources> to
discover <information>*. It is time-boxed and ends with notes, bugs and ideas
for new automated tests.

## Charters

| ID | Charter | Status |
|---|---|---|
| C1 | Explore **interrupting the computer's turn** (New game, Menu, extra clicks during the 400 ms delay) to discover state corruption and errors. | Done - session 1 |
| C2 | Explore **Hard difficulty responsiveness**, especially when the computer moves first, to discover UI freezes. | Done - session 1 |
| C3 | Explore **platform-specific code** (colours, fonts, window APIs) to discover what breaks outside Windows. | Done - confirmed by CI |
| C4 | Explore **AI behaviour in unusual positions** with generated boards to discover wrong or surprising moves. | Done - session 1 (via Hypothesis) |
| C5 | Explore **usability and accessibility**: keyboard only, high-DPI scaling, window focus, pop-up behaviour, repeated rounds. | Not started |

## Session 1 - 2026-09-27

**Tester:** Claude (AI assistant acting as SDET) · **Build:** commit `d1a74f5`
· **Environment:** Windows 10 Home 19045, Python 3.14.6, Tk 8.6.15
· **Time box:** 60 min

**Method:** code review to form hypotheses, then scripted reproduction against
the real application. The Tk window was created hidden, buttons were pressed
with `invoke()`, and the event loop was pumped so that `after()` callbacks fired
exactly as they would for a real user. No manual mouse clicking was done in
this session. That is still needed for C5 and for visual checks.

### C1 - Interrupting the computer's turn

| Step | Observation |
|---|---|
| PvC, human first, click a cell, then **New game** within 400 ms | ❌ The computer's pending move fires on the **new** board and places **X**, the human's mark (board `['', '', '', '', 'X', '', '', '', '']`, current player O). The human is forced to play O. → **Bug [#1](https://github.com/OlegShotyk/TicTacToe/issues/1)** (Major) |
| Same, but click **Menu** within 400 ms | ❌ `TclError: invalid command name ".!frame2.!frame.!button2"`: the callback uses buttons that no longer exist. → **Bug [#2](https://github.com/OlegShotyk/TicTacToe/issues/2)** (Minor) |
| Click another cell during the computer's turn | ✅ Ignored, as intended |

Root cause (shared): the id returned by `root.after()` is not stored, so the
callback is never cancelled, and `computer_move()` does not check whose turn it is.
Both scenarios are now automated in `tests/test_known_bugs.py` as `xfail(strict=True)`.

### C2 - Hard AI responsiveness

| Step | Observation |
|---|---|
| Hard, computer first: time `choose_computer_move()` on an empty board | ❌ **0.73 s** on the test PC, running on the Tk main thread, so the window does not respond for that long. Later moves are fast (under 0.1 s). → **Bug [#3](https://github.com/OlegShotyk/TicTacToe/issues/3)** (Minor, performance) |

Cause: full minimax without alpha-beta pruning or caching. A performance test
with a 200 ms budget is planned (requirement N2).

### C3 - Platform-specific code (code review only)

| Finding | Status |
|---|---|
| `btn.config(bg="SystemButtonFace")` in `setup_new_round`: a Windows-only system colour name. On X11 Tk it is expected to raise `unknown color name`, which would crash *Start game*. | Filed as **[#4](https://github.com/OlegShotyk/TicTacToe/issues/4)**, first as `[Needs verification]`. **Confirmed by CI on 2026-09-27:** Ubuntu (Tk 8.6.14) fails with `TclError: unknown color name "SystemButtonFace"` on *Start game*; macOS and Windows are fine. Severity raised to Critical (Linux). |
| Font "Arial" | Not a crash risk: Tk falls back to a default font. The look may differ; check visually on Linux. |

### C4 - AI in unusual positions (Hypothesis)

- ✅ Easy / Medium / Hard always choose an empty cell and never change the real board.
- ✅ Medium always takes a win if available and otherwise blocks a single threat.
- ✅ Every possible game against Hard was checked (AI first and second): Hard never loses.
- ℹ️ **Observation, not a bug:** in a position that is *already lost* (the
  opponent has a fork), Hard does not block the immediate threat. Every move
  scores -1 and minimax just returns the first empty cell. Example found by
  Hypothesis: `X X O / . . . / . . O`, X to move, plays cell 3 instead of 5.
  Such positions cannot arise in a real game against Hard (proven by the
  exhaustive test), so there is no user impact. If the AI is ever reused for
  analysis or hints, prefer the move that loses *latest*.

### Ideas for new tests (from this session)

- Component test with a **fake clock** for `root.after`, so timing scenarios
  run instantly and deterministically.
- Performance test for N2.
- CI matrix for C3.
- C5 checklist: Tab/Space navigation, 150 % / 200 % Windows scaling, closing the
  pop-up with Esc/Enter, 20 rounds in a row without restart.

### Session summary

| Bugs found | Confirmed | Needs verification | Observations |
|---|---|---|---|
| 4 | 4 (#1, #2, #3; #4 confirmed later by CI) | 0 | 1 (lost-position behaviour of Hard AI) |
