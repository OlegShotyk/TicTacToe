# Requirements and Traceability - Tic-Tac-Toe

The project has no written specification, so these requirements were derived
from the current behaviour of `main.py` and reviewed as the intended behaviour.
Each requirement has an ID that is used in test docstrings, bug reports and the
traceability matrix below.

## Functional requirements

| ID | Requirement |
|---|---|
| **R1** | The board has 3×3 cells. X always moves first and players alternate. X is drawn in blue, O in red. |
| **R2** | An occupied cell cannot be changed. No moves are accepted after the round is over. |
| **R3** | A win is detected on any of the 8 lines (3 rows, 3 columns, 2 diagonals). The winning line is highlighted in green. |
| **R4** | When the board is full and nobody has won, the round is a draw. |
| **R5** | The status line shows whose turn it is: PvP - `Player's turn: X`; PvC - `Your turn (X)` or `Computer's turn... (O)`. |
| **R6** | At the end of a round the status line and a pop-up titled `Game over` show the result: PvP - `Winner: X` / `Draw!`; PvC - `You win!` / `The computer wins!` / `Draw!`. The pop-up appears exactly once per round. |
| **R7** | The menu offers two modes: `Two players` and `Vs. computer`. The difficulty and "Who goes first" options are enabled only for `Vs. computer`. |
| **R8** | Vs. computer: whoever goes first plays X. If the computer goes first, it makes its move automatically. In PvP the "who goes first" setting is ignored. |
| **R9** | Easy: the computer plays a random empty cell. |
| **R10** | Medium: the computer completes its own line if it can, otherwise blocks the opponent's winning cell, otherwise plays randomly. |
| **R11** | Hard: the computer plays optimally and **never loses**, whether it moves first or second. |
| **R12** | `New game` starts a fresh round with the same settings. `Menu` returns to the menu. |
| **R13** | The computer answers after a short delay (~400 ms). Human clicks are ignored during the computer's turn. Leaving the round (New game / Menu) cancels any pending computer move. |

## Non-functional requirements

| ID | Requirement |
|---|---|
| **N1** | Runs on Windows, macOS and Linux with Python 3.10+ and the standard Tkinter. |
| **N2** | The window stays responsive: a computer move takes at most 200 ms on a typical PC. |
| **N3** | All user-facing text is in English. |
| **N4** | Unexpected errors do not appear during normal use (no tracebacks from Tk callbacks). |

## Traceability matrix

Status: ✅ covered and passing · ❌ covered, test fails because of an open bug (xfail) · 🔍 manual / exploratory · ⏳ planned

| ID | Automated tests | Other checks | Status |
|---|---|---|---|
| R1 | `test_game_flow.py::TestMakeMoveRendering`, `test_main.py::TestMakeMove::test_marks_board_and_switches_player` | | ✅ |
| R2 | `test_game_flow.py::TestOnClick::test_occupied_cell_cannot_be_overwritten`, `test_main.py::TestMakeMove::test_does_not_allow_move_after_game_over_via_on_click`, `test_game_flow.py::TestEndOfRound::test_popup_shown_exactly_once_per_round` | | ✅ |
| R3 | `test_main.py::TestCheckWinner` (all 8 lines), `test_properties.py::test_check_winner_returns_a_real_line_of_one_mark`, `test_game_flow.py::TestEndOfRound::test_winning_line_is_highlighted` | | ✅ |
| R4 | `test_main.py::TestMakeMove::test_detects_draw_and_ends_game`, `test_game_flow.py::TestEndOfRound::test_draw_message_in_both_modes` | | ✅ |
| R5 | `test_game_flow.py::TestUpdateStatus` | | ✅ |
| R6 | `test_game_flow.py::TestEndOfRound` | Pop-up look: exploratory | ✅ |
| R7 | `test_game_flow.py::TestModeChange` | | ✅ |
| R8 | `test_game_flow.py::TestSetupNewRound` | | ✅ |
| R9 | `test_main.py::TestChooseComputerMoveEasy`, `test_properties.py::test_computer_always_picks_an_empty_cell` | | ✅ |
| R10 | `test_main.py::TestChooseComputerMoveMedium`, `test_properties.py::test_medium_wins_when_it_can_and_blocks_otherwise` | | ✅ |
| R11 | **`test_ai_exhaustive.py::test_hard_ai_never_loses_any_possible_game`** (every possible game, AI first and second), `test_properties.py::test_hard_keeps_the_best_achievable_result`, `test_main.py::TestChooseComputerMoveHard`, `test_main.py::TestMinimax` | | ✅ |
| R12 | `test_game_flow.py::TestSetupNewRound::test_reset_starts_a_new_round` | | ✅ |
| R13 | `test_game_flow.py::TestOnClick`, `test_known_bugs.py::test_new_game_during_computer_delay_leaves_board_empty`, `test_known_bugs.py::test_menu_during_computer_delay_raises_no_error` | Charter C1 | ❌ [#1](https://github.com/OlegShotyk/TicTacToe/issues/1), [#2](https://github.com/OlegShotyk/TicTacToe/issues/2) |
| N1 | `test_gui_smoke.py` on the CI matrix (Windows, macOS, Linux × Python 3.10/3.12/3.14) | Charter C3 | ❌ Linux: [#4](https://github.com/OlegShotyk/TicTacToe/issues/4); ✅ Windows, macOS |
| N2 | - | Charter C2 (measured 0.73 s); pytest-benchmark planned | ❌ [#3](https://github.com/OlegShotyk/TicTacToe/issues/3) |
| N3 | Message assertions in `test_game_flow.py` | Visual review of all screens | ✅ 🔍 |
| N4 | `test_known_bugs.py::test_menu_during_computer_delay_raises_no_error` | Charter C1 | ❌ [#2](https://github.com/OlegShotyk/TicTacToe/issues/2) |
