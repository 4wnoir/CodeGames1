# guessoutput.py - GÜNCELLEME (Skor Tablosu Düzenlemesi)

import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import time

from theme import get_theme
from base_frame import BaseGameFrame

try:
    from score_manager import save_score, get_top_scores_for_game # get_top_scores_for_game added
except ImportError:
    print("score_manager.py could not be imported. Using dummy save_score and get_top_scores_for_game functions.")


    def save_score(game_name, player_name, score_value, is_time_score=True, elapsed_time=None): # elapsed_time added
        print(
            f"[Dummy Save] Game: {game_name}, Player: {player_name}, Score: {score_value}, Time Score: {is_time_score}, Duration: {elapsed_time}")


    def get_top_scores_for_game(game_name, num_scores=5):
        print(f"[Dummy Get] Top {num_scores} scores requested for {game_name}.")
        if game_name == "Çıktı Tahmini": # Dummy scores only for this game
            return [
                {"player_name": "Tahminci1", "score": 1500, "time_taken": 180},
                {"player_name": "Tahminci2", "score": 1200, "time_taken": 200},
                {"player_name": "Tahminci3", "score": 1000, "time_taken": 250}
            ]
        return []


class GuessOutputFrame(BaseGameFrame):
    def __init__(self, parent, controller, game_name_str=None):
        print("DEBUG_GO: GuessOutputFrame: __init__ started.")
        self.game_name = game_name_str if game_name_str else "Çıktı Tahmini"
        super().__init__(parent, controller, self.game_name)

        self.questions = [
            {"code": "print('Merhaba Dünya')", "output": "Merhaba Dünya"},
            {"code": "x = 5\ny = 10\nprint(x + y)", "output": "15"},
            {"code": "s = 'Python'\nprint(len(s))", "output": "6"},
            {"code": "liste = [1, 2, 3]\nliste.append(4)\nprint(liste[0])", "output": "1"},
            {"code": "def kare(n):\n return n * n\nprint(kare(7))", "output": "49"},
            {"code": "a = True\nb = False\nprint(a and b)", "output": "False"},
            {"code": "my_tuple = (10, 20, 30)\nprint(my_tuple[1])", "output": "20"},
            {"code": "for i in range(2):\n print('Tekrar')", "output": "Tekrar\nTekrar"},
            {"code": "text = 'Elma,Armut,Muz'\nparts = text.split(',')\nprint(parts[1])", "output": "Armut"},
            {"code": "sayi = 15\nif sayi > 10:\n print('Büyük')\nelse:\n print('Küçük')", "output": "Büyük"}
        ]
        self.current_question = {}
        self.score = 0
        self.question_count = 0
        self.start_time = None
        self.timer_running = False
        self.timer_id = None
        self.total_time_taken = 0
        self.current_question_start_time = 0
        self.score_labels = [] # List for scoreboard labels

        self.build_ui()
        self.reset_game() # Game is reset, which calls load_question.
        self.update_score_display() # Update scoreboard initially

        print("DEBUG_GO: GuessOutputFrame: __init__ completed.")

    def build_ui(self):
        print("DEBUG_GO: GuessOutputFrame: build_ui started.")
        for widget in self.winfo_children():
            widget.destroy()
            print(f"DEBUG_GO: Old widget destroyed: {widget}")

        theme = get_theme()
        print(f"DEBUG_GO: Active theme: {theme.get('bg', 'N/A')}")

        # Main window grid configuration: Left side game area, Right side scoreboard
        self.grid_rowconfigure(0, weight=0) # Header
        self.grid_rowconfigure(1, weight=1) # Main content area (for game and scoreboard)

        # ADJUSTED: Game area column (left) is now 3 units, Scoreboard column (right) is 1 unit
        self.grid_columnconfigure(0, weight=3) # main_content_frame for game area (left)
        self.grid_columnconfigure(1, weight=1) # scoreboard_frame (right)

        self.header_frame = tk.Frame(self, bg=theme["header_bg"])
        # Header spans both columns
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=10)
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_label = tk.Label(self.header_frame, text=self.game_name,
                                     font=("Arial", 28, "bold"),
                                     bg=theme["header_bg"], fg=theme["header_fg"])
        self.header_label.pack(expand=True)
        print("DEBUG_GO: Header UI built.")

        # Main content frame (will contain the game area)
        self.main_content_frame = tk.Frame(self, bg=theme["bg"])
        # This frame now occupies the left column
        self.main_content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        # Configure rows/columns within main_content_frame to center game_area_frame
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        print("DEBUG_GO: GuessOutputFrame: main_content_frame created and gridded.")

        # Game area frame - Actual game content, will be scaled down and centered
        self.game_area_frame = tk.Frame(self.main_content_frame, bd=2, relief="groove", bg=theme["panel_bg"])
        # ADJUSTED: place used to center and scale down within main_content_frame
        # relwidth=0.7, relheight=0.7 provides approximately half the area of its parent (0.49)
        self.game_area_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.7, relheight=0.7)
        # Grid configuration for widgets inside game_area_frame
        self.game_area_frame.grid_rowconfigure(0, weight=0)
        self.game_area_frame.grid_rowconfigure(1, weight=1) # Code area expands
        self.game_area_frame.grid_rowconfigure(2, weight=0)
        self.game_area_frame.grid_rowconfigure(3, weight=0)
        self.game_area_frame.grid_columnconfigure(0, weight=1)
        print("DEBUG_GO: GuessOutputFrame: game_area_frame created and placed inside main_content_frame.")

        # Info area (Score and Time)
        info_frame = tk.Frame(self.game_area_frame, bg=theme["panel_bg"])
        info_frame.grid(row=0, column=0, pady=15, sticky="ew")
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_columnconfigure(1, weight=1)

        self.score_label = tk.Label(info_frame, text="Skor: 0", font=("Arial", 22),
                                     bg=theme["panel_bg"], fg=theme["fg"])
        self.score_label.grid(row=0, column=0, padx=30, sticky="w")

        self.time_label = tk.Label(info_frame, text="Süre: 0s", font=("Arial", 22),
                                     bg=theme["panel_bg"], fg=theme["fg"])
        self.time_label.grid(row=0, column=1, padx=30, sticky="e")
        print("DEBUG_GO: GuessOutputFrame: Info labels created.")

        # Code display area
        self.code_display = tk.Text(self.game_area_frame, height=10, state="disabled", wrap="word",
                                   font=("Courier New", 28), relief="sunken", bd=1,
                                   bg=theme["code_bg"], fg=theme["code_fg"])
        self.code_display.grid(row=1, column=0, padx=30, pady=15, sticky="nsew")
        print("DEBUG_GO: GuessOutputFrame: Code display area created.")

        # Answer input area
        self.answer_entry = tk.Text(self.game_area_frame, height=5, font=("Arial", 24),
                                   relief="sunken", bd=1,
                                   bg=theme["input_bg"], fg=theme["input_fg"],
                                   insertbackground=theme["input_fg"])
        self.answer_entry.grid(row=2, column=0, padx=30, pady=15, sticky="ew")
        print("DEBUG_GO: GuessOutputFrame: Answer input area created.")

        # Buttons
        button_frame = tk.Frame(self.game_area_frame, bg=theme["panel_bg"])
        button_frame.grid(row=3, column=0, pady=15, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)

        main_menu_button = tk.Button(button_frame, text="Ana Menü", font=("Arial", 18),
                                     command=lambda: self.controller.show_frame("MainMenu"),
                                     bg=theme["button_bg"], fg=theme["button_fg"],
                                     activebackground=theme["active_button_bg"],
                                     activeforeground=theme["active_button_fg"])
        main_menu_button.grid(row=0, column=0, padx=(30, 15), pady=15, sticky="ew")

        self.check_button = tk.Button(button_frame, text="Cevabı Kontrol Et", font=("Arial", 18),
                                      command=self.check_answer,
                                      bg=theme["button_bg"], fg=theme["button_fg"],
                                      activebackground=theme["active_button_bg"],
                                      activeforeground=theme["active_button_fg"])
        self.check_button.grid(row=0, column=1, padx=15, pady=15, sticky="ew")

        self.next_button = tk.Button(button_frame, text="Yeni Soru", font=("Arial", 18),
                                     command=self.load_question, state=tk.DISABLED,
                                     bg=theme["button_bg"], fg=theme["button_fg"],
                                     activebackground=theme["active_button_bg"],
                                     activeforeground=theme["active_button_fg"])
        self.next_button.grid(row=0, column=2, padx=(15, 30), pady=15, sticky="ew")
        print("DEBUG_GO: GuessOutputFrame: Buttons created.")

        # Scoreboard frame - Placed in the right column
        self.scoreboard_frame = tk.Frame(self, bg=theme["panel_bg"], bd=2, relief="groove")
        # ADJUSTED: scoreboard_frame is still in column 1, but column weights have changed
        # It now spans from row 0 (header level) to row 1 (main content level) to take more vertical space
        self.scoreboard_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(10, 20), pady=20)
        self.scoreboard_frame.grid_columnconfigure(0, weight=1)
        self.scoreboard_frame.grid_rowconfigure(0, weight=0)
        self.scoreboard_frame.grid_rowconfigure(1, weight=1)
        scoreboard_title = tk.Label(self.scoreboard_frame, text="En İyi Skorlar",
                                     font=("Arial", 18, "bold"),
                                     bg=theme["panel_bg"], fg=theme["header_fg"])
        scoreboard_title.grid(row=0, column=0, pady=10, padx=10, sticky="n")
        self.score_display_frame = tk.Frame(self.scoreboard_frame, bg=theme["panel_bg"])
        self.score_display_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.score_display_frame.grid_columnconfigure(0, weight=1)
        self.score_display_frame.grid_columnconfigure(1, weight=1)
        self.score_display_frame.grid_columnconfigure(2, weight=1) # New column for time
        print("DEBUG_GO: Scoreboard UI built.")

        self.apply_theme()
        print("DEBUG_GO: GuessOutputFrame: build_ui completed.")

    def load_question(self):
        print("DEBUG_GO: load_question started.")
        if not self.questions:
            messagebox.showerror("Error", "No questions found to load. Please check the 'questions' list.",
                                 parent=self)
            print("ERROR_GO: Questions list is empty!")
            return

        self.current_question = random.choice(self.questions)
        print(f"DEBUG_GO: Selected question: {self.current_question['code'][:30]}...")

        if hasattr(self, 'code_display') and self.code_display.winfo_exists():
            print("DEBUG_GO: code_display exists, updating text.")
            self.code_display.config(state="normal")
            self.code_display.delete(1.0, tk.END)
            self.code_display.insert(tk.END, self.current_question["code"])
            self.code_display.config(state="disabled")
            print("DEBUG_GO: code_display text updated.")
        else:
            print("ERROR_GO: self.code_display object is missing or undefined! Question could not be displayed.")

        if hasattr(self, 'answer_entry') and self.answer_entry.winfo_exists():
            self.answer_entry.delete(1.0, tk.END)
            self.answer_entry.focus_set()
        else:
            print("ERROR_GO: self.answer_entry object is missing or undefined!")

        if hasattr(self, 'check_button') and self.check_button.winfo_exists():
            self.check_button.config(state=tk.NORMAL)
        if hasattr(self, 'next_button') and self.next_button.winfo_exists():
            self.next_button.config(state=tk.DISABLED)

        self.question_count += 1
        self.current_question_start_time = time.time()

        if not self.timer_running:
            self.start_timer()
        print(f"DEBUG_GO: Question loaded and UI updates made: {self.current_question['code'][:50]}...")
        print("DEBUG_GO: load_question completed.")

    def check_answer(self):
        print("DEBUG_GO: check_answer started.")
        if not hasattr(self, 'answer_entry') or not self.answer_entry.winfo_exists():
            print("ERROR_GO: Answer input field not found.")
            return

        user_answer = self.answer_entry.get(1.0, tk.END).strip()
        correct_output = self.current_question["output"].strip()

        user_answer_normalized = user_answer.replace('\r\n', '\n').strip()
        correct_output_normalized = correct_output.replace('\r\n', '\n').strip()

        print(f"DEBUG_GO: User answer: '{user_answer_normalized}'")
        print(f"DEBUG_GO: Correct answer: '{correct_output_normalized}'")

        if user_answer_normalized == correct_output_normalized:
            time_taken_for_question = time.time() - self.current_question_start_time
            points = max(0, 100 - int(time_taken_for_question * 5))
            self.score += points
            self.score_label.config(text=f"Skor: {self.score}")
            messagebox.showinfo("Correct!", f"Your answer is correct! (+{points} points)", parent=self)
            print(f"DEBUG_GO: Answer is correct. Score: {self.score}")
        else:
            self.score = max(0, self.score - 20)
            self.score_label.config(text=f"Skor: {self.score}")
            messagebox.showerror("Wrong!", f"Your answer is wrong. Correct answer:\n'{correct_output}'", parent=self)
            print(f"DEBUG_GO: Answer is wrong. Score: {self.score}")

        # Total elapsed time is used when saving score
        self.total_time_taken = int(time.time() - self.start_time)
        save_score(self.game_name, "Anonim", self.score, is_time_score=False, elapsed_time=self.total_time_taken)
        self.update_score_display() # Update scoreboard

        if hasattr(self, 'check_button') and self.check_button.winfo_exists():
            self.check_button.config(state=tk.DISABLED)
        if hasattr(self, 'next_button') and self.next_button.winfo_exists():
            self.next_button.config(state=tk.NORMAL)
        print("DEBUG_GO: check_answer completed.")

    def start_timer(self):
        print("DEBUG_GO: start_timer called.")
        if not self.timer_running:
            self.start_time = time.time()
            self.timer_running = True
            self.update_timer()

    def update_timer(self):
        if self.timer_running:
            elapsed_time = int(time.time() - self.start_time)
            self.time_label.config(text=f"Süre: {elapsed_time}s")
            self.timer_id = self.after(1000, self.update_timer)
            # print(f"DEBUG_GO: Timer updated: {elapsed_time}s") # Produces too much output, uncomment if needed

    def stop_timer(self):
        print("DEBUG_GO: stop_timer called.")
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_running = False
            self.timer_id = None

    def reset_game(self):
        print("DEBUG_GO: GuessOutputFrame: reset_game started.")
        self.stop_timer()
        self.score = 0
        self.question_count = 0
        self.total_time_taken = 0

        if hasattr(self, 'score_label') and self.score_label.winfo_exists():
            self.score_label.config(text="Skor: 0")
        if hasattr(self, 'time_label') and self.time_label.winfo_exists():
            self.time_label.config(text="Süre: 0s")

        # Clear code and answer areas and set their states
        if hasattr(self, 'code_display') and self.code_display.winfo_exists():
            self.code_display.config(state="normal")
            self.code_display.delete(1.0, tk.END)
            self.code_display.config(state="disabled")
        if hasattr(self, 'answer_entry') and self.answer_entry.winfo_exists():
            self.answer_entry.delete(1.0, tk.END)

        # Set button states
        if hasattr(self, 'check_button') and self.check_button.winfo_exists():
            self.check_button.config(state=tk.NORMAL)
        if hasattr(self, 'next_button') and self.next_button.winfo_exists():
            self.next_button.config(state=tk.DISABLED)

        self.load_question() # Load new question
        self.update_score_display() # Update scoreboard on reset
        print("DEBUG_GO: GuessOutputFrame: reset_game completed.")

    def on_show(self):
        print("DEBUG_GO: GuessOutputFrame: on_show called. Resetting game and updating scores.")
        self.reset_game()
        self.update_score_display() # Update scores whenever the frame is shown

    def update_score_display(self):
        print("DEBUG_GO: update_score_display called.")
        for label in self.score_labels:
            if label.winfo_exists():
                label.destroy()
        self.score_labels.clear()

        theme = get_theme()
        # Fetch scores only for this game
        top_scores = get_top_scores_for_game(self.game_name, num_scores=5)

        # Create headers (always visible)
        player_header = tk.Label(self.score_display_frame, text="Oyuncu Adı", font=("Arial", 14, "bold"),
                                 bg=theme["panel_bg"], fg=theme["fg"])
        player_header.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        score_header = tk.Label(self.score_display_frame, text="Skor", font=("Arial", 14, "bold"),
                                bg=theme["panel_bg"], fg=theme["fg"])
        score_header.grid(row=0, column=1, sticky="e", padx=5, pady=2)
        time_header = tk.Label(self.score_display_frame, text="Süre", font=("Arial", 14, "bold"),
                               bg=theme["panel_bg"], fg=theme["fg"])
        time_header.grid(row=0, column=2, sticky="e", padx=5, pady=2)
        self.score_labels.extend([player_header, score_header, time_header])

        if not top_scores:
            no_score_label = tk.Label(self.score_display_frame, text="Henüz skor yok.",
                                       font=("Arial", 12), bg=theme["panel_bg"], fg=theme["fg"])
            no_score_label.grid(row=1, column=0, columnspan=3, pady=5)
            self.score_labels.append(no_score_label)
        else:
            for i, score_entry in enumerate(top_scores):
                player_name = score_entry.get("player_name", "Anonim")
                score_value = score_entry.get("score", 0)
                time_taken = score_entry.get("time_taken") # Time information

                formatted_time = ""
                if time_taken is not None:
                    minutes = int(time_taken // 60)
                    secs = int(time_taken % 60)
                    formatted_time = f"{minutes:02}:{secs:02}"

                player_label = tk.Label(self.score_display_frame, text=player_name,
                                        font=("Arial", 12), bg=theme["panel_bg"], fg=theme["fg"])
                player_label.grid(row=i + 1, column=0, sticky="w", padx=5, pady=1)

                score_label = tk.Label(self.score_display_frame, text=str(score_value),
                                        font=("Arial", 12), bg=theme["panel_bg"], fg=theme["fg"])
                score_label.grid(row=i + 1, column=1, sticky="e", padx=5, pady=1)

                time_label = tk.Label(self.score_display_frame, text=formatted_time,
                                        font=("Arial", 12), bg=theme["panel_bg"], fg=theme["fg"])
                time_label.grid(row=i + 1, column=2, sticky="e", padx=5, pady=1)
                self.score_labels.extend([player_label, score_label, time_label])
        print("DEBUG_GO: Scores updated for display.")

    def apply_theme(self):
        print("DEBUG_GO: GuessOutputFrame: apply_theme started.")
        super().apply_theme() # Call BaseGameFrame's apply_theme
        theme = get_theme()
        print(f"DEBUG_GO: apply_theme called, theme: {theme.get('bg')}")

        self.config(bg=theme["bg"])
        if hasattr(self, 'header_frame') and self.header_frame.winfo_exists():
            self.header_frame.config(bg=theme["header_bg"])
        if hasattr(self, 'header_label') and self.header_label.winfo_exists():
            self.header_label.config(bg=theme["header_bg"], fg=theme["header_fg"])

        if hasattr(self, 'main_content_frame') and self.main_content_frame.winfo_exists():
            self.main_content_frame.config(bg=theme["bg"])

        if hasattr(self, 'game_area_frame') and self.game_area_frame.winfo_exists():
            self.game_area_frame.config(bg=theme["panel_bg"])

        info_frame = None
        if hasattr(self, 'score_label') and self.score_label.winfo_exists():
            info_frame = self.score_label.master
            self.score_label.config(bg=theme["panel_bg"], fg=theme["fg"])

        if hasattr(self, 'time_label') and self.time_label.winfo_exists():
            if not info_frame: info_frame = self.time_label.master
            self.time_label.config(bg=theme["panel_bg"], fg=theme["fg"])

        if info_frame and info_frame.winfo_exists():
            info_frame.config(bg=theme["panel_bg"])

        if hasattr(self, 'code_display') and self.code_display.winfo_exists():
            print(f"DEBUG_GO: code_display theme applied. BG: {theme.get('code_bg')}, FG: {theme.get('code_fg')}")
            self.code_display.config(bg=theme["code_bg"], fg=theme["code_fg"])
        else:
            print("ERROR_GO: apply_theme: code_display missing or not available.")

        if hasattr(self, 'answer_entry') and self.answer_entry.winfo_exists():
            self.answer_entry.config(bg=theme["input_bg"], fg=theme["input_fg"], insertbackground=theme["input_fg"])
        else:
            print("ERROR_GO: apply_theme: answer_entry missing or not available.")

        button_frame = None
        if hasattr(self, 'check_button') and self.check_button.winfo_exists():
            button_frame = self.check_button.master
            if button_frame and button_frame.winfo_exists():
                button_frame.config(bg=theme["panel_bg"]) # Theme the frame containing the buttons
                for btn in button_frame.winfo_children():
                    if isinstance(btn, tk.Button):
                        btn.config(bg=theme["button_bg"], fg=theme["button_fg"],
                                   activebackground=theme["active_button_bg"],
                                   activeforeground=theme["active_button_fg"])
            else:
                print("ERROR_GO: apply_theme: button_frame missing or not available.")
        else:
            print("ERROR_GO: apply_theme: check_button missing or not available.")

        # Scoreboard theming
        if hasattr(self, 'scoreboard_frame') and self.scoreboard_frame.winfo_exists():
            self.scoreboard_frame.config(bg=theme["panel_bg"])
            for widget in self.scoreboard_frame.winfo_children():
                if isinstance(widget, tk.Label) and widget["text"] == "En İyi Skorlar":
                    widget.config(bg=theme["panel_bg"], fg=theme["header_fg"])

        if hasattr(self, 'score_display_frame') and self.score_display_frame.winfo_exists():
            self.score_display_frame.config(bg=theme["panel_bg"])
            for label in self.score_labels:
                if label.winfo_exists():
                    label.config(bg=theme["panel_bg"], fg=theme["fg"])
        print("DEBUG_GO: GuessOutputFrame: apply_theme completed.")
