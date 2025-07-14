# admin_panel.py - GÜNCEL (Buton ile Menü Yönlendirme)
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk  # ttk eklendi
from theme import get_theme
from base_frame import BaseGameFrame
from datetime import datetime  # Tarih formatlama için eklendi
import json  # Soru kaydetme/yükleme için eklendi
import os  # Dizin işlemleri için eklendi

# --- score_manager modülünü içe aktırma ---
try:
    from score_manager import delete_score, get_top_scores_for_game

    print("DEBUG: score_manager.py başarıyla içe aktarıldı (admin_panel.py).")
except ImportError as e:
    print(f"HATA: score_manager.py içe aktarılamadı (admin_panel.py)! Hata: {e}")
    print("Dummy delete_score ve get_top_scores_for_game fonksiyonları KULLANILIYOR.")


    def delete_score(game_name, player_name=""):
        print(
            f"[Dummy Silme] Oyun: {game_name}, Oyuncu: {player_name if player_name else 'TÜM oyuncular'} skoru silindi (sahte).")
        return True, "Skor başarıyla silindi (dummy)."


    def get_top_scores_for_game(game_name, num_scores=5):
        print(f"[Dummy Get - admin_panel.py] {game_name} için boş/sahte skorlar döndürülüyor.")
        return []

# --- question_manager fonksiyonları (doğrudan buraya alındı veya benzeri) ---
# Normalde ayrı bir question_manager.py dosyasından gelmeliydi, ama entegrasyon için buraya kopyalanmıştır.
QUESTIONS_DIR = "game_questions"


def _get_questions_file_path(game_name):
    """Belirli bir oyunun soru dosyasının yolunu döndürür."""
    os.makedirs(QUESTIONS_DIR, exist_ok=True)  # Klasörü oluştur
    return os.path.join(QUESTIONS_DIR, f"{game_name.lower().replace(' ', '_')}_questions.json")


def load_questions(game_name):
    """Belirli bir oyun için soruları yükler."""
    file_path = _get_questions_file_path(game_name)
    if not os.path.exists(file_path):
        print(f"DEBUG: '{file_path}' bulunamadı. Boş soru listesi döndürülüyor.")
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            questions = json.load(f)
            print(f"DEBUG: '{file_path}' başarıyla yüklendi. Yüklenen soru sayısı: {len(questions)}")  # Added print
            return questions
    except json.JSONDecodeError:
        print(f"Hata: '{file_path}' dosyası bozuk veya geçersiz JSON içeriyor. Boş soru listesi döndürülüyor.")
        return []
    except Exception as e:
        print(f"Hata: '{file_path}' yüklenirken beklenmeyen bir hata oluştu: {e}")
        return []


def save_questions(game_name, questions):
    """Belirli bir oyun için soruları kaydeder."""
    file_path = _get_questions_file_path(game_name)
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(questions, f, indent=4, ensure_ascii=False)
        print(f"DEBUG: Sorular '{file_path}' dosyasına başarıyla kaydedildi.")
        return True
    except IOError as e:
        print(f"Hata: Soru dosyası '{file_path}' kaydedilirken bir hata oluştu: {e}")
        return False
    except Exception as e:
        print(f"Hata: Sorular kaydedilirken beklenmeyen bir hata oluştu: {e}")
        return False


def get_all_game_names_with_questions():
    """Mevcut soru dosyalarına göre oyun isimlerini döndürür."""
    game_names = []
    if os.path.exists(QUESTIONS_DIR):
        for filename in os.listdir(QUESTIONS_DIR):
            if filename.endswith("_questions.json"):
                game_name = filename.replace("_questions.json", "").replace("_", " ").title()
                game_names.append(game_name)
    return sorted(game_names)


