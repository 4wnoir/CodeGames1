# scoreboard.py
import tkinter as tk
from theme import get_theme
from base_frame import BaseGameFrame

# score_manager'dan dummy fonksiyonlar yerine gerçek fonksiyonları doğru şekilde import edin
try:
    from score_manager import get_top_scores_for_game
    print("DEBUG (scoreboard.py): get_top_scores_for_game başarıyla içe aktarıldı.")
except ImportError as e:
    print(f"HATA (scoreboard.py): score_manager içe aktarılamadı! Hata: {e}")
    print("Dummy get_top_scores_for_game fonksiyonu kullanılacak.")

    def get_top_scores_for_game(game_name, num_scores=5):
        print(f"[DUMMY] '{game_name}' için boş skorlar döndürülüyor (scoreboard.py).")
        return []

class ScoreBoardFrame(BaseGameFrame):
    def __init__(self, parent, controller, game_name_str=None):
        super().__init__(parent, controller, game_name_str)
        # game_name_mapping: Ana menüde gösterilen oyun adı ile score_manager'da kaydedilen oyun adının eşleşmesi
        self.game_name_mapping = {
            "🧩 Kod Hafızası": "Kod Hafızası",
            "🧠 Output Tahmini": "GuessOutput",
            "⚡ Syntax Rush": "SyntaxRush",
            "🔢 Sayı Tahmini": "NumberGuessGame",
            "✍️ Hızlı Yazma": "TypingGame",
        }
        self.header_label = None # Başlangıçta None olarak ayarla
        self.score_display_container = None
        self.canvas = None
        self.scrollbar = None
        self.inner_frame = None
        self.canvas_window_id = None
        self.back_button = None # Back button'ı da tutalım

        self.build_ui() # __init__ içinde UI'ı inşa et

    def build_ui(self):
        print("DEBUG (ScoreBoardFrame): build_ui başladı. Mevcut widget'lar yok ediliyor.")
        for widget in self.winfo_children():
            widget.destroy()  # Her defasında widget'ları temizle

        theme = get_theme()

        # Ana layout'u belirle
        self.grid_rowconfigure(0, weight=0)  # Header sabit
        self.grid_rowconfigure(1, weight=1)  # Skor alanı genişlesin
        self.grid_rowconfigure(2, weight=0)  # Geri tuşu sabit
        self.grid_columnconfigure(0, weight=1)  # Tek sütun genişlesin

        # Header Frame
        header_frame = tk.Frame(self, bg=theme["header_bg"])
        header_frame.grid(row=0, column=0, sticky="ew", pady=10)
        header_frame.grid_columnconfigure(0, weight=1)

        self.header_label = tk.Label(header_frame, text="En Yüksek Skorlar",
                                font=("Arial", 28, "bold"),
                                bg=theme["header_bg"], fg=theme["header_fg"])
        self.header_label.pack(expand=True)

        # Score Display Frame (Scrollable)
        self.score_display_container = tk.Frame(self, bg=theme["panel_bg"], bd=2, relief="groove")
        self.score_display_container.grid(row=1, column=0, sticky="nsew", padx=50, pady=20)
        self.score_display_container.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.score_display_container, bg=theme["panel_bg"], highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.score_display_container, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', self._on_canvas_configure) # Canvas boyutlandığında iç çerçeveyi ayarla

        self.inner_frame = tk.Frame(self.canvas, bg=theme["panel_bg"])
        self.canvas_window_id = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw", width=self.canvas.winfo_width())

        # İç çerçevenin boyutları değiştiğinde canvas'ın scroll bölgesini güncelle
        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Back Button
        self.back_button = tk.Button(self, text="Ana Menüye Dön", font=("Arial", 16),
                                command=lambda: self.controller.show_frame("MainMenu"),
                                bg=theme["button_bg"], fg=theme["button_fg"],
                                activebackground=theme["active_button_bg"],
                                activeforeground=theme["active_button_fg"])
        self.back_button.grid(row=2, column=0, pady=20)

        # İlk yüklemede ve tema değişiminde skorları güncelle
        self.update_score_display()
        self.apply_theme() # Temayı uygula
        print("DEBUG (ScoreBoardFrame): build_ui tamamlandı.")

    def _on_canvas_configure(self, event):
        """Canvas'ın genişliği değiştiğinde iç çerçevenin genişliğini ayarlar ve scrollregion'ı günceller."""
        print(f"DEBUG (ScoreBoardFrame): _on_canvas_configure çağrıldı. Yeni genişlik: {event.width}")
        if self.canvas_window_id:
            self.canvas.itemconfig(self.canvas_window_id, width=event.width)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


    def on_show(self):
        """Bu frame her gösterildiğinde çağrılacak metot."""
        print("DEBUG (ScoreBoardFrame): on_show çağrıldı. Skorlar ve tema güncelleniyor.")
        self.update_score_display()  # Skorları yeniden yükle ve göster
        self.apply_theme()  # Temayı yeniden uygula

    def update_score_display(self):
        print("DEBUG (ScoreBoardFrame): update_score_display başladı.")
        # Mevcut etiketleri temizle
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        theme = get_theme()
        row_idx = 0

        # Başlık etiketleri (Oyun Adı | Oyuncu Adı | Skor | Süre)
        # Bu etiketleri de bir listede tutarsak apply_theme'de kolayca güncelleyebiliriz
        self.score_header_labels = []
        self.score_header_labels.append(tk.Label(self.inner_frame, text="Oyun Adı", font=("Arial", 14, "bold"), bg=theme["panel_bg"], fg=theme["fg"]))
        self.score_header_labels[-1].grid(row=row_idx, column=0, sticky="w", padx=5, pady=2)
        self.score_header_labels.append(tk.Label(self.inner_frame, text="Oyuncu Adı", font=("Arial", 14, "bold"), bg=theme["panel_bg"], fg=theme["fg"]))
        self.score_header_labels[-1].grid(row=row_idx, column=1, sticky="w", padx=5, pady=2)
        self.score_header_labels.append(tk.Label(self.inner_frame, text="Skor", font=("Arial", 14, "bold"), bg=theme["panel_bg"], fg=theme["fg"]))
        self.score_header_labels[-1].grid(row=row_idx, column=2, sticky="e", padx=5, pady=2)
        self.score_header_labels.append(tk.Label(self.inner_frame, text="Süre", font=("Arial", 14, "bold"), bg=theme["panel_bg"], fg=theme["fg"]))
        self.score_header_labels[-1].grid(row=row_idx, column=3, sticky="e", padx=5, pady=2)


        # Sütun ağırlıkları - Skorbord içindeki kolonlar için
        self.inner_frame.grid_columnconfigure(0, weight=2)  # Oyun Adı
        self.inner_frame.grid_columnconfigure(1, weight=3)  # Oyuncu Adı
        self.inner_frame.grid_columnconfigure(2, weight=1)  # Skor
        self.inner_frame.grid_columnconfigure(3, weight=1)  # Süre

        row_idx += 1

        try:
            has_scores = False
            # Tüm tanımlı oyunlar için skorları çek
            for game_display_name, game_internal_name in self.game_name_mapping.items():
                print(f"DEBUG (ScoreBoardFrame): '{game_display_name}' ({game_internal_name}) için skorlar çekiliyor.")
                top_scores = get_top_scores_for_game(game_internal_name, num_scores=5)

                if top_scores:
                    has_scores = True
                    # Oyun başlığı
                    game_title_label = tk.Label(self.inner_frame, text=game_display_name, font=("Arial", 14, "bold"),
                                                bg=theme["panel_bg"], fg=theme["header_fg"])
                    game_title_label.grid(row=row_idx, column=0, columnspan=4, sticky="w", padx=5, pady=5)
                    row_idx += 1

                    for i, score_entry in enumerate(top_scores):
                        player_name = score_entry.get("player_name", "Anonim")
                        score_value = score_entry.get("score", 0)
                        time_taken = score_entry.get("time_taken")

                        formatted_time = ""
                        if time_taken is not None:
                            minutes = int(time_taken // 60)
                            secs = int(time_taken % 60)
                            formatted_time = f"{minutes:02}:{secs:02}"

                        print(
                            f"DEBUG (ScoreBoardFrame): {game_display_name} - Skor: {player_name}, {score_value}, {formatted_time}")

                        tk.Label(self.inner_frame, text=f"{i + 1}.", font=("Arial", 12), bg=theme["panel_bg"],
                                 fg=theme["fg"]).grid(row=row_idx, column=0, sticky="w", padx=5, pady=1)
                        tk.Label(self.inner_frame, text=player_name, font=("Arial", 12), bg=theme["panel_bg"],
                                 fg=theme["fg"]).grid(row=row_idx, column=1, sticky="w", padx=5, pady=1)
                        tk.Label(self.inner_frame, text=str(score_value), font=("Arial", 12), bg=theme["panel_bg"],
                                 fg=theme["fg"]).grid(row=row_idx, column=2, sticky="e", padx=5, pady=1)
                        tk.Label(self.inner_frame, text=formatted_time, font=("Arial", 12), bg=theme["panel_bg"],
                                 fg=theme["fg"]).grid(row=row_idx, column=3, sticky="e", padx=5, pady=1)
                        row_idx += 1
                    row_idx += 1  # Oyun grupları arasında boşluk bırak

            if not has_scores:
                no_score_label = tk.Label(self.inner_frame, text="Henüz hiçbir oyun için skor yok.",
                                          font=("Arial", 12), bg=theme["panel_bg"], fg=theme["fg"])
                no_score_label.grid(row=row_idx, column=0, columnspan=4, pady=5)
                print("DEBUG (ScoreBoardFrame): Henüz skor bulunamadı.")

        except Exception as e:
            print(f"HATA (ScoreBoardFrame): Skorlar yüklenirken bir sorun oluştu: {e}")
            error_label = tk.Label(self.inner_frame, text=f"Skor yüklenirken hata oluştu: {e}",
                                   font=("Arial", 12), bg=theme["panel_bg"], fg="red")
            error_label.grid(row=row_idx, column=0, columnspan=4, pady=5)

        self.inner_frame.update_idletasks()  # Çerçevenin boyutunu güncellemeyi zorla
        self.canvas.config(scrollregion=self.canvas.bbox("all"))  # Scrollbar'ı güncelle
        print("DEBUG (ScoreBoardFrame): update_score_display tamamlandı.")

    def apply_theme(self):
        print("DEBUG (ScoreBoardFrame): apply_theme başladı.")
        super().apply_theme()
        theme = get_theme()

        self.config(bg=theme["bg"])

        # Header Frame and Label
        if self.header_label and self.header_label.winfo_exists():
            self.header_label.config(bg=theme["header_bg"], fg=theme["header_fg"])
            if self.header_label.master: # Header frame'i de temalandır
                self.header_label.master.config(bg=theme["header_bg"])

        # Score Display Container and Canvas
        if self.score_display_container and self.score_display_container.winfo_exists():
            self.score_display_container.config(bg=theme["panel_bg"], bd=2, relief="groove")

        if self.canvas and self.canvas.winfo_exists():
            self.canvas.config(bg=theme["panel_bg"], highlightthickness=0)

        if self.inner_frame and self.inner_frame.winfo_exists():
            self.inner_frame.config(bg=theme["panel_bg"])
            # Inner frame içindeki tüm etiketleri güncelle
            for widget in self.inner_frame.winfo_children():
                if isinstance(widget, tk.Label):
                    current_font_str = widget.cget("font")
                    if "bold" in str(current_font_str).lower():
                        # Oyun başlıkları ve sütun başlıkları için özel renk
                        if widget["text"] in self.game_name_mapping.keys() or widget["text"] in ["Oyun Adı", "Oyuncu Adı", "Skor", "Süre"]:
                            widget.config(bg=theme["panel_bg"], fg=theme["header_fg"]) # Başlıklar için başlık rengi
                        else:
                            widget.config(bg=theme["panel_bg"], fg=theme["fg"]) # Normal yazı rengi
                    else:
                        widget.config(bg=theme["panel_bg"], fg=theme["fg"]) # Normal yazı rengi

        # Scrollbar
        if self.scrollbar and self.scrollbar.winfo_exists():
            self.scrollbar.config(troughcolor=theme["panel_bg"], bg=theme["button_bg"],
                                  activebackground=theme["active_button_bg"])

        # Back Button
        if self.back_button and self.back_button.winfo_exists():
            self.back_button.config(bg=theme["button_bg"], fg=theme["button_fg"],
                                  activebackground=theme["active_button_bg"],
                                  activeforeground=theme["active_button_fg"])
        print("DEBUG (ScoreBoardFrame): apply_theme tamamlandı.")