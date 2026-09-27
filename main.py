import random
import tkinter as tk
from tkinter import messagebox

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # рядки
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # стовпці
    (0, 4, 8), (2, 4, 6),             # діагоналі
]

DIFFICULTIES = {
    "easy": "Easy",
    "medium": "Medium",
    "hard": "Hard",
}


class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic-Tac-Toe")
        self.root.resizable(False, False)

        self.board = [""] * 9
        self.current_player = "X"
        self.buttons = []
        self.game_over = False

        self.mode_var = tk.StringVar(value="PVC")
        self.difficulty_var = tk.StringVar(value="medium")
        self.first_var = tk.StringVar(value="human")

        self.mode = "PVC"
        self.difficulty = "medium"
        self.human_mark = "X"
        self.computer_mark = "O"

        self.menu_frame = None
        self.game_frame = None
        self.status_label = None

        self.build_menu()

    # ---------- Меню вибору режиму ----------

    def build_menu(self):
        if self.game_frame:
            self.game_frame.destroy()
            self.game_frame = None

        self.menu_frame = tk.Frame(self.root, padx=20, pady=20)
        self.menu_frame.grid(row=0, column=0)

        tk.Label(self.menu_frame, text="Tic-Tac-Toe", font=("Arial", 20, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 15)
        )

        tk.Label(self.menu_frame, text="Game mode:", font=("Arial", 12, "bold")).grid(
            row=1, column=0, columnspan=2, sticky="w"
        )
        tk.Radiobutton(
            self.menu_frame, text="Two players", variable=self.mode_var, value="PVP",
            font=("Arial", 11), command=self.on_mode_change,
        ).grid(row=2, column=0, columnspan=2, sticky="w")
        tk.Radiobutton(
            self.menu_frame, text="Vs. computer", variable=self.mode_var, value="PVC",
            font=("Arial", 11), command=self.on_mode_change,
        ).grid(row=3, column=0, columnspan=2, sticky="w")

        self.difficulty_label = tk.Label(
            self.menu_frame, text="Difficulty:", font=("Arial", 12, "bold")
        )
        self.difficulty_label.grid(row=4, column=0, columnspan=2, sticky="w", pady=(15, 0))

        self.difficulty_buttons = []
        for i, (value, text) in enumerate(DIFFICULTIES.items()):
            rb = tk.Radiobutton(
                self.menu_frame, text=text, variable=self.difficulty_var, value=value,
                font=("Arial", 11),
            )
            rb.grid(row=5 + i, column=0, columnspan=2, sticky="w")
            self.difficulty_buttons.append(rb)

        self.first_label = tk.Label(
            self.menu_frame, text="Who goes first:", font=("Arial", 12, "bold")
        )
        self.first_label.grid(row=8, column=0, columnspan=2, sticky="w", pady=(15, 0))

        self.first_buttons = []
        rb1 = tk.Radiobutton(
            self.menu_frame, text="Me (X)", variable=self.first_var, value="human",
            font=("Arial", 11),
        )
        rb1.grid(row=9, column=0, columnspan=2, sticky="w")
        rb2 = tk.Radiobutton(
            self.menu_frame, text="Computer (X)", variable=self.first_var, value="computer",
            font=("Arial", 11),
        )
        rb2.grid(row=10, column=0, columnspan=2, sticky="w")
        self.first_buttons = [rb1, rb2]

        tk.Button(
            self.menu_frame, text="Start game", font=("Arial", 13, "bold"),
            bg="lightblue", command=self.start_game,
        ).grid(row=11, column=0, columnspan=2, pady=(20, 0))

        self.on_mode_change()

    def on_mode_change(self):
        state = tk.NORMAL if self.mode_var.get() == "PVC" else tk.DISABLED
        for rb in self.difficulty_buttons:
            rb.config(state=state)
        for rb in self.first_buttons:
            rb.config(state=state)

    # ---------- Ігровий екран ----------

    def start_game(self):
        self.mode = self.mode_var.get()
        self.difficulty = self.difficulty_var.get()

        self.menu_frame.destroy()
        self.menu_frame = None

        self.game_frame = tk.Frame(self.root, padx=10, pady=10)
        self.game_frame.grid(row=0, column=0)

        self.status_label = tk.Label(self.game_frame, text="", font=("Arial", 16), pady=10)
        self.status_label.grid(row=0, column=0, columnspan=3)

        board_frame = tk.Frame(self.game_frame)
        board_frame.grid(row=1, column=0, columnspan=3)

        self.buttons = []
        for i in range(9):
            btn = tk.Button(
                board_frame,
                text="",
                font=("Arial", 32, "bold"),
                width=4,
                height=2,
                command=lambda i=i: self.on_click(i),
            )
            btn.grid(row=i // 3, column=i % 3)
            self.buttons.append(btn)

        button_row = tk.Frame(self.game_frame)
        button_row.grid(row=2, column=0, columnspan=3, pady=10)
        tk.Button(button_row, text="New game", font=("Arial", 12), command=self.reset).pack(
            side="left", padx=5
        )
        tk.Button(button_row, text="Menu", font=("Arial", 12), command=self.build_menu).pack(
            side="left", padx=5
        )

        self.setup_new_round()

    def setup_new_round(self):
        self.board = [""] * 9
        self.game_over = False
        for btn in self.buttons:
            btn.config(text="", bg="SystemButtonFace", state=tk.NORMAL)

        if self.mode == "PVC" and self.first_var.get() == "computer":
            self.human_mark, self.computer_mark = "O", "X"
            self.current_player = "X"
        else:
            self.human_mark, self.computer_mark = "X", "O"
            self.current_player = "X"

        self.update_status()

        if self.mode == "PVC" and self.current_player == self.computer_mark:
            self.root.after(400, self.computer_move)

    def update_status(self):
        if self.mode == "PVC":
            who = "Your turn" if self.current_player == self.human_mark else "Computer's turn..."
            self.status_label.config(text=f"{who} ({self.current_player})")
        else:
            self.status_label.config(text=f"Player's turn: {self.current_player}")

    # ---------- Ігрова логіка ----------

    def on_click(self, index):
        if self.game_over or self.board[index] != "":
            return
        if self.mode == "PVC" and self.current_player != self.human_mark:
            return

        self.make_move(index)

        if not self.game_over and self.mode == "PVC" and self.current_player == self.computer_mark:
            self.root.after(400, self.computer_move)

    def make_move(self, index):
        self.board[index] = self.current_player
        self.buttons[index].config(
            text=self.current_player,
            fg="blue" if self.current_player == "X" else "red",
        )

        winner_line = self.check_winner(self.board)
        if winner_line:
            self.game_over = True
            self.highlight_win(winner_line)
            self.finish_round(f"Winner: {self.current_player}")
            return

        if "" not in self.board:
            self.game_over = True
            self.finish_round("Draw!")
            return

        self.current_player = "O" if self.current_player == "X" else "X"
        self.update_status()

    def finish_round(self, message):
        if self.mode == "PVC":
            if "Winner" in message:
                mark = message.split(": ")[1]
                if mark == self.human_mark:
                    message = "You win!"
                else:
                    message = "The computer wins!"
        self.status_label.config(text=message)
        messagebox.showinfo("Game over", message)

    def computer_move(self):
        if self.game_over:
            return
        index = self.choose_computer_move()
        if index is not None:
            self.make_move(index)

    def choose_computer_move(self):
        empty = self.empty_cells(self.board)
        if not empty:
            return None

        if self.difficulty == "easy":
            return random.choice(empty)

        if self.difficulty == "medium":
            move = self.find_winning_move(self.board, self.computer_mark)
            if move is not None:
                return move
            move = self.find_winning_move(self.board, self.human_mark)
            if move is not None:
                return move
            return random.choice(empty)

        # hard: мінімакс, зіграти неможливо
        _, move = self.minimax(self.board[:], self.computer_mark)
        return move

    def find_winning_move(self, board, mark):
        for i in self.empty_cells(board):
            board[i] = mark
            win = self.check_winner(board)
            board[i] = ""
            if win:
                return i
        return None

    def minimax(self, board, player):
        winner_line = self.check_winner(board)
        if winner_line:
            winner_mark = board[winner_line[0]]
            score = 1 if winner_mark == self.computer_mark else -1
            return score, None
        if "" not in board:
            return 0, None

        opponent = self.human_mark if player == self.computer_mark else self.computer_mark
        maximizing = player == self.computer_mark
        best_score = -2 if maximizing else 2
        best_move = None

        for i in self.empty_cells(board):
            board[i] = player
            score, _ = self.minimax(board, opponent)
            board[i] = ""
            if maximizing and score > best_score:
                best_score, best_move = score, i
            elif not maximizing and score < best_score:
                best_score, best_move = score, i

        return best_score, best_move

    @staticmethod
    def empty_cells(board):
        return [i for i, v in enumerate(board) if v == ""]

    @staticmethod
    def check_winner(board):
        for a, b, c in WIN_LINES:
            if board[a] and board[a] == board[b] == board[c]:
                return (a, b, c)
        return None

    def highlight_win(self, line):
        for i in line:
            self.buttons[i].config(bg="lightgreen")

    def reset(self):
        self.setup_new_round()


def main():
    root = tk.Tk()
    TicTacToe(root)
    root.mainloop()


if __name__ == "__main__":
    main()
