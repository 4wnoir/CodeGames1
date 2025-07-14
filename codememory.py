# codememory.py - Python Yazılım Dili Hafıza Oyunu (TÜM GÜNCELLEMELER DAHİL - DETAYLI DEBUGGING İÇİN)

import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import time

from theme import get_theme
from base_frame import BaseGameFrame

# score_manager modülünü içe aktarma
try:
    from score_manager import save_score, get_top_scores_for_game
    print("DEBUG: score_manager.py başarıyla içe aktarıldı.")
except ImportError as e:
    print(f"HATA: score_manager.py içe aktarılamadı! Hata: {e}")
    print(
        "Lütfen 'score_manager.py' dosyasının 'codememory.py' ile aynı klasörde olduğundan ve isminin doğru olduğundan emin olun.")
    print("Dummy save_score ve get_top_scores_for_game fonksiyonları KULLANILIYOR.")


    def save_score(game_name, player_name, score_value, is_time_score=False, elapsed_time=None):
        print(
            f"[DUMMY KAYIT] Oyun: {game_name}, Oyuncu: {player_name}, Skor: {score_value}, Zaman Skoru: {is_time_score}, Süre: {elapsed_time}")


    def get_top_scores_for_game(game_name, num_scores=5):
        print(f"[DUMMY KAYIT] {game_name} için en iyi {num_scores} skor isteniyor.")
        if game_name == "Kod Hafızası":
            return [
                {"player_name": "Anonim1", "score": 500, "time_taken": 120},
                {"player_name": "Anonim2", "score": 400, "time_taken": 150}
            ]
        return []