class AdminPanelFrame(BaseGameFrame):
    def __init__(self, parent, controller, game_name_str=None):
        self.game_name = "Admin Paneli"  # Admin paneli için sabit bir isim
        super().__init__(parent, controller, self.game_name)

        # Soru düzenleme için gerekli değişkenler
        self.selected_game_for_questions = tk.StringVar(
            self)  # Hangi oyunun sorularını düzenlediğimizi tutar (Combobox için)
        self.current_questions = []  # Seçili oyunun soruları (JSON listesi)
        self.current_question_index = -1  # Düzenlenen/görüntülenen sorunun indeksi

        # Soru düzenleme UI eleman referansları
        self.question_text_entry = None
        self.answer_entry = None
        self.option_entries = []
        self.question_info_label = None

        # Notebook ve sekme referanslarını başlangıçta None olarak ayarla (artık kullanılmıyor)
        self.notebook = None
        self.manage_questions_tab = None
        self.manage_scores_tab = None

        # Yeni panel referansları
        self.admin_buttons_frame = None
        self.question_management_panel = None
        self.score_management_panel = None
        self.current_active_panel_frame = None  # Hangi panelin aktif olduğunu takip eder

        self.build_ui()
        self.show_admin_panel("main_buttons")  # Başlangıçta ana butonları göster

    def build_ui(self):
        print("DEBUG: AdminPanelFrame: build_ui başladı.")
        for widget in self.winfo_children():
            widget.destroy()

        theme = get_theme()
        self.config(bg=theme["bg"])

        # Header
        self.header_frame = tk.Frame(self, bg=theme["header_bg"])
        self.header_frame.pack(side="top", fill="x", pady=10)
        self.header_label = tk.Label(self.header_frame, text=self.game_name,
                                     font=("Arial", 28, "bold"),
                                     bg=theme["header_bg"], fg=theme["header_fg"])
        self.header_label.pack(expand=True)
        print("DEBUG: AdminPanelFrame: Header UI kuruldu.")

        # Ana içerik çerçevesi (tüm panelleri barındıracak)
        self.main_content_frame = tk.Frame(self, bg=theme["bg"])
        self.main_content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        print("DEBUG: AdminPanelFrame: Ana içerik çerçevesi kuruldu.")

        # Admin ana butonları çerçevesi
        self.admin_buttons_frame = tk.Frame(self.main_content_frame, bg=theme["bg"])
        # self.admin_buttons_frame.pack(fill="both", expand=True) # Başlangıçta pack_forget ile gizlenecek

        # Soru Yönetimi Paneli
        self.question_management_panel = tk.Frame(self.main_content_frame, bg=theme["bg"])
        self.create_manage_questions_panel_content(self.question_management_panel)
        # self.question_management_panel.pack_forget() # Başlangıçta gizli

        # Skor Yönetimi Paneli
        self.score_management_panel = tk.Frame(self.main_content_frame, bg=theme["bg"])
        self.create_manage_scores_panel_content(self.score_management_panel)
        # self.score_management_panel.pack_forget() # Başlangıçta gizli

        # Ana Menüye Dön butonu (her zaman görünür olacak)
        back_button = tk.Button(self, text="⬅️ Ana Menüye Dön", font=("Arial", 16),
                                command=lambda: self.controller.show_frame("MainMenu"),
                                bg=theme["button_bg"], fg=theme["button_fg"],
                                activebackground=theme["active_button_bg"],
                                activeforeground=theme["active_button_fg"])
        back_button.pack(pady=20)
        print("DEBUG: AdminPanelFrame: Ana Menüye Dön butonu kuruldu.")

        self.apply_theme()  # Temayı uygula
        print("DEBUG: AdminPanelFrame: build_ui tamamlandı.")

    def show_admin_panel(self, panel_name):
        """Belirli bir yönetim panelini gösterir ve diğerlerini gizler."""
        # Tüm panelleri gizle
        if self.admin_buttons_frame:
            self.admin_buttons_frame.pack_forget()
        if self.question_management_panel:
            self.question_management_panel.pack_forget()
        if self.score_management_panel:
            self.score_management_panel.pack_forget()

        # İstenen paneli göster
        if panel_name == "main_buttons":
            self.admin_buttons_frame.pack(fill="both", expand=True)
            self.current_active_panel_frame = self.admin_buttons_frame
            self._create_main_admin_buttons_content()  # Butonları yeniden oluştur
        elif panel_name == "questions":
            self.question_management_panel.pack(fill="both", expand=True)
            self.current_active_panel_frame = self.question_management_panel
            self.on_game_selected_for_questions()  # Soruları yükle ve göster
        elif panel_name == "scores":
            self.score_management_panel.pack(fill="both", expand=True)
            self.current_active_panel_frame = self.score_management_panel
            self.display_scores_for_deletion()  # Skorları yükle ve göster

        self.apply_theme()  # Temayı uygulayarak yeni gösterilen panelin doğru temayı almasını sağla

    def _create_main_admin_buttons_content(self):
        """Admin ana menü butonlarını oluşturur."""
        theme = get_theme()
        # Mevcut butonları temizle
        for widget in self.admin_buttons_frame.winfo_children():
            widget.destroy()

        tk.Label(self.admin_buttons_frame, text="Yönetim Seçenekleri", font=("Arial", 20, "bold"),
                 bg=theme["bg"], fg=theme["fg"]).pack(pady=30)

        tk.Button(self.admin_buttons_frame, text="Soruları Yönet", font=("Arial", 18, "bold"),
                  command=lambda: self.show_admin_panel("questions"),
                  bg=theme["button_bg"], fg=theme["button_fg"],
                  activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"],
                  width=20, height=2).pack(pady=10)

        tk.Button(self.admin_buttons_frame, text="Skorları Yönet", font=("Arial", 18, "bold"),
                  command=lambda: self.show_admin_panel("scores"),
                  bg=theme["button_bg"], fg=theme["button_fg"],
                  activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"],
                  width=20, height=2).pack(pady=10)
        self.apply_theme()

    def create_manage_questions_panel_content(self, parent_frame):
        """Soruları Yönet panelinin içeriğini oluşturur."""
        theme = get_theme()
        parent_frame.config(bg=theme["bg"])

        # Geri Dön butonu
        tk.Button(parent_frame, text="⬅️ Yönetim Ana Menüye Dön", font=("Arial", 12),
                  command=lambda: self.show_admin_panel("main_buttons"),
                  bg=theme["button_bg"], fg=theme["button_fg"],
                  activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"]).pack(pady=10,
                                                                                                               anchor="nw",
                                                                                                               padx=10)

        # Ana içerik çerçevesi (grid layout)
        questions_main_content_frame = tk.Frame(parent_frame, bg=theme["bg"])
        questions_main_content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        questions_main_content_frame.grid_columnconfigure(0, weight=1)
        questions_main_content_frame.grid_rowconfigure(1, weight=1)  # Soru düzenleme alanı genişlesin

        # --- Oyun Seçim Alanı ---
        self.game_selection_frame = tk.Frame(questions_main_content_frame, bg=theme["panel_bg"], bd=2, relief="groove")
        self.game_selection_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.game_selection_frame.grid_columnconfigure(1, weight=1)

        tk.Label(self.game_selection_frame, text="Oyun Seç:", font=("Arial", 14),
                 bg=theme["panel_bg"], fg=theme["fg"]).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # ComboBox stilini ayarlayalım (ttk için)
        s = ttk.Style()
        s.theme_use('default')
        s.configure('TCombobox',
                    fieldbackground=theme["input_bg"],
                    background=theme["button_bg"],
                    foreground=theme["input_fg"],
                    bordercolor=theme["input_border"],
                    arrowcolor=theme["button_fg"])
        s.map('TCombobox',
              background=[('active', theme["active_button_bg"])],
              foreground=[('active', theme["active_button_fg"])])
        s.configure('TCombobox.Border', bordercolor=theme["input_border"])

        self.game_names = get_all_game_names_with_questions()
        manual_add_games = ["Kod Hafızası", "Output Tahmini", "Syntax Rush", "Sayı Tahmini", "Hızlı Yazma"]
        for game_name in manual_add_games:
            if game_name not in self.game_names:
                self.game_names.append(game_name)
        self.game_names.sort()

        self.game_selector = ttk.Combobox(self.game_selection_frame, textvariable=self.selected_game_for_questions,
                                          values=self.game_names, font=("Arial", 12),
                                          state="readonly", style='TCombobox')
        self.game_selector.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.game_selector.bind("<<ComboboxSelected>>", self.on_game_selected_for_questions)
        print("DEBUG: AdminPanelFrame: 'Soruları Düzenle' sekmesi için oyun seçimi ComboBox oluşturuldu.")

        # --- Soru Görüntüleme ve Düzenleme Alanı ---
        self.question_edit_frame = tk.Frame(questions_main_content_frame, bg=theme["panel_bg"], bd=2, relief="groove")
        self.question_edit_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.question_edit_frame.grid_columnconfigure(0, weight=1)
        print("DEBUG: AdminPanelFrame: 'Soruları Düzenle' sekmesi için soru düzenleme alanı oluşturuldu.")

        # --- Navigation/Actions Frame ---
        self.navigation_frame = tk.Frame(questions_main_content_frame, bg=theme["bg"])
        self.navigation_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        self.navigation_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        tk.Button(self.navigation_frame, text="◀ Önceki Soru", font=("Arial", 12),
                  command=self.prev_question, bg=theme["button_bg"], fg=theme["button_fg"],
                  activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"]).grid(row=0,
                                                                                                               column=0,
                                                                                                               padx=5,
                                                                                                               pady=5,
                                                                                                               sticky="ew")
        tk.Button(self.navigation_frame, text="Sonraki Soru ▶", font=("Arial", 12),
                  command=self.next_question, bg=theme["button_bg"], fg=theme["button_fg"],
                  activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"]).grid(row=0,
                                                                                                               column=1,
                                                                                                               padx=5,
                                                                                                               pady=5,
                                                                                                               sticky="ew")
        tk.Button(self.navigation_frame, text="➕ Soru Ekle", font=("Arial", 12),
                  command=self.add_question, bg=theme["success"], fg=theme["fg"],
                  activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"]).grid(row=0,
                                                                                                               column=2,
                                                                                                               padx=5,
                                                                                                               pady=5,
                                                                                                               sticky="ew")
        tk.Button(self.navigation_frame, text="🗑️ Soru Sil", font=("Arial", 12),
                  command=self.delete_question, bg=theme["error"], fg=theme["fg"],
                  activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"]).grid(row=0,
                                                                                                               column=3,
                                                                                                               padx=5,
                                                                                                               pady=5,
                                                                                                               sticky="ew")
        tk.Button(self.navigation_frame, text="💾 Kaydet", font=("Arial", 12, "bold"),
                  command=self.save_current_questions, bg=theme["button_bg"], fg=theme["button_fg"],
                  activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"]).grid(row=0,
                                                                                                               column=4,
                                                                                                               padx=5,
                                                                                                               pady=5,
                                                                                                               sticky="ew")
        print("DEBUG: AdminPanelFrame: 'Soruları Düzenle' sekmesi için navigasyon butonları oluşturuldu.")

        # Başlangıçta oyun yüklemesi kaldırıldı. Sadece boş mesaj gösterilecek.
        self.current_questions = []
        self.current_question_index = -1
        self.display_question()  # Boş göster

        self.apply_theme()  # Tüm UI elemanları oluşturulduktan sonra temayı uygula
        print("DEBUG: AdminPanelFrame: create_manage_questions_panel_content tamamlandı.")

    def on_game_selected_for_questions(self, event=None):
        """Oyun seçimi değiştiğinde soruları yükler ve gösterir."""
        game_name = self.selected_game_for_questions.get()
        if not game_name or game_name == "Oyun Seçin":
            messagebox.showwarning("Uyarı", "Lütfen düzenlemek için geçerli bir oyun seçin.", parent=self)
            self.current_questions = []
            self.current_question_index = -1
            self.display_question()
            return

        print(f"DEBUG: AdminPanelFrame: Oyun seçildi: {game_name}")
        self.current_questions = load_questions(game_name)
        self.current_question_index = 0 if self.current_questions else -1
        self.display_question()
        self.apply_theme()

    def display_question(self):
        """Mevcut soruyu düzenleme alanına yükler veya 'soru yok' mesajı gösterir."""
        theme = get_theme()

        for widget in self.question_edit_frame.winfo_children():
            widget.destroy()

        self.question_text_entry = None
        self.answer_entry = None
        self.option_entries = []
        self.question_info_label = None

        print(
            f"DEBUG: display_question çağrıldı. current_questions: {len(self.current_questions) if self.current_questions else 0}, current_question_index: {self.current_question_index}")  # Added print

        if not self.current_questions or self.current_question_index == -1:
            no_question_label = tk.Label(self.question_edit_frame,
                                         text="Bu oyun için henüz soru yok veya seçili soru yok. Yeni bir soru eklemek için '➕ Soru Ekle' butonuna tıklayın veya yukarıdan bir oyun seçin.",
                                         font=("Arial", 14), bg=theme["panel_bg"], fg=theme["fg"], wraplength=500)
            no_question_label.pack(pady=50)
            self.question_info_label = tk.Label(self.question_edit_frame, text="Soru 0 / 0",
                                                font=("Arial", 10), bg=theme["panel_bg"], fg=theme["fg"])
            self.question_info_label.pack(pady=5)
            print("DEBUG: 'Soru yok' mesajı gösteriliyor.")  # Added print
            self.apply_theme()
            return

        # Soru ve cevap alanları
        question_label_frame = tk.LabelFrame(self.question_edit_frame, text="Soru Metni",
                                             bg=theme["panel_bg"], fg=theme["fg"], font=("Arial", 12, "bold"))
        question_label_frame.pack(fill="x", padx=10, pady=5)
        self.question_text_entry = tk.Text(question_label_frame, height=5, font=("Courier New", 12),
                                           bg=theme["input_bg"], fg=theme["input_fg"],
                                           insertbackground=theme["input_fg"], bd=1, relief="solid",
                                           highlightbackground=theme["input_border"], highlightthickness=1,
                                           wrap="word")
        self.question_text_entry.pack(fill="both", expand=True, padx=5, pady=5)

        answer_label_frame = tk.LabelFrame(self.question_edit_frame, text="Doğru Cevap",
                                           bg=theme["panel_bg"], fg=theme["fg"], font=("Arial", 12, "bold"))
        answer_label_frame.pack(fill="x", padx=10, pady=5)
        self.answer_entry = tk.Text(answer_label_frame, height=3, font=("Arial", 12),
                                    bg=theme["input_bg"], fg=theme["input_fg"],
                                    insertbackground=theme["input_fg"], bd=1, relief="solid",
                                    highlightbackground=theme["input_border"], highlightthickness=1,
                                    wrap="word")
        self.answer_entry.pack(fill="both", expand=True, padx=5, pady=5)

        self.options_frame = tk.LabelFrame(self.question_edit_frame, text="Seçenekler (Çoktan Seçmeli İçin, Opsiyonel)",
                                           bg=theme["panel_bg"], fg=theme["fg"], font=("Arial", 12, "bold"))
        self.options_frame.pack(fill="x", padx=10, pady=5)
        self.option_entries = []
        for i in range(4):
            option_entry = tk.Entry(self.options_frame, font=("Arial", 12),
                                    bg=theme["input_bg"], fg=theme["input_fg"],
                                    insertbackground=theme["input_fg"], bd=1, relief="solid",
                                    highlightbackground=theme["input_border"], highlightthickness=1)
            option_entry.pack(fill="x", padx=5, pady=2)
            self.option_entries.append(option_entry)

        q_data = self.current_questions[self.current_question_index]
        self.question_text_entry.delete(1.0, tk.END)
        self.question_text_entry.insert(1.0, q_data.get("question", ""))
        self.answer_entry.delete(1.0, tk.END)
        self.answer_entry.insert(1.0, q_data.get("answer", ""))

        options = q_data.get("options", [])
        for i, entry in enumerate(self.option_entries):
            entry.delete(0, tk.END)
            if i < len(options):
                entry.insert(0, options[i])

        self.question_info_label = tk.Label(self.question_edit_frame,
                                            text=f"Soru {self.current_question_index + 1} / {len(self.current_questions)}",
                                            font=("Arial", 10), bg=theme["panel_bg"], fg=theme["fg"])
        self.question_info_label.pack(pady=5)

        self.apply_theme()

    def _get_current_question_data_from_ui(self):
        """UI'daki giriş alanlarından verileri toplayarak bir soru objesi döndürür."""
        if not self.question_text_entry or not self.answer_entry:
            return {"question": "", "answer": ""}

        question_text = self.question_text_entry.get(1.0, tk.END).strip()
        answer_text = self.answer_entry.get(1.0, tk.END).strip()

        options = [entry.get().strip() for entry in self.option_entries if entry.get().strip()]

        q_data = {
            "question": question_text,
            "answer": answer_text
        }
        if options:
            q_data["options"] = options
        return q_data

    def _update_current_question_in_list(self):
        """UI'daki verileri mevcut soru listesinde günceller."""
        if self.current_questions and 0 <= self.current_question_index < len(self.current_questions):
            updated_data = self._get_current_question_data_from_ui()
            if updated_data["question"] or updated_data["answer"] or (
                    updated_data.get("options") and len(updated_data["options"]) > 0):
                self.current_questions[self.current_question_index] = updated_data
                print(f"DEBUG (AdminPanelFrame): Soru {self.current_question_index + 1} güncellendi (bellekte).")
            else:
                print(
                    f"DEBUG (AdminPanelFrame): Soru {self.current_question_index + 1} için boş veri tespit edildi, güncelleme yapılmadı.")

    def prev_question(self):
        if not self.current_questions:
            messagebox.showinfo("Bilgi", "Gösterilecek soru yok.")
            return
        self._update_current_question_in_list()
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.display_question()
        else:
            messagebox.showinfo("Bilgi", "İlk sorudasınız.")

    def next_question(self):
        if not self.current_questions:
            messagebox.showinfo("Bilgi", "Gösterilecek soru yok.")
            return
        self._update_current_question_in_list()
        if self.current_question_index < len(self.current_questions) - 1:
            self.current_question_index += 1
            self.display_question()
        else:
            messagebox.showinfo("Bilgi", "Son sorudasınız.")

    def add_question(self):
        if self.current_questions and self.current_question_index != -1:
            self._update_current_question_in_list()

        new_question_data = {"question": "", "answer": "", "options": ["", "", "", ""]}
        self.current_questions.append(new_question_data)
        self.current_question_index = len(self.current_questions) - 1

        self.display_question()
        messagebox.showinfo("Bilgi", "Yeni boş soru eklendi. Lütfen doldurun ve kaydedin.")

    def delete_question(self):
        if not self.current_questions:
            messagebox.showwarning("Uyarı", "Silinecek soru yok.")
            return

        response = messagebox.askyesno("Onayla", "Bu soruyu silmek istediğinizden emin misiniz? Geri alınamaz!")
        if response:
            if 0 <= self.current_question_index < len(self.current_questions):
                deleted_q = self.current_questions.pop(self.current_question_index)
                print(f"DEBUG (AdminPanelFrame): Soru silindi: {deleted_q.get('question', 'Bilinmeyen Soru')}")

                if not self.current_questions:
                    self.current_question_index = -1
                elif self.current_question_index >= len(self.current_questions):
                    self.current_question_index = len(self.current_questions) - 1

                self.display_question()
                messagebox.showinfo("Başarılı", "Soru başarıyla silindi. Kaydetmeyi unutmayın!")
            else:
                messagebox.showwarning("Uyarı", "Geçerli bir soru seçili değil.")

    def save_current_questions(self):
        """Mevcut seçili oyunun tüm sorularını dosyaya kaydeder."""
        if self.current_questions and 0 <= self.current_question_index < len(self.current_questions):
            self._update_current_question_in_list()

        game_name = self.selected_game_for_questions.get()
        if not game_name or game_name == "Oyun Seçin":
            messagebox.showerror("Hata", "Lütfen soruları kaydetmek için bir oyun seçin.")
            return

        cleaned_questions = []
        for q_data in self.current_questions:
            if not q_data.get("question", "").strip() or not q_data.get("answer", "").strip():
                print(f"UYARI: Boş soru veya cevabı olan soru atlandı ve kaydedilmedi: {q_data}")
                continue

            if "options" in q_data and isinstance(q_data["options"], list):
                q_data["options"] = [opt for opt in q_data["options"] if opt.strip()]
                if not q_data["options"]:
                    del q_data["options"]
            cleaned_questions.append(q_data)

        success = save_questions(game_name, cleaned_questions)
        self.current_questions = cleaned_questions
        self.current_question_index = 0 if self.current_questions else -1
        self.display_question()
        if success:
            messagebox.showinfo("Başarılı", f"'{game_name}' oyununun soruları başarıyla kaydedildi!")
        else:
            messagebox.showerror("Hata", f"'{game_name}' oyununun soruları kaydedilirken bir hata oluştu.")

        # Oyun listesini de yenile ki yeni oluşturulan oyunlar varsa görünsün
        self.game_names = get_all_game_names_with_questions()
        manual_add_games = ["Kod Hafızası", "Output Tahmini", "Syntax Rush", "Sayı Tahmini", "Hızlı Yazma"]
        for g_name in manual_add_games:
            if g_name not in self.game_names:
                self.game_names.append(g_name)
        self.game_names.sort()
        self.game_selector.config(values=self.game_names)

    # --- SKORLARI DÜZENLE PANEL METODU ---
    def create_manage_scores_panel_content(self, parent_frame):
        theme = get_theme()
        parent_frame.config(bg=theme["bg"])

        # Geri Dön butonu
        tk.Button(parent_frame, text="⬅️ Yönetim Ana Menüye Dön", font=("Arial", 12),
                  command=lambda: self.show_admin_panel("main_buttons"),
                  bg=theme["button_bg"], fg=theme["button_fg"],
                  activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"]).pack(pady=10,
                                                                                                               anchor="nw",
                                                                                                               padx=10)

        tk.Label(parent_frame, text="Skor Silme Paneli", font=("Arial", 20, "bold"),
                 bg=theme["bg"], fg=theme["fg"]).pack(pady=20)

        # Oyun Adı Girişi
        game_name_label = tk.Label(parent_frame, text="Oyun Adı:", font=("Arial", 14),
                                   bg=theme["bg"], fg=theme["fg"])
        game_name_label.pack(pady=5)
        self.score_game_name_entry = tk.Entry(parent_frame, font=("Arial", 14),
                                              bg=theme["entry_bg"], fg=theme["entry_fg"],
                                              insertbackground=theme["entry_fg"],
                                              highlightbackground=theme["input_border"], highlightthickness=1)
        self.score_game_name_entry.pack(pady=5)
        print("DEBUG: AdminPanelFrame: Skor silme için oyun adı girişi oluşturuldu.")

        # Oyuncu Adı Girişi
        player_name_label = tk.Label(parent_frame, text="Oyuncu Adı (Tüm skorları silmek için boş bırakın):",
                                     font=("Arial", 14),
                                     bg=theme["bg"], fg=theme["fg"])
        player_name_label.pack(pady=5)
        self.score_player_name_entry = tk.Entry(parent_frame, font=("Arial", 14),
                                                bg=theme["entry_bg"], fg=theme["entry_fg"],
                                                insertbackground=theme["entry_fg"],
                                                highlightbackground=theme["input_border"], highlightthickness=1)
        self.score_player_name_entry.pack(pady=5)
        print("DEBUG: AdminPanelFrame: Skor silme için oyuncu adı girişi oluşturuldu.")

        # Skorları Sil Butonu
        delete_score_button = tk.Button(parent_frame, text="Skorları Sil", font=("Arial", 16, "bold"),
                                        command=self.delete_selected_scores,
                                        bg=theme["error"], fg=theme["fg"],  # Hata rengi kullanıldı
                                        activebackground=theme["wrong_color"],
                                        activeforeground=theme["fg"])
        delete_score_button.pack(pady=20)
        print("DEBUG: AdminPanelFrame: Skor silme butonu oluşturuldu.")

        # Skorları Görüntüleme Alanı (Silmeden önce kontrol etmek için)
        tk.Label(parent_frame, text="Mevcut Skorlar (Silmeden Önce Kontrol Edin):", font=("Arial", 16),
                 bg=theme["bg"], fg=theme["fg"]).pack(pady=10)

        self.score_display_text = tk.Text(parent_frame, height=10, width=60, font=("Courier New", 12),
                                          bg=theme["code_bg"], fg=theme["code_fg"],
                                          state="disabled", wrap="word")
        self.score_display_text.pack(pady=10)

        # Skorları Göster Butonu
        show_scores_button = tk.Button(parent_frame, text="Skorları Göster", font=("Arial", 14),
                                       command=self.display_scores_for_deletion,
                                       bg=theme["button_bg"], fg=theme["button_fg"],
                                       activebackground=theme["active_button_bg"],
                                       activeforeground=theme["active_button_fg"])
        show_scores_button.pack(pady=10)
        print("DEBUG: AdminPanelFrame: Skorları göster butonu ve görüntüleme alanı oluşturuldu.")

    def display_scores_for_deletion(self):
        """Belirtilen oyun için skorları görüntüleme alanında gösterir."""
        game_name = self.score_game_name_entry.get().strip()
        if not game_name:
            messagebox.showwarning("Uyarı", "Lütfen bir oyun adı girin.", parent=self)
            return

        self.score_display_text.config(state="normal")
        self.score_display_text.delete(1.0, tk.END)

        top_scores = get_top_scores_for_game(game_name, num_scores=20)  # Daha fazla skor göster

        if not top_scores:
            self.score_display_text.insert(tk.END, f"'{game_name}' oyunu için skor bulunamadı.\n")
        else:
            self.score_display_text.insert(tk.END, f"--- '{game_name}' Oyununun Skorları ---\n")
            for i, score_entry in enumerate(top_scores):
                player_name = score_entry.get("player_name", "Anonim")
                score_value = score_entry.get("score", 0)
                time_taken = score_entry.get("time_taken")
                timestamp = score_entry.get("timestamp")

                time_str = ""
                if time_taken is not None:
                    minutes = int(time_taken // 60)
                    secs = int(time_taken % 60)
                    time_str = f" Süre: {minutes:02}:{secs:02}"

                date_str = ""
                if timestamp:
                    try:
                        date_obj = datetime.fromtimestamp(timestamp)
                        date_str = f" ({date_obj.strftime('%Y-%m-%d %H:%M')})"
                    except (TypeError, ValueError):
                        date_str = " (Geçersiz Tarih)"

                self.score_display_text.insert(tk.END,
                                               f"{i + 1}. Oyuncu: {player_name}, Skor: {score_value}{time_str}{date_str}\n")
        self.score_display_text.config(state="disabled")
        print(f"DEBUG: AdminPanelFrame: '{game_name}' için skorlar görüntülendi.")

    def delete_selected_scores(self):
        """Belirtilen oyun ve oyuncuya ait skorları siler."""
        game_name = self.score_game_name_entry.get().strip()
        player_name = self.score_player_name_entry.get().strip()

        if not game_name:
            messagebox.showwarning("Uyarı", "Lütfen silmek istediğiniz oyunun adını girin.", parent=self)
            return

        confirm_message = f"'{game_name}' oyunundan "
        if player_name:
            confirm_message += f"'{player_name}' adlı oyuncuya ait tüm skorları silmek istediğinizden emin misiniz?"
        else:
            confirm_message += "TÜM skorları silmek istediğinizden emin misiniz? Bu işlem geri alınamaz!"

        confirm = messagebox.askyesno("Onay", confirm_message, parent=self)
        if not confirm:
            return

        # score_manager'daki delete_score fonksiyonunu çağır
        success, message = delete_score(game_name, player_name)

        if success:
            messagebox.showinfo("Başarılı", message, parent=self)
            self.display_scores_for_deletion()  # Skorları tekrar yükleyerek güncel durumu göster
        else:
            messagebox.showerror("Hata", message, parent=self)
        print(f"DEBUG: AdminPanelFrame: Skor silme işlemi tamamlandı. Sonuç: {message}")

    # on_tab_change artık kullanılmıyor, çünkü sekmeler kaldırıldı.
    # Bu metodun içeriği show_admin_panel metoduna taşındı.
    # def on_tab_change(self, event):
    #     pass

    def on_show(self):
        """Admin paneli her gösterildiğinde çağrılır."""
        print("DEBUG: AdminPanelFrame: on_show çağrıldı.")

        # UI'ı tamamen yeniden oluşturma çağrısını kaldırıyoruz.
        # self.build_ui() # BU SATIR KALDIRILDI!

        # Temayı uygula (widget'lar zaten var olduğu varsayılır)
        self.apply_theme()

        # Ana butonları göster
        self.show_admin_panel("main_buttons")

        print("DEBUG: AdminPanelFrame: on_show tamamlandı.")

    def apply_theme(self):
        print("DEBUG: AdminPanelFrame: apply_theme başladı.")
        super().apply_theme()
        theme = get_theme()

        self.config(bg=theme["bg"])

        # Check if attributes exist and are not None before calling winfo_exists()
        if hasattr(self, 'header_frame') and self.header_frame is not None and self.header_frame.winfo_exists():
            self.header_frame.config(bg=theme["header_bg"])
        if hasattr(self, 'header_label') and self.header_label is not None and self.header_label.winfo_exists():
            self.header_label.config(bg=theme["header_bg"], fg=theme["header_fg"])

        if hasattr(self,
                   'main_content_frame') and self.main_content_frame is not None and self.main_content_frame.winfo_exists():
            self.main_content_frame.config(bg=theme["bg"])

        # Ana butonlar çerçevesini temala
        if hasattr(self,
                   'admin_buttons_frame') and self.admin_buttons_frame is not None and self.admin_buttons_frame.winfo_exists():
            self.admin_buttons_frame.config(bg=theme["bg"])
            for widget in self.admin_buttons_frame.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.config(bg=theme["bg"], fg=theme["fg"])
                elif isinstance(widget, tk.Button):
                    widget.config(bg=theme["button_bg"], fg=theme["button_fg"],
                                  activebackground=theme["active_button_bg"],
                                  activeforeground=theme["active_button_fg"])

        # Soru yönetimi panelini temala
        if hasattr(self,
                   'question_management_panel') and self.question_management_panel is not None and self.question_management_panel.winfo_exists():
            self.question_management_panel.config(bg=theme["bg"])
            for widget in self.question_management_panel.winfo_children():
                if isinstance(widget, tk.Frame) or isinstance(widget, tk.LabelFrame):
                    if (widget is self.game_selection_frame and self.game_selection_frame is not None) or \
                            (widget is self.question_edit_frame and self.question_edit_frame is not None) or \
                            (hasattr(self,
                                     'options_frame') and self.options_frame is not None and widget is self.options_frame):
                        widget.config(bg=theme["panel_bg"])
                    elif (widget is self.navigation_frame and self.navigation_frame is not None):
                        widget.config(bg=theme["bg"])
                    else:
                        widget.config(bg=theme["bg"])  # Default to background

                    for sub_widget in widget.winfo_children():
                        if isinstance(sub_widget, tk.Label):
                            if (
                                    sub_widget.master is self.game_selection_frame and self.game_selection_frame is not None) or \
                                    (
                                            sub_widget.master is self.question_edit_frame and self.question_edit_frame is not None) or \
                                    (hasattr(self,
                                             'options_frame') and self.options_frame is not None and sub_widget.master is self.options_frame) or \
                                    isinstance(sub_widget.master, tk.LabelFrame):
                                sub_widget.config(bg=theme["panel_bg"], fg=theme["fg"])
                            else:
                                sub_widget.config(bg=theme["bg"], fg=theme["fg"])
                        elif isinstance(sub_widget, (tk.Entry, tk.Text)):
                            sub_widget.config(bg=theme["input_bg"], fg=theme["input_fg"],
                                              insertbackground=theme["input_fg"],
                                              highlightbackground=theme["input_border"],
                                              highlightcolor=theme["input_border"],
                                              bd=1, relief="solid", highlightthickness=1)
                        elif isinstance(sub_widget, tk.Button):
                            if "Soru Ekle" in sub_widget.cget("text"):
                                sub_widget.config(bg=theme["success"], fg=theme["fg"],
                                                  activebackground=theme["active_button_bg"],
                                                  activeforeground=theme["active_button_fg"])
                            elif "Soru Sil" in sub_widget.cget("text"):
                                sub_widget.config(bg=theme["error"], fg=theme["fg"],
                                                  activebackground=theme["active_button_bg"],
                                                  activeforeground=theme["active_button_fg"])
                            else:
                                sub_widget.config(bg=theme["button_bg"], fg=theme["button_fg"],
                                                  activebackground=theme["active_button_bg"],
                                                  activeforeground=theme["active_button_fg"])
                        elif isinstance(sub_widget, ttk.Combobox):
                            s = ttk.Style()
                            s.configure('TCombobox',
                                        fieldbackground=theme["input_bg"],
                                        background=theme["button_bg"],
                                        foreground=theme["input_fg"],
                                        bordercolor=theme["input_border"],
                                        arrowcolor=theme["button_fg"])
                            s.map('TCombobox',
                                  background=[('active', theme["active_button_bg"])],
                                  foreground=[('active', theme["active_button_fg"])])
                            s.configure('TCombobox.Border', bordercolor=theme["input_border"])
                            sub_widget.config(style='TCombobox')

        # Skor yönetimi panelini temala
        if hasattr(self,
                   'score_management_panel') and self.score_management_panel is not None and self.score_management_panel.winfo_exists():
            self.score_management_panel.config(bg=theme["bg"])
            for widget in self.score_management_panel.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.config(bg=theme["bg"], fg=theme["fg"])
                elif isinstance(widget, tk.Entry):
                    widget.config(bg=theme["entry_bg"], fg=theme["entry_fg"],
                                  insertbackground=theme["entry_fg"],
                                  highlightbackground=theme["input_border"], highlightthickness=1)
                elif isinstance(widget, tk.Button):
                    if widget.cget("text") == "Skorları Sil":
                        widget.config(bg=theme["error"], fg=theme["fg"],
                                      activebackground=theme["wrong_color"],
                                      activeforeground=theme["fg"])
                    else:
                        widget.config(bg=theme["button_bg"], fg=theme["button_fg"],
                                      activebackground=theme["active_button_bg"],
                                      activeforeground=theme["active_button_fg"])
                elif isinstance(widget, tk.Text):
                    widget.config(bg=theme["code_bg"], fg=theme["code_fg"])

        for widget in self.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget("text") == "⬅️ Ana Menüye Dön":
                widget.config(bg=theme["button_bg"], fg=theme["button_fg"],
                              activebackground=theme["active_button_bg"],
                              activeforeground=theme["active_button_fg"])
        print("DEBUG: AdminPanelFrame: apply_theme tamamlandı.")
