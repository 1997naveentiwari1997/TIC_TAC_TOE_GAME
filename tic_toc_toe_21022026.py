#===============================LOGS_PATH==========================================================

import streamlit as st
import logging
from logging.handlers import RotatingFileHandler
import os
import sys

#import brings built-in Python tools into your program
#logging → used to save messages like “game started”
#RotatingFileHandler → keeps log files from getting too big
#os → works with folders and files
#sys → talks to the Python system (how the program is running)

logging.DEBUG

#This line does nothing by itself.It should normally be used when setting a level (later you do that correctly).

def get_app_dir():   #def means define a function. This function finds where your program is located
    if getattr(sys, 'frozen', False):   #Checks if the program is turned into an .exe file. getattr safely checks if sys.frozen exists
        return os.path.dirname(sys.executable)   #If it’s an .exe, return the folder where the .exe lives
    return os.path.dirname(os.path.abspath(__file__))  #Otherwise, return the folder where this .py file is located

APP_DIR = get_app_dir()   #Runs the function and stores the result
LOG_DIR = os.path.join(APP_DIR, "logs")  #Creates a path like: your_program_folder/logs
os.makedirs(LOG_DIR, exist_ok=True)  #Creates the logs folder. exist_ok=True → no error if it already exists

LOG_FILE = os.path.join(LOG_DIR, "tic_tac_toe.log")  #Full path to the log file

handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=2_000_000,  #Log file size limit = 2MB
    backupCount=5,   #Keep 5 old log files
    encoding="utf-8"  #Use UTF-8 text
)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"  #Defines how log messages look: 2026-01-25 12:00 | INFO | Game started
)
handler.setFormatter(formatter)  #Applies that format to the file handler

logger = logging.getLogger()  #Gets the main logger object
logger.setLevel(logging.DEBUG)   # 🔥 log4j.ALL equivalent(Allows ALL messages (debug, info, warning, error))
logger.addHandler(handler)   #Tells Python: send logs to the file

logger.debug("=== Application started ===") #Writes this message to the log file

#==========================PART 2: TKINTER (GUI WINDOW)==============================================

import tkinter as tk  #tkinter = Python’s built-in GUI library
from tkinter import messagebox  #messagebox = pop-up dialogs (alerts)

# ===================== WINDOW =====================
root = tk.Tk()  #Creates the main window
root.title("Tic Tac Toe Pro") #Window title text
root.geometry("900x750") #Window size (width x height)
root.minsize(750, 650) #Minimum window size
BG = "#2e294e"  #Background color (hex color)
root.configure(bg=BG)  #Sets window background color

# ===================== GAME STATE =====================
CELL = 150  #Size of one tic-tac-toe cell (pixels)
board = [""] * 9  #Game board:
#["", "", "",
# "", "", "",
# "", "", ""]
current_turn = "X" #Whose turn it is
player_symbol = "X"
bot_symbol = "O"
#Symbols used in the game

game_mode = "BOT" #Game type (BOT or 2P)
rounds = 3
current_round = 1
#Best-of-3 by default
player_score = 0
bot_score = 0
#Scores
move_count = 0 #Counts moves (used to check winner faster)

player_name = ""
opponent_name = ""
#Names entered by the user
# ===================== FRAMES =====================
main = tk.Frame(root, bg=BG)   #A container inside the window
main.pack(fill="both", expand=True)   #Makes it fill the window

#Two screens:
#Setup screen
#Game screen

setup_frame = tk.Frame(main, bg=BG)
game_frame = tk.Frame(main, bg=BG)

# ===================== SETUP SCREEN =====================
def show_setup():   #Function to show setup screen
    game_frame.pack_forget()  #Hides the game screen
    setup_frame.pack(fill="both", expand=True)  #Shows setup screen

tk.Label(setup_frame, text="TIC TAC TOE",  #Big title text
         font=("Arial", 36, "bold"),
         fg="white", bg=BG).pack(pady=30)  

mode_var = tk.StringVar(value="BOT")  #Stores selected radio button value

def on_mode_change():
    if mode_var.get() == "BOT":
        player2_entry.delete(0, tk.END)
        player2_entry.config(state="disabled")
    else:
        player2_entry.config(state="normal")

tk.Radiobutton(setup_frame, text="Play vs Bot",
               variable=mode_var, value="BOT",
               font=("Arial", 18),
               fg="white", bg=BG,
               selectcolor=BG,
               command=on_mode_change).pack()

tk.Radiobutton(setup_frame, text="2 Players (Local)",
               variable=mode_var, value="2P",
               font=("Arial", 18),
               fg="white", bg=BG,
               selectcolor=BG,
               command=on_mode_change).pack()

tk.Label(setup_frame, text="Choose Your Symbol",
         font=("Arial", 18),
         fg="white", bg=BG).pack(pady=10)

