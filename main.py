# main.py - "Bilinmeyen Oyun" Başlığı ve Score Manager Uyumluluğu İçin Güncel Çözüm
import tkinter as tk
from tkinter import messagebox, ttk # ttk hala gerekli olabilir, bu yüzden bırakıldı
import random  # Bu belki kullanılmıyor olabilir, ama kalsın
import time  # Bu da belki kullanılmıyor olabilir, ama kalsın
import os
from datetime import datetime # Tarih formatlama için ekli olduğundan emin olun

# theme modülünden gerekli fonksiyonları içe aktar
from theme import get_theme, set_theme, get_all_theme_names, get_current_theme_name # toggle_theme yerine yenileri

from base_frame import BaseGameFrame

# --- score_manager modülünü içe aktırma ---
# Artık get_scores yerine get_top_scores_for_game ve save_score'u alıyoruz.
try:
    from score_manager import save_score, get_top_scores_for_game, delete_score # delete_score da burada olmalı
    print("DEBUG: score_manager.py başarıyla içe aktarıldı (main.py).")
except ImportError as e:
    print(f"HATA: score_manager.py içe aktarılamadı (main.py)! Hata: {e}")
    print(
        "Lütfen 'score_manager.py' dosyasının 'main.py' ile aynı klasörde olduğundan ve isminin doğru olduğundan emin olun.")
    print("Dummy save_score ve get_top_scores_for_game fonksiyonları KULLANILIYOR.")

    # Dummy fonksiyonlar, elapsed_time parametresini de içerecek şekilde güncellendi
    def save_score(game_name, player_name, score_value, is_time_score=False, elapsed_time=None):
        print(
            f"[Dummy Kayıt - main.py] Oyun: {game_name}, Oyuncu: {player_name}, Skor: {score_value}, Zaman Skoru: {is_time_score}, Süre: {elapsed_time}")

    def get_top_scores_for_game(game_name, num_scores=5):
        print(f"[Dummy Get - main.py] {game_name} için boş/sahte skorlar döndürülüyor.")
        return []
    def delete_score(game_name, player_name=""):
        print(f"[Dummy Silme - main.py] Oyun: {game_name}, Oyuncu: {player_name if player_name else 'TÜM oyuncular'} skoru silindi (sahte).")
        return True, "Skor başarıyla silindi (dummy)."


