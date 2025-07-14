# syntaxrush.py - GÜNCELLENDİ (DEBUG ÇIKTILARI EKLENDİ)
import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import time

from theme import get_theme
from base_frame import BaseGameFrame

try:
    from score_manager import save_score
except ImportError:
    print("score_manager.py içe aktarılamadı. Dummy save_score fonksiyonu kullanılıyor.")


    def save_score(game_name, player_name, score_value, is_time_score=True):
        print(
            f"[Dummy Kayıt] Oyun: {game_name}, Oyuncu: {player_name}, Skor: {score_value}, Zaman Skoru: {is_time_score}")


class SyntaxRushFrame(BaseGameFrame):
    def __init__(self, parent, controller, game_name_str=None): # <-- BURASI DÜZELTİLDİ: game_name_str eklendi
        print("DEBUG_SR: SyntaxRushFrame: __init__ başladı.")
        # Eğer game_name_str belirtilmezse, varsayılan olarak "Syntax Rush" kullan
        self.game_name = game_name_str if game_name_str else "Syntax Rush"
        super().__init__(parent, controller, self.game_name) # <-- BURASI DÜZELTİLDİ: self.game_name BaseGameFrame'e iletildi

        self.questions = [
            {"code": "def greet(name):\n  print('Hello, ' + name))", "fix": "fazla parantez",
             "correct_code": "def greet(name):\n  print('Hello, ' + name)"},
            {"code": "for i in range(5\n  print(i)", "fix": "eksik parantez",
             "correct_code": "for i in range(5):\n  print(i)"},
            {"code": "x = 10\nif x > 5\n  print('Büyük')", "fix": "eksik iki nokta",
             "correct_code": "x = 10\nif x > 5:\n  print('Büyük')"},
            {"code": "my_list = [1, 2, 3]\nmy_list.add(4)", "fix": "add yerine append",
             "correct_code": "my_list = [1, 2, 3]\nmy_list.append(4)"},
            {"code": "print('Hello, World!'", "fix": "eksik tırnak", "correct_code": "print('Hello, World!')"},
            {"code": "def calculate(a, b):\n  return a * b\nprint(calculate(5, 3))", "fix": "hata yok",
             "correct_code": "def calculate(a, b):\n  return a * b\nprint(calculate(5, 3))"},
            {"code": "num = 10\nwhile num > 0:\nprint(num)", "fix": "eksik girinti",
             "correct_code": "num = 10\nwhile num > 0:\n  print(num)"},
            {"code": "class MyClass\n  def __init__(self):", "fix": "eksik iki nokta",
             "correct_code": "class MyClass:\n  def __init__(self):"},
            {"code": "value = input('Enter a number')\nprint(value + 5)", "fix": "tip dönüşümü",
             "correct_code": "value = int(input('Enter a number'))\nprint(value + 5)"},
            {"code": "import math\nprint(math.PI)", "fix": "büyük harf PI",
             "correct_code": "import math\nprint(math.pi)"}
        ]
        self.current_question = {}
        self.score = 0
        self.current_round = 0
        self.start_time = None
        self.timer_running = False
        self.timer_id = None
        self.is_question_active = False

        self.build_ui()
        self.reset_game() # Oyun sıfırlanır, bu da load_question'ı çağırır.

        print("DEBUG_SR: SyntaxRushFrame: __init__ tamamlandı.")

    def build_ui(self):
        print("DEBUG_SR: SyntaxRushFrame: build_ui başladı.")
        super().build_ui()
        theme = get_theme()

        # Başlık ve header_frame oluşturma (SyntaxRush'a özel)
        if not hasattr(self, 'header_frame') or not self.header_frame.winfo_exists():
            print("DEBUG_SR: Header frame/label yok, yeniden oluşturuluyor (beklenmedik).")
            self.header_frame = tk.Frame(self, bg=theme["header_bg"])
            self.header_frame.pack(side="top", fill="x", pady=10)
            self.header_label = tk.Label(self.header_frame, text=self.game_name,
                                         font=("Arial", 28, "bold"),
                                         bg=theme["header_bg"], fg=theme["header_fg"])
            self.header_label.pack(expand=True)
        else:
            print("DEBUG_SR: Header frame/label mevcut, sadece text güncelleniyor.")
            self.header_label.config(text=self.game_name)

        # Eski main_content_frame'i yok etmeden önce varsa
        if hasattr(self, 'main_content_frame') and self.main_content_frame.winfo_exists():
            print("DEBUG_SR: Eski main_content_frame yok ediliyor.")
            self.main_content_frame.destroy()

        self.main_content_frame = tk.Frame(self, bg=theme["bg"])
        self.main_content_frame.pack(side="top", fill="both", expand=True, padx=20, pady=20)
        print("DEBUG_SR: main_content_frame oluşturuldu ve pack edildi.")

        self.game_area_frame = tk.Frame(self.main_content_frame, bd=2, relief="groove", bg=theme["panel_bg"])
        self.game_area_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=1.0, relheight=1.0)
        print("DEBUG_SR: game_area_frame oluşturuldu ve main_content_frame içine place edildi.")

        self.game_area_frame.grid_rowconfigure(0, weight=0)
        self.game_area_frame.grid_rowconfigure(1, weight=1) # Soru alanı için genişleme
        self.game_area_frame.grid_rowconfigure(2, weight=0)
        self.game_area_frame.grid_rowconfigure(3, weight=0)
        self.game_area_frame.grid_columnconfigure(0, weight=1)

        # Bilgi alanı (Skor ve Süre)
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
        print("DEBUG_SR: Bilgi etiketleri oluşturuldu.")

        # Kod görüntüleme alanı
        self.code_display = tk.Text(self.game_area_frame, height=10, state="disabled", wrap="word",
                                    font=("Courier New", 28), relief="sunken", bd=1,
                                    bg=theme["code_bg"], fg=theme["code_fg"])
        self.code_display.grid(row=1, column=0, padx=30, pady=15, sticky="nsew")
        print("DEBUG_SR: Kod görüntüleme alanı oluşturuldu.")

        # Cevap/Düzeltme giriş alanı
        self.fix_entry = tk.Entry(self.game_area_frame, font=("Arial", 24),
                                  bg=theme["input_bg"], fg=theme["input_fg"],
                                  insertbackground=theme["input_fg"])
        self.fix_entry.grid(row=2, column=0, padx=30, pady=15, sticky="ew")
        self.fix_entry.bind("<Return>", lambda event: self.check_fix())
        print("DEBUG_SR: Düzeltme giriş alanı oluşturuldu.")

        # Butonlar
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

        self.check_button = tk.Button(button_frame, text="Kontrol Et", font=("Arial", 18),
                                      command=self.check_fix,
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
        print("DEBUG_SR: Butonlar oluşturuldu.")

        print("DEBUG_SR: SyntaxRushFrame: build_ui tamamlandı.")

    def load_question(self):
        print("DEBUG_SR: load_question başladı.")
        if not self.questions:
            messagebox.showerror("Hata", "Yüklenecek soru bulunamadı. Lütfen 'questions' listesini kontrol edin.",
                                 parent=self)
            print("HATA_SR: Sorular listesi boş!")
            return

        self.current_question = random.choice(self.questions)
        print(f"DEBUG_SR: Seçilen soru: {self.current_question['code'][:30]}...")

        if hasattr(self, 'code_display') and self.code_display.winfo_exists():
            print("DEBUG_SR: code_display mevcut, metin güncelleniyor.")
            self.code_display.config(state="normal")
            self.code_display.delete(1.0, tk.END)
            self.code_display.insert(tk.END, self.current_question["code"])
            self.code_display.config(state="disabled")
            print("DEBUG_SR: code_display metni güncellendi.")
        else:
            print("HATA_SR: self.code_display objesi yok veya tanımsız! Soru görüntülenemedi.")

        if hasattr(self, 'fix_entry') and self.fix_entry.winfo_exists():
            self.fix_entry.delete(0, tk.END)
            self.fix_entry.focus_set()
        else:
            print("HATA_SR: self.fix_entry objesi yok veya tanımsız!")

        if hasattr(self, 'check_button') and self.check_button.winfo_exists():
            self.check_button.config(state=tk.NORMAL)
        if hasattr(self, 'next_button') and self.next_button.winfo_exists():
            self.next_button.config(state=tk.DISABLED)

        self.current_round += 1
        self.current_question_start_time = time.time()

        if not self.timer_running:
            self.start_timer()
        self.is_question_active = True
        print(f"DEBUG_SR: Soru yüklendi ve UI güncellemeleri yapıldı: {self.current_question['code'][:50]}...")
        print("DEBUG_SR: load_question tamamlandı.")

    def check_fix(self):
        print("DEBUG_SR: check_fix başladı.")
        if not self.is_question_active:
            messagebox.showwarning("Uyarı", "Yeni bir soru yüklemeden cevap veremezsiniz.", parent=self)
            print("DEBUG_SR: Soru aktif değil, cevap engellendi.")
            return

        if not hasattr(self, 'fix_entry') or not self.fix_entry.winfo_exists():
            print("HATA_SR: Düzeltme girişi alanı bulunamadı.")
            return

        user_fix = self.fix_entry.get().strip()
        correct_fix_hint = self.current_question["fix"].strip()
        correct_code_full = self.current_question["correct_code"].strip()
        current_displayed_code = self.code_display.get(1.0, tk.END).strip()

        is_correct = False
        if correct_fix_hint.lower() == "hata yok":
            if user_fix.lower() == "hata yok" or user_fix.lower() == "doğru":
                is_correct = True
        else:
            # Kullanıcının cevabı ipucunu içeriyor mu VEYA
            # Kullanıcının düzeltmesini uyguladığımızda kod doğru koda eşit mi?
            is_correct = correct_fix_hint.lower() in user_fix.lower() or \
                         correct_code_full == current_displayed_code # Bu kısım biraz yanıltıcı olabilir,
                                                                     # çünkü kullanıcı kodu direkt düzeltmiyor,
                                                                     # sadece ipucunu yazıyor.
                                                                     # Genellikle sadece ipucu kontrolü yeterlidir.

        print(f"DEBUG_SR: Kullanıcı düzeltmesi: '{user_fix}'")
        print(f"DEBUG_SR: Doğru ipucu:        '{correct_fix_hint}'")
        print(f"DEBUG_SR: Doğru kod (tam):   '{correct_code_full}'")
        print(f"DEBUG_SR: Görünen kod:       '{current_displayed_code}'")


        if is_correct:
            self.score += 100
            self.score_label.config(text=f"Skor: {self.score}")
            messagebox.showinfo("Doğru!", "Düzeltmeniz doğru!", parent=self)
            print(f"DEBUG_SR: Cevap doğru. Skor: {self.score}")
        else:
            self.score = max(0, self.score - 50)
            self.score_label.config(text=f"Skor: {self.score}")
            messagebox.showerror("Yanlış!",
                                 f"Düzeltmeniz yanlış. İpucu: '{correct_fix_hint}'\nDoğru kod:\n{self.current_question['correct_code']}",
                                 parent=self)
            print(f"DEBUG_SR: Cevap yanlış. Skor: {self.score}")

        if hasattr(self, 'check_button') and self.check_button.winfo_exists():
            self.check_button.config(state=tk.DISABLED)
        if hasattr(self, 'next_button') and self.next_button.winfo_exists():
            self.next_button.config(state=tk.NORMAL)
        self.is_question_active = False
        print("DEBUG_SR: check_fix tamamlandı.")

    def start_timer(self):
        print("DEBUG_SR: start_timer başladı.")
        if not self.timer_running:
            self.start_time = time.time()
            self.timer_running = True
            self.update_timer()

    def update_timer(self):
        if self.timer_running:
            elapsed_time = int(time.time() - self.start_time)
            self.time_label.config(text=f"Süre: {elapsed_time}s")
            self.timer_id = self.after(1000, self.update_timer)

    def stop_timer(self):
        print("DEBUG_SR: stop_timer çağrıldı.")
        if self.timer_id:
            self.after_cancel(self.timer_id)
        self.timer_running = False
        self.timer_id = None

    def reset_game(self):
        print("DEBUG_SR: SyntaxRushFrame: reset_game başladı.")
        self.stop_timer()
        self.score = 0
        self.current_round = 0
        self.is_question_active = False

        if hasattr(self, 'score_label') and self.score_label.winfo_exists(): self.score_label.config(text="Skor: 0")
        if hasattr(self, 'time_label') and self.time_label.winfo_exists(): self.time_label.config(text="Süre: 0s")

        if hasattr(self, 'code_display') and self.code_display.winfo_exists():
            self.code_display.config(state="normal")
            self.code_display.delete(1.0, tk.END)
            self.code_display.config(state="disabled")
        else:
            print("HATA_SR: reset_game: code_display yok veya mevcut değil.")

        if hasattr(self, 'fix_entry') and self.fix_entry.winfo_exists():
            self.fix_entry.delete(0, tk.END)
        else:
            print("HATA_SR: reset_game: fix_entry yok veya mevcut değil.")

        if hasattr(self, 'check_button') and self.check_button.winfo_exists():
            self.check_button.config(state=tk.NORMAL)
        if hasattr(self, 'next_button') and self.next_button.winfo_exists():
            self.next_button.config(state=tk.DISABLED)

        self.load_question() # Yeni soruyu yükle
        print("DEBUG_SR: SyntaxRushFrame: reset_game tamamlandı.")

    def apply_theme(self):
        print("DEBUG_SR: SyntaxRushFrame: apply_theme başladı.")
        super().apply_theme()
        theme = get_theme()
        print(f"DEBUG_SR: apply_theme çağrıldı, tema: {theme.get('bg')}")

        # Header temalama
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
                print(f"DEBUG_SR: code_display teması uygulanıyor. BG: {theme.get('code_bg')}, FG: {theme.get('code_fg')}")
                self.code_display.config(bg=theme["code_bg"], fg=theme["code_fg"])
            else:
                print("HATA_SR: apply_theme: code_display yok veya mevcut değil.")

            if hasattr(self, 'fix_entry') and self.fix_entry.winfo_exists():
                self.fix_entry.config(bg=theme["input_bg"], fg=theme["input_fg"], insertbackground=theme["input_fg"])
            else:
                print("HATA_SR: apply_theme: fix_entry yok veya mevcut değil.")

            button_frame = None
            if hasattr(self, 'check_button') and self.check_button.winfo_exists():
                button_frame = self.check_button.master
                if button_frame and button_frame.winfo_exists():
                    button_frame.config(bg=theme["panel_bg"])
                    for btn in button_frame.winfo_children():
                        if isinstance(btn, tk.Button):
                            btn.config(bg=theme["button_bg"], fg=theme["button_fg"],
                                       activebackground=theme["active_button_bg"],
                                       activeforeground=theme["active_button_fg"])
                else:
                    print("HATA_SR: apply_theme: button_frame yok veya mevcut değil.")
            else:
                print("HATA_SR: apply_theme: check_button yok veya mevcut değil.")

            print("DEBUG_SR: SyntaxRushFrame: apply_theme tamamlandı.")