symbol_var = tk.StringVar(value="X")

tk.Radiobutton(setup_frame, text="X",
               variable=symbol_var, value="X",
               font=("Arial", 16),
               fg="white", bg=BG,
               selectcolor=BG).pack()

tk.Radiobutton(setup_frame, text="O",
               variable=symbol_var, value="O",
               font=("Arial", 16),
               fg="white", bg=BG,
               selectcolor=BG).pack()

tk.Label(setup_frame, text="Player Name",
         font=("Arial", 16),
         fg="white", bg=BG).pack(pady=5)

player1_entry = tk.Entry(setup_frame, font=("Arial", 16))
player1_entry.pack()

tk.Label(setup_frame, text="Opponent Name",
         font=("Arial", 16),
         fg="white", bg=BG).pack(pady=5)

player2_entry = tk.Entry(setup_frame, font=("Arial", 16))
player2_entry.pack()
player2_entry.config(state="disabled")

tk.Label(setup_frame, text="Number of Rounds (Odd)",
         font=("Arial", 16),
         fg="white", bg=BG).pack(pady=10)

round_entry = tk.Entry(setup_frame, font=("Arial", 16))
round_entry.pack()

# ===================== START GAME =====================
def start_game():
    global rounds, game_mode, player_symbol, bot_symbol
    global current_turn, player_name, opponent_name
    
    logger.debug("Start Game clicked")
    
    player_name = player1_entry.get().strip()
    opponent_name = player2_entry.get().strip()

    if not player_name:
        messagebox.showerror("Error", "Player name is required.")
        return

    game_mode = mode_var.get()

    if game_mode == "2P":
        if not opponent_name:
            messagebox.showerror("Error", "Opponent name is required.")
            return
        if player_name.lower() == opponent_name.lower():
            messagebox.showerror("Error", "Player names must be different.")
            return
    else:
        opponent_name = "Bot"

    try:
        r = int(round_entry.get())
        if r % 2 == 0:
            raise ValueError
        rounds = r
    except:
        messagebox.showerror("Error", "Rounds must be an odd number.")
        return

    player_symbol = symbol_var.get()
    bot_symbol = "O" if player_symbol == "X" else "X"
    current_turn = "X"

    logger.info(
        f"Game started | Mode={game_mode} | Rounds={rounds} | "
        f"{player_name} vs {opponent_name}"
    )
    setup_frame.pack_forget()
    init_game()

tk.Button(setup_frame, text="Start Game",
          font=("Arial", 20),
          command=start_game).pack(pady=25)

root.bind("<Return>", lambda event: start_game())

# ===================== GAME UI =====================
status = tk.Label(game_frame, font=("Arial", 20, "bold"),
                  fg="white", bg=BG)
status.pack(pady=10)

score = tk.Label(game_frame, font=("Arial", 15),
                 fg="white", bg=BG)
score.pack()

canvas = tk.Canvas(game_frame, width=450, height=450,
                   bg="#1b1b2f", highlightthickness=0)
canvas.pack(expand=True)

# ===================== GAME LOGIC =====================
def check_winner(state):
    wins = [
        (0,1,2),(3,4,5),(6,7,8),
        (0,3,6),(1,4,7),(2,5,8),
        (0,4,8),(2,4,6)
    ]
    for a,b,c in wins:
        if state[a] == state[b] == state[c] != "":
            return state[a], (a,b,c)
    if "" not in state:
        return "Draw", None
    return None, None