class CodeMemoryFrame(BaseGameFrame):
    def __init__(self, parent, controller, game_name_str=None):
        self.game_name = "Kod Hafızası"
        super().__init__(parent, controller, self.game_name)

        self.languages = ['Python', 'Java', 'JavaScript', 'C#', 'C++', 'PHP', 'SQL', 'HTML', 'CSS', 'C']

        self.cards_content = []
        self.card_buttons = []
        self.revealed_state = []
        self.matched_state = []

        self.first_choice_idx = None
        self.block_clicks = False

        self.score = 0
        self.start_time = 0
        self.elapsed_time = 0
        self.timer_id = None

        print("DEBUG: CodeMemoryFrame.__init__ çağrıldı.")
        self.build_ui()
        self.reset_game()
        print("DEBUG: CodeMemoryFrame.__init__ tamamlandı. UI kuruldu ve oyun sıfırlandı.")

    def build_ui(self):
        print("DEBUG: CodeMemoryFrame: build_ui başladı.")
        for widget in self.winfo_children():
            widget.destroy()
            print(f"DEBUG: Eski widget yok edildi: {widget}")

        theme = get_theme()
        print(f"DEBUG: Aktif tema: {theme.get('bg', 'N/A')}")

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)

        self.header_frame = tk.Frame(self, bg=theme["header_bg"])
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=10)
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_label = tk.Label(self.header_frame, text=self.game_name,
                                     font=("Arial", 28, "bold"),
                                     bg=theme["header_bg"], fg=theme["header_fg"])
        self.header_label.pack(expand=True)
        print("DEBUG: Header UI kuruldu.")

        self.game_area_frame = tk.Frame(self, bg=theme["panel_bg"])
        self.game_area_frame.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=20)
        self.game_area_frame.grid_rowconfigure(0, weight=1)
        self.game_area_frame.grid_rowconfigure(1, weight=0)
        self.game_area_frame.grid_rowconfigure(2, weight=1)
        self.game_area_frame.grid_columnconfigure(0, weight=1)
        self.game_area_frame.grid_columnconfigure(1, weight=0)
        self.game_area_frame.grid_columnconfigure(2, weight=1)

        self.inner_card_grid_frame = tk.Frame(self.game_area_frame, bg=theme["panel_bg"])
        self.inner_card_grid_frame.grid(row=1, column=1, sticky="nsew")
        print("DEBUG: Game area ve inner card grid frame kuruldu.")

        self.button_frame = tk.Frame(self, bg=theme["bg"])
        self.button_frame.grid(row=2, column=0, sticky="ew", padx=(20, 10), pady=10)
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)

        main_menu_button = tk.Button(self.button_frame, text="Ana Menü", font=("Arial", 16),
                                     command=lambda: self.controller.show_frame("MainMenu"),
                                     bg=theme["button_bg"], fg=theme["button_fg"],
                                     activebackground=theme["active_button_bg"],
                                     activeforeground=theme["active_button_fg"])
        main_menu_button.grid(row=0, column=0, padx=10, pady=5, sticky="e")

        reset_button = tk.Button(self.button_frame, text="Yeniden Başlat", font=("Arial", 16),
                                 command=self.reset_game,
                                 bg=theme["button_bg"], fg=theme["button_fg"],
                                 activebackground=theme["active_button_bg"],
                                 activeforeground=theme["active_button_fg"])
        reset_button.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        print("DEBUG: Butonlar kuruldu.")

        self.info_frame = tk.Frame(self, bg=theme["bg"])
        self.info_frame.grid(row=3, column=0, sticky="ew", padx=(20, 10), pady=10)
        self.info_frame.grid_columnconfigure(0, weight=1)
        self.info_frame.grid_columnconfigure(1, weight=1)
        self.score_label = tk.Label(self.info_frame, text="Skor: 0", font=("Arial", 18),
                                     bg=theme["bg"], fg=theme["fg"])
        self.score_label.grid(row=0, column=0, padx=10, sticky="w")
        self.time_label = tk.Label(self.info_frame, text="Süre: 00:00", font=("Arial", 18),
                                     bg=theme["bg"], fg=theme["fg"])
        self.time_label.grid(row=0, column=1, padx=10, sticky="e")
        print("DEBUG: Skor ve süre etiketleri kuruldu.")

        self.scoreboard_frame = tk.Frame(self, bg=theme["panel_bg"], bd=2, relief="groove")
        self.scoreboard_frame.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=(10, 20), pady=20)
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
        self.score_labels = []
        self.update_score_display()
        print("DEBUG: Skor tablosu UI kuruldu.")

        self.apply_theme()
        print("DEBUG: CodeMemoryFrame: build_ui tamamlandı.")

    def reset_game(self):
        print("DEBUG: CodeMemoryFrame: reset_game başladı.")
        if self.timer_id:
            self.after_cancel(self.timer_id)
            print("DEBUG: Mevcut zamanlayıcı iptal edildi.")

        self.score = 0
        self.elapsed_time = 0
        self.score_label.config(text="Skor: 0")
        self.time_label.config(text="Süre: 00:00")
        print("DEBUG: Skor ve süre sıfırlandı.")

        self.first_choice_idx = None
        self.block_clicks = False
        self.card_buttons = []
        self.revealed_state = []
        self.matched_state = []
        print("DEBUG: Oyun durumu değişkenleri sıfırlandı.")

        self.cards_content = self.languages * 2
        random.shuffle(self.cards_content)
        print(f"DEBUG: Kart içeriği hazırlandı. Toplam {len(self.cards_content)} kart.")

        # Mevcut kart butonlarını temizle (varsa)
        for widget in self.inner_card_grid_frame.winfo_children():
            widget.destroy()
            print(f"DEBUG: Eski kart butonu yok edildi: {widget}")
        print("DEBUG: Mevcut kart butonları temizlendi.")

        expected_cards = 20 # 4x5 ızgara için

        for r in range(4):
            self.inner_card_grid_frame.grid_rowconfigure(r, weight=1)
            for c in range(5):
                self.inner_card_grid_frame.grid_columnconfigure(c, weight=1)

                idx = r * 5 + c
                if idx < len(self.cards_content):
                    card_button = tk.Button(self.inner_card_grid_frame,
                                            text="?",
                                            font=("Arial", 16, "bold"),
                                            width=8, height=4,
                                            bg=get_theme()["card_back_color"],
                                            fg=get_theme()["card_text_color"],
                                            state=tk.NORMAL,
                                            command=lambda i=idx: self.on_card_click(i))
                    card_button.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")
                    self.card_buttons.append(card_button)
                    self.revealed_state.append(False)
                    self.matched_state.append(False)
                    print(
                        f"DEBUG: Kart {idx} (R:{r}, C:{c}) oluşturuldu. Text: '{card_button['text']}', BG: '{card_button['bg']}'")
                else:
                    print(
                        f"UYARI: Kart oluşturulurken index {idx} cards_content boyutunu ({len(self.cards_content)}) aştı.")

        print(f"DEBUG: reset_game: cards_content boyutu: {len(self.cards_content)}")
        print(f"DEBUG: reset_game: card_buttons boyutu: {len(self.card_buttons)}")
        print(f"DEBUG: reset_game: revealed_state boyutu: {len(self.revealed_state)}")
        print(f"DEBUG: reset_game: matched_state boyutu: {len(self.matched_state)}")

        if len(self.card_buttons) != expected_cards:
            print(
                f"HATA: Beklenen kart sayısı {expected_cards} iken, oluşturulan kart sayısı {len(self.card_buttons)}.")

        # UI'nin güncellenmesini zorlamak için after(1) kullanabiliriz (son çare)
        # self.after(100, lambda: self.update_idletasks()) # Gerekirse denenebilir, şimdilik yorumda kalsın

        self.start_time = time.time()
        self.update_timer()
        self.apply_theme()
        print("DEBUG: CodeMemoryFrame: reset_game tamamlandı. Kartlar hazırlandı ve tema uygulandı.")

    def on_show(self):
        print("DEBUG: CodeMemoryFrame: on_show çağrıldı. Oyunu sıfırlıyor ve skorları güncelliyor.")
        self.reset_game()
        self.update_score_display()

    def on_card_click(self, index):
        print(f"\nDEBUG: --- Tıklama Başladı --- Index: {index} ---")
        if (self.block_clicks or
                self.revealed_state[index] or
                self.matched_state[index] or
                self.card_buttons[index]['state'] == tk.DISABLED):
            print(
                f"DEBUG: Tıklama engellendi. Nedenleri: Blocked={self.block_clicks}, Revealed={self.revealed_state[index]}, Matched={self.matched_state[index]}, Tkinter State={self.card_buttons[index]['state']}")
            print(f"DEBUG: --- Tıklama Engellendi --- Index: {index} ---")
            return

        self.card_buttons[index].config(text=self.cards_content[index], bg=get_theme()["card_front_color"])
        self.revealed_state[index] = True
        print(f"DEBUG: Kart {index} açıldı. İçerik: {self.cards_content[index]}")

        if self.first_choice_idx is None:
            self.first_choice_idx = index
            print(f"DEBUG: İlk kart seçildi: {self.first_choice_idx}")
        else:
            if index == self.first_choice_idx:
                print(f"DEBUG: Aynı karta tekrar tıklandı: {index}. Kapatılıyor.")
                self.card_buttons[index].config(text="?", bg=get_theme()["card_back_color"])
                self.revealed_state[index] = False
                self.first_choice_idx = None
                print(f"DEBUG: --- Tıklama Bitti (Aynı Karta Tıklandı) --- Index: {index} ---")
                return

            self.block_clicks = True
            print(f"DEBUG: İkinci kart seçildi: {index}. Tıklamalar engellendi (block_clicks = True).")
            self.after(1500, self.check_match)
            print(f"DEBUG: --- Tıklama Bitti --- Index: {index} ---")

    def check_match(self):
        print("\nDEBUG: --- Eşleşme Kontrolü Başladı ---")
        idx1 = self.first_choice_idx

        if idx1 is None:
            print("HATA: check_match çağrıldı ancak first_choice_idx None! Tıklamalar tekrar etkinleştiriliyor.")
            self.block_clicks = False
            return

        revealed_indices = [i for i, state in enumerate(self.revealed_state) if state]

        if len(revealed_indices) != 2:
            print(
                f"UYARI: check_match sırasında açık kart sayısı 2 değil: {len(revealed_indices)}. Revealed: {self.revealed_state}")
            self._close_all_revealed_cards()
            print("DEBUG: --- Eşleşme Kontrolü Bitti (Hata Durumu) ---")
            return

        if idx1 not in revealed_indices:
            print(f"HATA: first_choice_idx ({idx1}) açık kartlar arasında değil! Düzeltiliyor.")
            self._close_all_revealed_cards()
            print("DEBUG: --- Eşleşme Kontrolü Bitti (Hata Durumu) ---")
            return

        revealed_indices.remove(idx1)
        idx2 = revealed_indices[0]

        card1_value = self.cards_content[idx1]
        card2_value = self.cards_content[idx2]

        if card1_value == card2_value:
            print(f"DEBUG: Eşleşme bulundu! {card1_value} - {card2_value} (İndeksler: {idx1}, {idx2})")
            self.score += 100
            self.score_label.config(text=f"Skor: {self.score}")
            self.card_buttons[idx1].config(text=self.cards_content[idx1], bg=get_theme()["matched_card_color"])
            self.card_buttons[idx2].config(text=self.cards_content[idx2], bg=get_theme()["matched_card_color"])
            self.after(50, lambda: self._finalize_matched_cards(idx1, idx2))
            print("DEBUG: Eşleşen kartlar için finalizasyon işlemi başlatıldı.")

        else:
            print(f"DEBUG: Eşleşme yok. {card1_value} - {card2_value} (İndeksler: {idx1}, {idx2})")
            self.after(100, lambda: self._close_unmatched_cards(idx1, idx2))

        print("DEBUG: check_match tamamlandı. Eşleşme sonrası beklenen işlem başlatıldı.")
        print(f"DEBUG: --- Eşleşme Kontrolü Bitti ---")

    def _close_all_revealed_cards(self):
        print("DEBUG: _close_all_revealed_cards: Tüm açık kartlar kapatılıyor.")
        theme = get_theme()
        for i, revealed in enumerate(self.revealed_state):
            if revealed and not self.matched_state[i]:
                self.card_buttons[i].config(text="?", bg=theme["card_back_color"], state=tk.NORMAL)
                self.revealed_state[i] = False
                print(f"DEBUG: Kart {i} kapatıldı.")
        self.first_choice_idx = None
        self.block_clicks = False
        print("DEBUG: _close_all_revealed_cards: Oyun durumu sıfırlandı.")

    def _finalize_matched_cards(self, idx1, idx2):
        print(f"\nDEBUG: _finalize_matched_cards: Kart {idx1} ve {idx2} için finalizasyon başladı.")
        self.card_buttons[idx1].config(state=tk.DISABLED)
        self.card_buttons[idx2].config(state=tk.DISABLED)
        print(f"DEBUG: Kart {idx1} ve {idx2} devre dışı bırakıldı.")
        self.revealed_state[idx1] = False
        self.revealed_state[idx2] = False
        self.matched_state[idx1] = True
        self.matched_state[idx2] = True
        print(f"DEBUG: matched_state güncellendi (True): {idx1}, {idx2}. Current matched_state: {self.matched_state}")
        self.first_choice_idx = None
        self.block_clicks = False
        print("DEBUG: Eşleşen kartlar devre dışı bırakıldı, tıklamalar tekrar etkin (block_clicks = False).")

        if all(self.matched_state):
            print("DEBUG: Tüm kartlar eşleşti! Oyun sonu.")
            if self.timer_id:
                self.after_cancel(self.timer_id)
            messagebox.showinfo("Tebrikler!",
                                f"Tüm çiftleri buldunuz! Skorunuz: {self.score}\nGeçen Süre: {self.format_time(self.elapsed_time)}",
                                parent=self)
            self.end_game()
        print(f"DEBUG: --- _finalize_matched_cards Bitti ---")

    def _close_unmatched_cards(self, idx1, idx2):
        print(f"\nDEBUG: _close_unmatched_cards: Kart {idx1} ve {idx2} kapatılıyor.")
        theme = get_theme()
        self.card_buttons[idx1].config(text="?", bg=theme["card_back_color"], state=tk.NORMAL)
        self.card_buttons[idx2].config(text="?", bg=theme["card_back_color"], state=tk.NORMAL)
        self.revealed_state[idx1] = False
        self.revealed_state[idx2] = False
        print(f"DEBUG: Kart {idx1} ve {idx2} kapatıldı ve durumu sıfırlandı.")
        self.first_choice_idx = None
        self.block_clicks = False
        print(f"DEBUG: Kartlar kapatıldı, tıklamalar tekrar etkin (block_clicks = False).")
        print(f"DEBUG: --- _close_unmatched_cards Bitti ---")

    def update_timer(self):
        self.elapsed_time = int(time.time() - self.start_time)
        self.time_label.config(text=f"Süre: {self.format_time(self.elapsed_time)}")
        self.timer_id = self.after(1000, self.update_timer)
        # print(f"DEBUG: Timer güncellendi: {self.format_time(self.elapsed_time)}") # Çok fazla çıktı üretir, gerekirse açın

    def format_time(self, seconds):
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02}:{secs:02}"

    def end_game(self):
        print("DEBUG: CodeMemoryFrame: end_game başladı.")
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None # timer_id'yi None yaparak tekrar iptal etmeyi engelle
        player_name = simpledialog.askstring("Skor Kaydet", "Lütfen adınızı girin:", parent=self)
        if player_name:
            save_score(self.game_name, player_name, self.score, is_time_score=False, elapsed_time=self.elapsed_time)
            messagebox.showinfo("Skor Kaydedildi",
                                f"Skorunuz: {self.score}\nGeçen Süre: {self.format_time(self.elapsed_time)}\nSkorunuz başarıyla kaydedildi!",
                                parent=self)
            self.update_score_display()
        else:
            messagebox.showinfo("Oyun Bitti",
                                f"Skorunuz: {self.score}\nGeçen Süre: {self.format_time(self.elapsed_time)}",
                                parent=self)
        self.controller.show_frame("MainMenu")
        print("DEBUG: CodeMemoryFrame: end_game tamamlandı.")

    def update_score_display(self):
        print("DEBUG: update_score_display çağrıldı.")
        for label in self.score_labels:
            if label.winfo_exists():
                label.destroy()
        self.score_labels.clear()

        theme = get_theme()
        # Buradaki self.game_name, CodeMemoryFrame'in __init__ metodunda "Kod Hafızası" olarak ayarlanmıştır.
        # Bu nedenle, get_top_scores_for_game fonksiyonu zaten sadece "Kod Hafızası" oyununun skorlarını çekecektir.
        top_scores = get_top_scores_for_game(self.game_name, num_scores=5)

        player_header = tk.Label(self.score_display_frame, text="Oyuncu Adı", font=("Arial", 14, "bold"),
                                 bg=theme["panel_bg"], fg=theme["fg"])
        player_header.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        score_header = tk.Label(self.score_display_frame, text="Skor", font=("Arial", 14, "bold"),
                                bg=theme["panel_bg"], fg=theme["fg"])
        score_header.grid(row=0, column=1, sticky="e", padx=5, pady=2)
        time_header = tk.Label(self.score_display_frame, text="Süre", font=("Arial", 14, "bold"),
                               bg=theme["panel_bg"], fg=theme["fg"])
        time_header.grid(row=0, column=2, sticky="e", padx=5, pady=2)
        self.score_display_frame.grid_columnconfigure(2, weight=1)
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
                time_taken = score_entry.get("time_taken")

                formatted_time = ""
                if time_taken is not None:
                    minutes = time_taken // 60
                    secs = time_taken % 60
                    formatted_time = f"{int(minutes):02}:{int(secs):02}"

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
        print("DEBUG: Skorlar gösterim için güncellendi.")

    def apply_theme(self):
        print("DEBUG: CodeMemoryFrame: apply_theme başladı.")
        super().apply_theme()
        theme = get_theme()
        print(f"DEBUG: apply_theme çağrıldı, tema: {theme.get('bg')}")

        self.config(bg=theme["bg"])
        if hasattr(self, 'header_frame') and self.header_frame.winfo_exists():
            self.header_frame.config(bg=theme["header_bg"])
        if hasattr(self, 'header_label') and self.header_label.winfo_exists():
            self.header_label.config(bg=theme["header_bg"], fg=theme["header_fg"])
        if hasattr(self, 'game_area_frame') and self.game_area_frame.winfo_exists():
            self.game_area_frame.config(bg=theme["panel_bg"])
        if hasattr(self, 'inner_card_grid_frame') and self.inner_card_grid_frame.winfo_exists():
            self.inner_card_grid_frame.config(bg=theme["panel_bg"])

        if hasattr(self, 'card_buttons') and self.card_buttons:
            for i, btn in enumerate(self.card_buttons):
                if btn.winfo_exists():
                    if self.matched_state[i]:
                        btn.config(text=self.cards_content[i], bg=theme["matched_card_color"],
                                   fg=theme["card_text_color"], state=tk.DISABLED)
                    elif self.revealed_state[i]:
                        btn.config(text=self.cards_content[i], bg=theme["card_front_color"],
                                   fg=theme["card_text_color"], state=tk.NORMAL)
                    else:
                        btn.config(text="?", bg=theme["card_back_color"], fg=theme["card_text_color"], state=tk.NORMAL)
            # print(f"DEBUG: Kart {i} tema uygulandı: Text='{btn['text']}', BG='{btn['bg']}'") # Çok fazla çıktı, gerekirse açın

        if hasattr(self, 'info_frame') and self.info_frame.winfo_exists():
            self.info_frame.config(bg=theme["bg"])
            self.score_label.config(bg=theme["bg"], fg=theme["fg"])
            self.time_label.config(bg=theme["bg"], fg=theme["fg"])

        if hasattr(self, 'button_frame') and self.button_frame.winfo_exists():
            self.button_frame.config(bg=theme["bg"])
            for widget in self.button_frame.winfo_children():
                if isinstance(widget, tk.Button):
                    widget.config(bg=theme["button_bg"], fg=theme["button_fg"],
                                  activebackground=theme["active_button_bg"],
                                  activeforeground=theme["active_button_fg"])

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
        print("DEBUG: CodeMemoryFrame: apply_theme tamamlandı.")
