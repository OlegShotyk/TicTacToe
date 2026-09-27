# Test Strategy - Tic-Tac-Toe

| | |
|---|---|
| **Product** | Tic-Tac-Toe desktop game, Python 3 + Tkinter (`main.py`, ~320 LOC) |
| **Document owner** | QA / SDET |
| **Status** | Active - updated 2026-09-27 |

## 1. Purpose and scope

This document describes how the game is tested: what is covered, at which
level, with which tools, and when a build is considered good enough to release.
It is intentionally short - the product is small, so the process is
proportionate to it.

**In scope**

- Game rules: moves, turn order, win / draw detection, reset.
- Game modes: two players (PvP) and player vs computer (PvC).
- Computer opponent: Easy, Medium and Hard difficulty.
- User interface: menu, game screen, status line, end-of-round pop-up, English texts.
- Non-functional: platform compatibility, responsiveness, basic usability / accessibility.

**Out of scope**

- Tkinter / Tcl-Tk itself and the operating system.
- Packaging and installers (the game is run from source).
- Localisation to languages other than English.

The testable rules are listed in [REQUIREMENTS.md](REQUIREMENTS.md), with
traceability to the tests that cover them.

## 2. Quality risks (what could hurt users most)

| Risk | Impact | Likelihood | How it is addressed |
|---|---|---|---|
| Wrong winner / missed draw | High | Low | Unit + property-based tests of `check_winner`, `make_move` |
| Hard AI can be beaten | High (the feature's promise) | Low | **Exhaustive** test over every possible game |
| Race between GUI callbacks (delayed computer move vs. New game / Menu) | High | **Confirmed** (#1, #2) | Exploratory testing, regression tests with a real Tk loop |
| Crash on non-Windows platforms | Critical | **Confirmed on Linux** (#4) | Cross-platform CI matrix + GUI smoke tests |
| UI freezes during Hard AI thinking | Medium | **Confirmed** (#3) | Performance test with a time budget (planned) |
| Result logic depends on message text | Medium | Present in design | Unit tests of every end-of-round message; refactoring proposal |

## 3. Test levels and approach

The test pyramid for this project:

| Level | What | How | Status |
|---|---|---|---|
| **Unit** | Pure game logic and single methods | pytest; GUI replaced by stubs (`tests/helpers.py`), no window opened | Done |
| **Exhaustive** | "Hard AI never loses" | Explore every legal human move sequence, AI moving first and second (`tests/test_ai_exhaustive.py`) | Done |
| **Property-based** | Rules that must hold for *any* reachable position | Hypothesis generates random legal positions (`tests/test_properties.py`) | Done |
| **Component (GUI)** | Real Tk widgets and event loop, no human | Hidden `tk.Tk()`, buttons found by their text and `invoke()`d, event pumping (`tests/test_gui_smoke.py`, `tests/test_known_bugs.py`); to be extended with a fake clock | Started |
| **End-to-end** | App launched as a separate process and driven like a user | pywinauto (Windows), 2-3 smoke scenarios | Planned |
| **Exploratory (manual)** | Timing, usability, look and feel, unexpected sequences | Time-boxed charters, see [EXPLORATORY_TESTING.md](EXPLORATORY_TESTING.md) | Session 1 done |
| **Non-functional** | Performance, platforms, accessibility | GitHub Actions on Windows/macOS/Linux (done); pytest-benchmark; manual keyboard review | Partly done |

Principles:

- **Test logic below the GUI.** Most checks are fast unit tests; only behaviour
  that depends on the Tk event loop is tested with a real window.
- **Known bugs are pinned by tests.** A confirmed bug gets a regression test
  marked `xfail(strict=True)` with the issue number. When the bug is fixed the
  test unexpectedly passes, the suite goes red, and the marker is removed.
- **Deterministic tests.** No real waiting on user input; random choices are
  either seeded or checked by properties, never by exact value.

## 4. Environments

| | Now | Target (CI) |
|---|---|---|
| OS | Windows 10 | Windows, macOS, Ubuntu (Linux with Xvfb virtual display) |
| Python | 3.14 | 3.10, 3.12, 3.14 |
| Tk | 8.6.15 | as shipped with each Python build (8.6.14 on Ubuntu) |

CI: [`.github/workflows/tests.yml`](../.github/workflows/tests.yml) runs the
whole suite on every push to `main` and every pull request: 3 OS × 3 Python
versions, branch coverage in the job summary, JUnit XML results as artifacts.

## 5. Tools

| Purpose | Tool |
|---|---|
| Test runner, fixtures, parametrization, monkeypatching | pytest |
| Property-based testing | Hypothesis |
| Coverage | pytest-cov, branch coverage (98% of `main.py`) |
| Mutation testing (planned) | mutmut |
| Performance (planned) | pytest-benchmark |
| GUI end-to-end (planned) | pywinauto |
| CI | GitHub Actions |
| Defect tracking | GitHub Issues, using the bug report template in `.github/ISSUE_TEMPLATE` |

## 6. Defect management

- Every defect is filed as a GitHub Issue using the bug template: steps,
  expected / actual result, environment, severity, and the test that reproduces it.
- Severity: **Critical** (app unusable / crash on start), **Major** (wrong game
  result or corrupted state), **Minor** (cosmetic, performance, error in log).
- Findings not yet reproduced are filed with the `[Needs verification]` prefix.

## 7. Entry and exit criteria

**Start testing a change when:** it is on a branch, the application starts, and
the existing suite passes locally.

**A change is ready to merge when:**

1. All automated tests pass (`xfail` tests only for open, linked issues).
2. Every requirement in `REQUIREMENTS.md` touched by the change has at least one test.
3. No open Critical or Major bug in the changed area.
4. The CI build is green on all three operating systems.

## 8. Deliverables

- This strategy, [REQUIREMENTS.md](REQUIREMENTS.md) (rules + traceability),
  [EXPLORATORY_TESTING.md](EXPLORATORY_TESTING.md) (charters + session notes).
- Automated tests in `tests/`.
- Bug reports in GitHub Issues.
- Test results and coverage as CI artifacts / job summary.

## 9. Roadmap

1. ~~Strategy and requirements~~
2. ~~Exploratory session 1, file bugs~~
3. ~~Unit, property-based and exhaustive AI tests~~
4. ~~GitHub Actions: OS × Python matrix, coverage report~~
5. Refactoring proposal: separate `GameEngine` from the Tk GUI
6. Component GUI tests with a fake clock for `after()`
7. Performance test (Hard AI move under 200 ms) and mutation testing