# ===================== MINIMAX (OPTIMAL) =====================
def minimax(state, is_bot, alpha, beta):
    result, _ = check_winner(state)
    if result == bot_symbol:
        return 1
    if result == player_symbol:
        return -1
    if result == "Draw":
        return 0

    if is_bot:
        best = -999
        for i in range(9):
            if state[i] == "":
                state[i] = bot_symbol
                score = minimax(state, False, alpha, beta)
                state[i] = ""
                best = max(best, score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    break
        return best
    else:
        best = 999
        for i in range(9):
            if state[i] == "":
                state[i] = player_symbol
                score = minimax(state, True, alpha, beta)
                state[i] = ""
                best = min(best, score)
                beta = min(beta, score)
                if beta <= alpha:
                    break
        return best

def bot_move():
    best_score = -999
    move = None

    logger.debug("Bot computing move")

    for i in range(9):
        if board[i] == "":
            board[i] = bot_symbol
            score = minimax(board, False, -999, 999)
            board[i] = ""
            if score > best_score:
                best_score = score
                move = i
    
    logger.debug(f"Bot selected cell {move}")

    if move is not None:
        place_move(move)

# ===================== MOVE HANDLING =====================
def place_move(index):
    global current_turn, move_count

    logger.debug(f"Move attempt | Cell={index} | Turn={current_turn}")

    if board[index] != "":
        return

    board[index] = current_turn
    draw_symbol(index, current_turn)
    move_count += 1

    logger.info(f"Move placed | Player={current_turn} | Cell={index}")

    winner = None
    combo = None
    if move_count >= 5:
        winner, combo = check_winner(board)

    if winner:
        if combo:
            draw_win_line(combo)

        logger.info(
            f"Round {current_round} finished | Result={winner}"
        )

        if winner == "Draw":
            messagebox.showinfo("Result", "Draw!")
        elif winner == player_symbol:
            messagebox.showinfo("Result", f"{player_name} wins this round!")
        else:
            messagebox.showinfo("Result", f"{opponent_name} wins this round!")

        root.after(600, lambda: end_round(winner))
        return

    current_turn = bot_symbol if current_turn == player_symbol else player_symbol
    update_status()

    if game_mode == "BOT" and current_turn == bot_symbol:
        root.after(50, bot_move)

# ===================== DRAWING =====================
def draw_symbol(i, symbol):
    x = (i % 3) * CELL + CELL // 2
    y = (i // 3) * CELL + CELL // 2
    canvas.create_text(x, y, text=symbol,
                       font=("Arial", 72, "bold"),
                       fill="white")

def draw_win_line(combo):
    x1 = (combo[0] % 3) * CELL + CELL//2
    y1 = (combo[0] // 3) * CELL + CELL//2
    x2 = (combo[2] % 3) * CELL + CELL//2
    y2 = (combo[2] // 3) * CELL + CELL//2
    canvas.create_line(x1, y1, x2, y2, width=8, fill="yellow")

def update_status():
    status.config(text=f"Turn: {current_turn}")
    score.config(text=f"Round {current_round}/{rounds} | "
                      f"{player_name}: {player_score} | "
                      f"{opponent_name}: {bot_score}")

# ===================== ROUND FLOW =====================
def end_round(result):
    global player_score, bot_score, current_round

    logger.info(
        f"Ending round {current_round} | Result={result} | "
        f"Score before update: {player_name}={player_score}, "
        f"{opponent_name}={bot_score}"
    )

    if result == player_symbol:
        player_score += 1
    elif result == bot_symbol:
        bot_score += 1

    logger.info(
        f"Score updated: {player_name}={player_score}, "
        f"{opponent_name}={bot_score}"
    )

    update_status()  # show correct score for THIS round

    if current_round >= rounds:
        end_game()
    else:
        current_round += 1
        reset_board()


def end_game():

    logger.info("Game over reached")

    if messagebox.askyesno("Game Over", "Start a new game?"):
        reset_all()
        show_setup()
    else:
        root.destroy()

# ===================== RESET =====================
def reset_board():
    global board, current_turn, move_count
    board = [""] * 9
    current_turn = "X"
    move_count = 0
    canvas.delete("all")

    for i in range(9):
        x1 = (i % 3) * CELL
        y1 = (i // 3) * CELL
        x2 = x1 + CELL
        y2 = y1 + CELL
        canvas.create_rectangle(x1, y1, x2, y2,
                                outline="white", width=2)

    update_status()

    if game_mode == "BOT" and current_turn == bot_symbol:
        root.after(50, bot_move)

def reset_all():
    global player_score, bot_score, current_round
    player_score = bot_score = 0
    current_round = 1

# ===================== INPUT =====================
def canvas_click(event):
    col = event.x // CELL
    row = event.y // CELL
    if col < 3 and row < 3:
        place_move(row * 3 + col)

canvas.bind("<Button-1>", canvas_click)

# ===================== INIT =====================
def init_game():
    game_frame.pack(fill="both", expand=True)
    reset_all()
    reset_board()

show_setup()
root.mainloop()


# ===============================================================================================

#====================================================================================
# To create a .exe file use below command
# python -m PyInstaller --onefile --noconsole D:\NEW_CODE_TEST\tic-tac-toe\tic_tac_toe20.py 
#  python -m PyInstaller --onefile --windowed D:\NEW_CODE_TEST\tic-tac-toe\tic_tac_toe18_final.py

# pyinstaller --onefile --noconsole tic_tac_toe.py
#--> onefile creates a single file
#--> nonconsole hides console window for GUI apps.
#--> output will be in dist/tic_tac_toe.exe

# pyinstaller --onefile --windowed tic_tac_toe.py
# creates dist/tic_tac_toe(a Mac .app bundle)
# QA can run on MAC
# Run with ./tic_tac_toe on Linux

#QA-release.zip
# ├── Windows/
# │    └── tic_tac_toe.exe
# ├── Mac/
# │    └── tic_tac_toe.app
# └── Linux/
#      └── tic_tac_toe (binary)