# --- PlaceholderGameFrame ---
# Eğer bir oyun dosyası bulunamazsa veya geliştirilmemişse gösterilecek yer tutucu frame
class PlaceholderGameFrame(BaseGameFrame):
    def __init__(self, parent, controller, game_name_str): # game_name_str BURADA KABUL EDİLİYOR
        self.game_name = game_name_str  # Gösterilecek oyun adı
        super().__init__(parent, controller, game_name_str) # BaseGameFrame'e de game_name_str'ı iletiyoruz
        self.build_ui()

    def build_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        theme = get_theme()
        self.config(bg=theme["bg"]) # Kendi arka planını ayarlar

        self.header_frame = tk.Frame(self, bg=theme["header_bg"])
        self.header_frame.pack(side="top", fill="x", pady=10)
        self.header_label = tk.Label(self.header_frame, text=self.game_name,
                                     font=("Arial", 28, "bold"),
                                     bg=theme["header_bg"], fg=theme["header_fg"])
        self.header_label.pack(expand=True)

        self.main_content_frame = tk.Frame(self, bg=theme["bg"])
        self.main_content_frame.pack(side="top", fill="both", expand=True, padx=20, pady=20)

        error_content_frame = tk.Frame(self.main_content_frame, bg=theme["panel_bg"])
        error_content_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(error_content_frame, text=f"Oyun '{self.game_name}' henüz geliştirilmedi!", font=("Arial", 24, "bold"),
                 fg=theme["fg"], bg=theme["panel_bg"]).pack(pady=50)
        tk.Button(error_content_frame, text="Ana Menüye Dön", command=lambda: self.controller.show_frame("MainMenu"),
                  font=("Arial", 16), bg=theme["button_bg"], fg=theme["button_fg"],
                  activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"]).pack(pady=20)

        self.apply_theme() # Build_ui sonunda temayı uygula

    def apply_theme(self):
        super().apply_theme() # BaseGameFrame'in tema uygulamasını çağırır
        theme = get_theme()

        self.config(bg=theme["bg"]) # Kendi arka planını günceller

        if hasattr(self, 'header_frame') and self.header_frame.winfo_exists():
            self.header_frame.config(bg=theme["header_bg"])
        if hasattr(self, 'header_label') and self.header_label.winfo_exists():
            self.header_label.config(bg=theme["header_bg"], fg=theme["header_fg"])

        if hasattr(self, 'main_content_frame') and self.main_content_frame.winfo_exists():
            self.main_content_frame.config(bg=theme["bg"])
            for widget in self.main_content_frame.winfo_children():
                if isinstance(widget, tk.Frame):
                    widget.config(bg=theme["panel_bg"]) # error_content_frame
                    for sub_widget in widget.winfo_children():
                        if isinstance(sub_widget, tk.Label):
                            sub_widget.config(bg=theme["panel_bg"], fg=theme["fg"])
                        elif isinstance(sub_widget, tk.Button):
                            sub_widget.config(bg=theme["button_bg"], fg=theme["button_fg"],
                                              activebackground=theme["active_button_bg"],
                                              activeforeground=theme["active_button_fg"])


# --- Oyuna Özel Frame İçe Aktarımları ---
# Her oyunu try-except bloğu içinde import ederek yoksa PlaceholderGameFrame kullanırız
try:
    from codememory import CodeMemoryFrame
except ImportError:
    print("codememory.py bulunamadı. 'Kod Hafızası' için yer tutucu kullanılıyor.")
    CodeMemoryFrame = PlaceholderGameFrame

try:
    from guessoutput import GuessOutputFrame
except ImportError:
    print("guessoutput.py bulunamadı. 'Output Tahmini' için yer tutucu kullanılıyor.")
    GuessOutputFrame = PlaceholderGameFrame

try:
    from syntaxrush import SyntaxRushFrame
except ImportError:
    print("syntaxrush.py bulunamadı. 'Syntax Rush' için yer tutucu kullanılıyor.")
    SyntaxRushFrame = PlaceholderGameFrame

# Scoreboard, Feedback ve YENİ Admin frame'leri her zaman olmalı
from scoreboard import ScoreBoardFrame
from feedback_frame import FeedbackFrame

# YENİ EKLENEN ADMIN MODÜLLERİ
from admin_login_frame import AdminLoginFrame
from admin_panel import AdminPanelFrame # admin_frame.py yerine admin_panel.py kullanılıyor
from question_editor_frame import QuestionEditorFrame # YENİ: QuestionEditorFrame import edildi


# --- MainMenuFrame ---
class MainMenuFrame(BaseGameFrame):
    def __init__(self, parent, controller): # style_obj parametresi kaldırıldı
        # game_name_str'i burada kullanmıyoruz, ana menü için sabit bir başlığımız var.
        super().__init__(parent, controller) # Placeholder gibi game_name_str göndermiyoruz
        self.game_name = "🧠 Kodlama Oyunları"  # Ana menü başlığı
        # self.style = style_obj # Style objesi saklama kaldırıldı
        self.build_ui()

    def build_ui(self):
        print("MainMenuFrame: build_ui başladı.")
        for widget in self.winfo_children():
            widget.destroy()

        super().build_ui()  # BaseGameFrame'deki temayı ayarlar
        theme = get_theme()

        self.header_frame = tk.Frame(self, bg=theme["header_bg"])
        self.header_frame.pack(side="top", fill="x", pady=10)

        self.header_label = tk.Label(self.header_frame, text=self.game_name,  # self.game_name kullanıldı
                                     font=("Arial", 28, "bold"),
                                     bg=theme["header_bg"], fg=theme["header_fg"])
        self.header_label.pack(expand=True)

        # Hata düzeltildi: self.notebook yerine self kullanıldı
        self.menu_content_frame = tk.Frame(self, bg=theme["bg"])
        self.menu_content_frame.pack(fill="both", expand=True)

        # Oyun listesi - (Görünen İsim, Açıklama, Dahili Anahtar)
        games = [
            ("🧩 Kod Hafızası", "Yazılım dillerini ezberlemeye dayalı hafıza oyunu", "CodeMemory"),
            ("🧠 Output Tahmini", "Kod çıktısını tahmin etmeye yönelik oyun", "GuessOutput"),
            ("⚡ Syntax Rush", "Hatalı kodları düzelt! Syntax bilgini test et", "SyntaxRush"),
            ("🔢 Sayı Tahmini", "Basit bir sayı tahmin oyunu", "NumberGuessGame"),
            ("✍️ Hızlı Yazma", "Klavyede ne kadar hızlısın?", "TypingGame"),
        ]

        game_buttons_frame = tk.Frame(self.menu_content_frame, bg=theme["bg"])
        game_buttons_frame.pack(pady=15)

        for i, (name, desc, key) in enumerate(games):
            # Oyun kartı konteynerini temadan gelen renkle oluştur
            game_button_container = tk.Frame(game_buttons_frame, bg=theme["game_card_bg"], bd=1, relief="solid")
            game_button_container.grid(row=i // 2, column=i % 2, pady=10, padx=15, sticky="ew")

            # Oyun adı ve açıklamasını temadan gelen renkle oluştur
            tk.Label(game_button_container, text=name, font=("Arial", 16, "bold"),
                     bg=theme["game_card_bg"], fg=theme["game_card_fg"]).pack(anchor="w", padx=15, pady=5)
            tk.Label(game_button_container, text=desc, font=("Arial", 12),
                     fg=theme["game_card_fg"], bg=theme["game_card_bg"], wraplength=300).pack(anchor="w", padx=15)

            # show_frame'e oyunun görünen adını (name) ve dahili anahtarını (key) gönderiyoruz.
            command = lambda k=key, n=name: self.controller.show_frame(k, game_name_str=n)

            # Oyna düğmesini temadan gelen renkle oluştur
            tk.Button(game_button_container, text="▶ Oyna", font=("Arial", 12),
                      bg=theme["play_button_bg"], fg=theme["play_button_fg"],
                      activebackground=theme["active_play_button_bg"], activeforeground=theme["active_play_button_fg"],
                      command=command).pack(side="right", padx=15, pady=10)

            game_button_container.grid_columnconfigure(0, weight=1)

        tk.Button(self.menu_content_frame, text="🌗 Tema Değiştir", font=("Arial", 14),
                  bg=theme["button_bg"], fg=theme["button_fg"],
                  activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"],
                  command=self.controller.handle_theme_toggle).pack(pady=15)

        tk.Button(self.menu_content_frame, text="💬 Geri Bildirim", font=("Arial", 14),
                  bg=theme["button_bg"], fg=theme["button_fg"],
                  activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"],
                  command=lambda: self.controller.show_frame("Feedback")).pack(pady=10)

        tk.Button(self.menu_content_frame, text="🏆 Skorlar", font=("Arial", 14),
                  bg=theme["button_bg"], fg=theme["button_fg"],
                  activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"],
                  command=lambda: self.controller.show_frame("ScoreBoard")).pack(pady=10)

        # YENİ ADMIN BUTONU
        tk.Button(self.menu_content_frame, text="⚙️ Admin Paneli", font=("Arial", 14),
                  bg=theme["button_bg"], fg=theme["button_fg"],
                  activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"],
                  command=lambda: self.controller.show_frame("AdminLogin")).pack(
            pady=10)  # Admin giriş ekranına yönlendir

        tk.Button(self.menu_content_frame, text="❌ Çıkış", font=("Arial", 14),
                  bg=theme["button_bg"], fg=theme["button_fg"],
                  activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"],
                  command=self.controller.quit).pack(pady=15)

        self.apply_theme()
        print("MainMenuFrame: build_ui tamamlandı.")

    def on_show(self):
        print("DEBUG: MainMenuFrame: on_show çağrıldı.")
        self.apply_theme()
        # Combobox kaldırıldığı için bu kısım artık gerekli değil
        print("DEBUG: MainMenuFrame: on_show tamamlandı.")

    def apply_theme(self):
        print("MainMenuFrame: apply_theme başladı.")
        super().apply_theme()
        theme = get_theme()
        print(f"DEBUG: MainMenuFrame.apply_theme - Current theme name: {get_current_theme_name()}")
        print(f"DEBUG: MainMenuFrame.apply_theme - theme['bg']: {theme.get('bg')}")
        print(f"DEBUG: MainMenuFrame.apply_theme - theme['game_card_bg']: {theme.get('game_card_bg')}")
        print(f"DEBUG: MainMenuFrame.apply_theme - theme['game_card_fg']: {theme.get('game_card_fg')}")
        print(f"DEBUG: MainMenuFrame.apply_theme - theme['play_button_bg']: {theme.get('play_button_bg')}")
        print(f"DEBUG: MainMenuFrame.apply_theme - theme['play_button_fg']: {theme.get('play_button_fg')}")


        self.config(bg=theme["bg"])

        if hasattr(self, 'header_frame') and self.header_frame.winfo_exists():
            self.header_frame.config(bg=theme["header_bg"])
        if hasattr(self, 'header_label') and self.header_label.winfo_exists():
            self.header_label.config(bg=theme["header_bg"], fg=theme["header_fg"])

        if hasattr(self, 'menu_content_frame') and self.menu_content_frame.winfo_exists():
            self.menu_content_frame.config(bg=theme["bg"])
            for widget in self.menu_content_frame.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.config(bg=theme["bg"], fg=theme["fg"])
                    print(f"DEBUG: MainMenuFrame.apply_theme - Label (main) bg/fg: {widget.cget('bg')}/{widget.cget('fg')}")
                elif isinstance(widget, tk.Frame): # game_buttons_frame ve game_button_container'lar
                    print(f"DEBUG: MainMenuFrame.apply_theme - Processing frame: {widget.winfo_name()}")
                    widget.config(bg=theme["bg"]) # game_buttons_frame'in arka planı
                    print(f"DEBUG: MainMenuFrame.apply_theme - game_buttons_frame bg: {widget.cget('bg')}")
                    for sub_widget in widget.winfo_children():
                        if isinstance(sub_widget, tk.Frame): # game_button_container
                            print(f"DEBUG: MainMenuFrame.apply_theme - Setting game_card_bg for {sub_widget.winfo_name()}: {theme.get('game_card_bg')}")
                            sub_widget.config(bg=theme["game_card_bg"]) # Oyun kartı arka planı
                            print(f"DEBUG: MainMenuFrame.apply_theme - game_button_container bg: {sub_widget.cget('bg')}")
                            for inner_widget in sub_widget.winfo_children():
                                if isinstance(inner_widget, tk.Label):
                                    print(f"DEBUG: MainMenuFrame.apply_theme - Setting label bg/fg for {inner_widget.winfo_name()}: {theme.get('game_card_bg')}/{theme.get('game_card_fg')}")
                                    inner_widget.config(bg=theme["game_card_bg"], fg=theme["game_card_fg"]) # Oyun kartı metin rengi
                                    print(f"DEBUG: MainMenuFrame.apply_theme - Inner label bg/fg: {inner_widget.cget('bg')}/{inner_widget.cget('fg')}")
                                elif isinstance(inner_widget, tk.Button): # Oyna düğmesi
                                    print(f"DEBUG: MainMenuFrame.apply_theme - Setting play_button bg/fg for {inner_widget.winfo_name()}: {theme.get('play_button_bg')}/{theme.get('play_button_fg')}")
                                    inner_widget.config(bg=theme["play_button_bg"], fg=theme["play_button_fg"],
                                                        activebackground=theme["active_play_button_bg"],
                                                        activeforeground=theme["active_play_button_fg"])
                                    print(f"DEBUG: MainMenuFrame.apply_theme - Play button bg/fg: {inner_widget.cget('bg')}/{inner_widget.cget('fg')}")
                        elif isinstance(sub_widget, tk.Button): # Diğer ana menü butonları
                            print(f"DEBUG: MainMenuFrame.apply_theme - Setting button bg/fg for {sub_widget.winfo_name()}: {theme.get('button_bg')}/{theme.get('button_fg')}")
                            sub_widget.config(bg=theme["button_bg"], fg=theme["button_fg"],
                                              activebackground=theme["active_button_bg"],
                                              activeforeground=theme["active_button_fg"])
                            print(f"DEBUG: MainMenuFrame.apply_theme - Sub-button bg/fg: {sub_widget.cget('bg')}/{sub_widget.cget('fg')}")
                elif isinstance(widget, tk.Button): # Ana menüdeki diğer düğmeler (Tema Değiştir, Geri Bildirim vb.)
                    print(f"DEBUG: MainMenuFrame.apply_theme - Setting main menu button bg/fg for {widget.winfo_name()}: {theme.get('button_bg')}/{theme.get('button_fg')}")
                    widget.config(bg=theme["button_bg"], fg=theme["button_fg"],
                                  activebackground=theme["active_button_bg"],
                                  activeforeground=theme["active_button_fg"])
                    print(f"DEBUG: MainMenuFrame.apply_theme - Main menu button bg/fg: {widget.cget('bg')}/{widget.cget('fg')}")
        print("MainMenuFrame: apply_theme tamamlandı.")


# --- App Class (Ana Uygulama) ---
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🧠 Kodlama Oyunları")
        self.attributes('-fullscreen', True)
        self.bind("<Escape>", self.toggle_fullscreen)

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.current_frame_instance = None

        # self.style = ttk.Style() # ttk.Style objesi kaldırıldı, çünkü MainMenuFrame'e artık iletilmiyor

        self.frames_classes = {
            "MainMenu": MainMenuFrame,
            "CodeMemory": CodeMemoryFrame,
            "GuessOutput": GuessOutputFrame,
            "SyntaxRush": SyntaxRushFrame,
            "ScoreBoard": ScoreBoardFrame,
            "Feedback": FeedbackFrame,
            "AdminLogin": AdminLoginFrame,
            "AdminPanel": AdminPanelFrame,
            "QuestionEditor": QuestionEditorFrame,  # YENİ: frames_classes'a eklendi
            "NumberGuessGame": PlaceholderGameFrame,
            "TypingGame": PlaceholderGameFrame,
        }

        self.show_frame("MainMenu")

    def show_frame(self, name, game_name_str=None):
        print(f"DEBUG (App): show_frame('{name}', game_name_str='{game_name_str}') çağrıldı.")

        if self.current_frame_instance:
            print(f"DEBUG (App): Önceki frame ({self.current_frame_instance.__class__.__name__}) yok ediliyor.")
            self.current_frame_instance.destroy()
            self.current_frame_instance = None
            print(f"DEBUG (App): Önceki frame yok edildi.")

        frame_class = self.frames_classes.get(name)
        new_frame_instance = None

        if frame_class:
            if frame_class is PlaceholderGameFrame:
                new_frame_instance = PlaceholderGameFrame(self.container, self,
                                                          game_name_str if game_name_str else name)
            # MainMenu, ScoreBoard, Feedback, AdminLogin, AdminPanel ve QuestionEditor için game_name_str'e gerek yok
            elif name in ["MainMenu", "ScoreBoard", "Feedback", "AdminLogin", "AdminPanel",
                          "QuestionEditor"]:  # YENİ: QuestionEditor eklendi
                new_frame_instance = frame_class(self.container, self)
            else:  # Diğer oyun frame'leri için game_name_str'i iletiyoruz
                new_frame_instance = frame_class(self.container, self, game_name_str)
        else:
            messagebox.showerror("Hata", f"Bilinmeyen frame tipi: {name}. Uygulama kapatılıyor.")
            self.quit()
            return

        if new_frame_instance:
            self.current_frame_instance = new_frame_instance
            self.current_frame_instance.pack(fill="both", expand=True)
            print(f"DEBUG (App): Yeni frame ({name}) pack edildi.")

            # Her frame'in kendi __init__ içinde build_ui'ı çağrıldığı varsayılır.
            # on_show metodu, frame her gösterildiğinde özel güncellemeler yapmak için kullanılır.
            if hasattr(new_frame_instance, 'on_show') and callable(new_frame_instance.on_show):
                print(f"DEBUG (App): {name} için on_show çağrılıyor.")
                new_frame_instance.on_show()
            else:
                # Eğer on_show yoksa, build_ui ve apply_theme'i manuel çağır
                # (Çoğu durumda __init__ içinde zaten çağrıldığı için bu yedek bir durumdur.)
                new_frame_instance.build_ui()
                new_frame_instance.apply_theme()

            # Oyun frame'leri (ve AdminLogin) için reset_game metodunu çağır
            if hasattr(new_frame_instance, 'reset_game') and callable(new_frame_instance.reset_game):
                if name not in ["MainMenu", "ScoreBoard", "Feedback", "AdminPanel",
                                "QuestionEditor"]:  # YENİ: AdminPanel ve QuestionEditor resetleme gerektirmez
                    print(f"DEBUG (App): {name} için reset_game çağrılıyor.")
                    new_frame_instance.reset_game()
                elif name == "AdminLogin":  # AdminLogin her gösterildiğinde resetlensin
                    new_frame_instance.reset_game()
        else:
            print(f"HATA (App): '{name}' için yeni frame örneği oluşturulamadı.")

        print(f"DEBUG (App): show_frame('{name}') tamamlandı.")

    def handle_theme_toggle(self):
        print("DEBUG (App): handle_theme_toggle çağrıldı.")
        all_themes = get_all_theme_names()
        current_theme_name = get_current_theme_name()

        try:
            current_index = all_themes.index(current_theme_name)
            next_index = (current_index + 1) % len(all_themes)
            next_theme_name = all_themes[next_index]
            set_theme(next_theme_name)
            print(f"DEBUG (App): Tema '{current_theme_name}' -> '{next_theme_name}' olarak değiştirildi.")
        except ValueError:
            print(
                f"UYARI (App): Mevcut tema adı '{current_theme_name}' tema listesinde bulunamadı. Varsayılan temaya geçiliyor.")
            set_theme(all_themes[0] if all_themes else "Koyu Tema")  # İlk temaya veya 'Koyu Tema'ya ayarla

        self.apply_theme_to_all_active_frames()

    def apply_theme_to_all_active_frames(self):
        print(
            f"DEBUG (App): apply_theme_to_all_active_frames çağrıldı. Mevcut frame: {self.current_frame_instance.__class__.__name__ if self.current_frame_instance else 'None'}")
        theme = get_theme()
        self.container.config(bg=theme["bg"])

        if self.current_frame_instance:
            # Temanın uygulanması genellikle build_ui içinde veya on_show içinde yapılır.
            # Burada tekrar çağırmak, tüm aktif widget'ların tema ile güncellendiğinden emin olur.
            if hasattr(self.current_frame_instance, 'on_show') and callable(self.current_frame_instance.on_show):
                self.current_frame_instance.on_show()  # on_show içindeki build_ui ve apply_theme çağrıları yeterli
            else:
                self.current_frame_instance.build_ui()
                self.current_frame_instance.apply_theme() # Düzeltildi: new_frame_instance yerine self.current_frame_instance
        print("DEBUG (App): apply_theme_to_all_active_frames tamamlandı.")

    def toggle_fullscreen(self, event=None):
        self.attributes('-fullscreen', not self.attributes('-fullscreen'))

    def quit(self):
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
