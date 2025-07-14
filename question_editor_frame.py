# question_editor_frame.py - GÜNCELLENDİ (Çok Satırlı Girişler ve Tema İyileştirmeleri)
import tkinter as tk
from tkinter import messagebox, ttk
from base_frame import BaseGameFrame
from theme import get_theme
from question_manager import load_questions, save_questions, get_all_game_names_with_questions

class QuestionEditorFrame(BaseGameFrame):
    def __init__(self, parent, controller, game_name_str=None):
        # game_name_str, hangi oyunun sorularını düzenlediğimizi belirtir.
        self.game_name = f"'{game_name_str}' Soruları Düzenle" if game_name_str else "Soru Düzenleyici"
        super().__init__(parent, controller, self.game_name) # BaseGameFrame'e güncel başlığı iletiyoruz
        self.selected_game = tk.StringVar(self) # Hangi oyunun sorularını düzenlediğimizi tutar (Combobox için)
        if game_name_str: # Eğer bir oyun adı ile başlatıldıysa, Combobox'ı o oyunla başlat
            self.selected_game.set(game_name_str)

        self.current_questions = [] # Seçili oyunun soruları (JSON listesi)
        self.current_question_index = -1 # Düzenlenen/görüntülenen sorunun indeksi

        # Entry ve Text widget'larını depolamak için değişkenler (Başlangıçta None)
        self.question_text_entry = None
        self.answer_entry = None # Artık Text widget olacak
        self.option_entries = []
        self.question_info_label = None # Soru sayısı bilgisi etiketi

        # Frame referansları
        self.header_frame = None
        self.game_selection_frame = None
        self.main_content_frame = None
        self.question_edit_frame = None
        self.navigation_frame = None

        self.build_ui() # UI'ı oluştur

    def build_ui(self):
        print("DEBUG (QuestionEditorFrame): build_ui başladı.")
        for widget in self.winfo_children():
            widget.destroy()

        theme = get_theme()
        self.config(bg=theme["bg"])

        # Header
        self.header_frame = tk.Frame(self, bg=theme["header_bg"])
        self.header_frame.pack(side="top", fill="x", pady=10)
        # Header etiketi, seçili oyunun adını dinamik olarak gösterecek
        self.header_label = tk.Label(self.header_frame, text=self.game_name, # Başlangıçta __init__ içindeki game_name'i kullanır
                                     font=("Arial", 28, "bold"),
                                     bg=theme["header_bg"], fg=theme["header_fg"])
        self.header_label.pack(expand=True)
        print("DEBUG (QuestionEditorFrame): Header UI kuruldu.")

        # Main Content Frame (Grid Layout)
        self.main_content_frame = tk.Frame(self, bg=theme["bg"])
        self.main_content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.main_content_frame.grid_columnconfigure(0, weight=1) # Tek sütunlu layout için
        self.main_content_frame.grid_rowconfigure(1, weight=1) # question_edit_frame'in olduğu satır genişlesin

        # --- Oyun Seçim Alanı ---
        self.game_selection_frame = tk.Frame(self.main_content_frame, bg=theme["panel_bg"], bd=2, relief="groove")
        self.game_selection_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.game_selection_frame.grid_columnconfigure(1, weight=1)

        tk.Label(self.game_selection_frame, text="Oyun Seç:", font=("Arial", 14),
                 bg=theme["panel_bg"], fg=theme["fg"]).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # ComboBox stilini ayarlayalım (ttk için)
        s = ttk.Style()
        s.theme_use('default') # Varsayılan temayı kullan
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


        # Mevcut soru dosyası olan oyunlar ve manuel eklenecek oyunlar
        self.game_names = get_all_game_names_with_questions()
        manual_add_games = ["Kod Hafızası", "Output Tahmini", "SyntaxRush", "NumberGuessGame", "TypingGame"]
        for game_name in manual_add_games:
            if game_name not in self.game_names:
                self.game_names.append(game_name)
        self.game_names.sort() # Alfabetik sırala

        self.game_selector = ttk.Combobox(self.game_selection_frame, textvariable=self.selected_game,
                                          values=self.game_names, font=("Arial", 12),
                                          state="readonly", style='TCombobox')
        self.game_selector.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.game_selector.bind("<<ComboboxSelected>>", self.on_game_selected)

        # --- Soru Görüntüleme ve Düzenleme Alanı ---
        self.question_edit_frame = tk.Frame(self.main_content_frame, bg=theme["panel_bg"], bd=2, relief="groove")
        self.question_edit_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.question_edit_frame.grid_columnconfigure(0, weight=1) # İçerik genişlesin

        # --- Navigation/Actions Frame ---
        self.navigation_frame = tk.Frame(self.main_content_frame, bg=theme["bg"])
        self.navigation_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        self.navigation_frame.grid_columnconfigure((0,1,2,3,4), weight=1) # Butonlar eşit yayılsın

        tk.Button(self.navigation_frame, text="◀ Önceki Soru", font=("Arial", 12),
                  command=self.prev_question, bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"]).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        tk.Button(self.navigation_frame, text="Sonraki Soru ▶", font=("Arial", 12),
                  command=self.next_question, bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"]).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        tk.Button(self.navigation_frame, text="➕ Soru Ekle", font=("Arial", 12),
                  command=self.add_question, bg=theme["success"], fg=theme["fg"], activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"]).grid(row=0, column=2, padx=5, pady=5, sticky="ew") # fg düzeltildi
        tk.Button(self.navigation_frame, text="🗑️ Soru Sil", font=("Arial", 12),
                  command=self.delete_question, bg=theme["error"], fg=theme["fg"], activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"]).grid(row=0, column=3, padx=5, pady=5, sticky="ew") # fg düzeltildi
        tk.Button(self.navigation_frame, text="💾 Kaydet", font=("Arial", 12, "bold"),
                  command=self.save_current_questions, bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"]).grid(row=0, column=4, padx=5, pady=5, sticky="ew") # fg düzeltildi

        # Back Button
        back_button = tk.Button(self, text="⬅️ Admin Paneline Dön", font=("Arial", 16),
                                command=lambda: self.controller.show_frame("AdminPanel"),
                                bg=theme["button_bg"], fg=theme["button_fg"],
                                activebackground=theme["active_button_bg"],
                                activeforeground=theme["active_button_fg"])
        back_button.pack(pady=20)

        # UI elemanları oluşturulduktan sonra, başlangıçtaki oyun yüklemesini yap
        # Eğer __init__ sırasında game_name_str ile başlatıldıysa, o oyunu seç
        if self.selected_game.get():
            self.on_game_selected()
        elif self.game_names: # Değilse, ilk oyunu seç
            self.selected_game.set(self.game_names[0])
            self.on_game_selected()
        else:
            # Hiç oyun yoksa veya seçili değilse boş ekranı göster
            self.current_questions = []
            self.current_question_index = -1
            self.display_question() # Boş göster

        self.apply_theme() # Tüm UI elemanları oluşturulduktan sonra temayı uygula
        print("DEBUG (QuestionEditorFrame): build_ui tamamlandı.")

    def on_game_selected(self, event=None):
        """Oyun seçimi değiştiğinde soruları yükler ve gösterir."""
        game_name = self.selected_game.get()
        if not game_name or game_name == "Oyun Seçin": # "Oyun Seçin" varsayılan değeri de kontrol et
            messagebox.showwarning("Uyarı", "Lütfen düzenlemek için geçerli bir oyun seçin.")
            self.current_questions = []
            self.current_question_index = -1
            self.display_question() # Boş göster
            self.header_label.config(text="Soru Düzenleyici") # Başlığı varsayılana döndür
            return

        print(f"DEBUG (QuestionEditorFrame): Oyun seçildi: {game_name}")
        self.header_label.config(text=f"'{game_name}' Soruları Düzenle") # Seçili oyun adını başlığa yansıt
        self.current_questions = load_questions(game_name)
        self.current_question_index = 0 if self.current_questions else -1 # Eğer soru varsa ilkini göster, yoksa -1
        self.display_question() # UI'ı güncelle
        self.apply_theme() # Yeni widget'lar yüklendiğinde temayı yeniden uygula

    def display_question(self):
        """Mevcut soruyu düzenleme alanına yükler veya 'soru yok' mesajı gösterir."""
        theme = get_theme()

        # question_edit_frame içindeki tüm eski widget'ları temizle
        for widget in self.question_edit_frame.winfo_children():
            widget.destroy()

        self.question_text_entry = None
        self.answer_entry = None
        self.option_entries = []
        self.question_info_label = None


        if not self.current_questions or self.current_question_index == -1:
            tk.Label(self.question_edit_frame, text="Bu oyun için henüz soru yok veya seçili soru yok. Yeni bir soru ekleyin.",
                     font=("Arial", 14), bg=theme["panel_bg"], fg=theme["fg"], wraplength=500).pack(pady=50)
            self.question_info_label = tk.Label(self.question_edit_frame, text="Soru 0 / 0",
                                                font=("Arial", 10), bg=theme["panel_bg"], fg=theme["fg"])
            self.question_info_label.pack(pady=5)
            self.apply_theme() # Temayı uygula
            return

        # Soru ve cevap alanları
        # Soru
        question_label_frame = tk.LabelFrame(self.question_edit_frame, text="Soru Metni",
                                             bg=theme["panel_bg"], fg=theme["fg"], font=("Arial", 12, "bold"))
        question_label_frame.pack(fill="x", padx=10, pady=5)
        self.question_text_entry = tk.Text(question_label_frame, height=5, font=("Courier New", 12), # Yüksekliği düşürüldü
                                           bg=theme["input_bg"], fg=theme["input_fg"],
                                           insertbackground=theme["input_fg"], bd=1, relief="solid",
                                           highlightbackground=theme["input_border"], highlightthickness=1,
                                           wrap="word")
        self.question_text_entry.pack(fill="both", expand=True, padx=5, pady=5)

        # Doğru Cevap (Artık Text widget)
        answer_label_frame = tk.LabelFrame(self.question_edit_frame, text="Doğru Cevap",
                                            bg=theme["panel_bg"], fg=theme["fg"], font=("Arial", 12, "bold"))
        answer_label_frame.pack(fill="x", padx=10, pady=5)
        self.answer_entry = tk.Text(answer_label_frame, height=3, font=("Arial", 12), # Text widget olarak değiştirildi, yükseklik ayarlandı
                                      bg=theme["input_bg"], fg=theme["input_fg"],
                                      insertbackground=theme["input_fg"], bd=1, relief="solid",
                                      highlightbackground=theme["input_border"], highlightthickness=1,
                                      wrap="word")
        self.answer_entry.pack(fill="both", expand=True, padx=5, pady=5)

        # Seçenekler alanı (Çoktan Seçmeli İçin, Opsiyonel)
        self.options_frame = tk.LabelFrame(self.question_edit_frame, text="Seçenekler (Çoktan Seçmeli İçin, Opsiyonel)",
                                           bg=theme["panel_bg"], fg=theme["fg"], font=("Arial", 12, "bold"))
        self.options_frame.pack(fill="x", padx=10, pady=5)
        self.option_entries = []
        for i in range(4): # 4 seçenek için yer açalım
            option_entry = tk.Entry(self.options_frame, font=("Arial", 12),
                                    bg=theme["input_bg"], fg=theme["input_fg"],
                                    insertbackground=theme["input_fg"], bd=1, relief="solid",
                                    highlightbackground=theme["input_border"], highlightthickness=1)
            option_entry.pack(fill="x", padx=5, pady=2)
            self.option_entries.append(option_entry)

        # Mevcut soruyu UI'a yükle
        q_data = self.current_questions[self.current_question_index]
        self.question_text_entry.delete(1.0, tk.END)
        self.question_text_entry.insert(1.0, q_data.get("question", ""))
        self.answer_entry.delete(1.0, tk.END) # Text widget olduğu için 1.0, tk.END
        self.answer_entry.insert(1.0, q_data.get("answer", ""))

        options = q_data.get("options", [])
        for i, entry in enumerate(self.option_entries):
            entry.delete(0, tk.END)
            if i < len(options):
                entry.insert(0, options[i])

        # Footer (Soru Sayısı Bilgisi)
        self.question_info_label = tk.Label(self.question_edit_frame,
                                            text=f"Soru {self.current_question_index + 1} / {len(self.current_questions)}",
                                            font=("Arial", 10), bg=theme["panel_bg"], fg=theme["fg"])
        self.question_info_label.pack(pady=5)

        self.apply_theme() # Yeni oluşturulan tüm widget'lara temayı uygula

    def _get_current_question_data_from_ui(self):
        """UI'daki giriş alanlarından verileri toplayarak bir soru objesi döndürür."""
        if not self.question_text_entry or not self.answer_entry:
            return {"question": "", "answer": ""}

        question_text = self.question_text_entry.get(1.0, tk.END).strip()
        answer_text = self.answer_entry.get(1.0, tk.END).strip() # Text widget olduğu için 1.0, tk.END

        # Sadece doldurulmuş seçenekleri al
        options = [entry.get().strip() for entry in self.option_entries if entry.get().strip()]

        q_data = {
            "question": question_text,
            "answer": answer_text
        }
        if options: # Eğer seçenekler varsa, dictionary'ye ekle
            q_data["options"] = options
        return q_data

    def _update_current_question_in_list(self):
        """UI'daki verileri mevcut soru listesinde günceller."""
        if self.current_questions and 0 <= self.current_question_index < len(self.current_questions):
            updated_data = self._get_current_question_data_from_ui()
            # Yalnızca geçerli veriler varsa güncelle
            if updated_data["question"] or updated_data["answer"] or (updated_data.get("options") and len(updated_data["options"]) > 0):
                self.current_questions[self.current_question_index] = updated_data
                print(f"DEBUG (QuestionEditorFrame): Soru {self.current_question_index + 1} güncellendi (bellekte).")
            else:
                print(f"DEBUG (QuestionEditorFrame): Soru {self.current_question_index + 1} için boş veri tespit edildi, güncelleme yapılmadı.")

    def prev_question(self):
        if not self.current_questions:
            messagebox.showinfo("Bilgi", "Gösterilecek soru yok.")
            return
        self._update_current_question_in_list() # Değişiklikleri kaydet (bellekte)
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.display_question()
        else:
            messagebox.showinfo("Bilgi", "İlk sorudasınız.")

    def next_question(self):
        if not self.current_questions:
            messagebox.showinfo("Bilgi", "Gösterilecek soru yok.")
            return
        self._update_current_question_in_list() # Değişiklikleri kaydet (bellekte)
        if self.current_question_index < len(self.current_questions) - 1:
            self.current_question_index += 1
            self.display_question()
        else:
            messagebox.showinfo("Bilgi", "Son sorudasınız.")

    def add_question(self):
        # Eğer mevcut bir soru varsa, önce onu kaydet
        if self.current_questions and self.current_question_index != -1:
            self._update_current_question_in_list()

        # Yeni boş bir soru oluştur ve listeye ekle
        new_question_data = {"question": "", "answer": "", "options": ["", "", "", ""]} # 4 boş seçenekle başlat
        self.current_questions.append(new_question_data)
        self.current_question_index = len(self.current_questions) - 1 # Yeni soruyu seç

        self.display_question() # Yeni boş soruyu göster
        messagebox.showinfo("Bilgi", "Yeni boş soru eklendi. Lütfen doldurun ve kaydedin.")

    def delete_question(self):
        if not self.current_questions:
            messagebox.showwarning("Uyarı", "Silinecek soru yok.")
            return

        response = messagebox.askyesno("Onayla", "Bu soruyu silmek istediğinizden emin misiniz? Geri alınamaz!")
        if response:
            if 0 <= self.current_question_index < len(self.current_questions):
                deleted_q = self.current_questions.pop(self.current_question_index)
                print(f"DEBUG (QuestionEditorFrame): Soru silindi: {deleted_q.get('question', 'Bilinmeyen Soru')}")

                # İndeksi ayarla: eğer liste boşsa -1, değilse bir önceki veya ilk soruya git
                if not self.current_questions:
                    self.current_question_index = -1
                elif self.current_question_index >= len(self.current_questions):
                    self.current_question_index = len(self.current_questions) - 1

                self.display_question() # UI'ı güncelle
                messagebox.showinfo("Başarılı", "Soru başarıyla silindi. Kaydetmeyi unutmayın!")
            else:
                messagebox.showwarning("Uyarı", "Geçerli bir soru seçili değil.")


    def save_current_questions(self):
        """Mevcut seçili oyunun tüm sorularını dosyaya kaydeder."""
        # En son görüntülenen sorunun güncel UI verilerini listeye kaydet
        if self.current_questions and 0 <= self.current_question_index < len(self.current_questions):
            self._update_current_question_in_list()

        game_name = self.selected_game.get()
        if not game_name or game_name == "Oyun Seçin":
            messagebox.showerror("Hata", "Lütfen soruları kaydetmek için bir oyun seçin.")
            return

        # Kaydetmeden önce soruları temizle ve boş/gereksiz seçenekleri kaldır
        cleaned_questions = []
        for q_data in self.current_questions:
            # Soru metni veya cevap boşsa bu soruyu atla
            if not q_data.get("question", "").strip() or not q_data.get("answer", "").strip():
                print(f"UYARI: Boş soru veya cevabı olan soru atlandı ve kaydedilmedi: {q_data}")
                continue # Bu soruyu temizlenmiş listeye ekleme

            # Boş ve gereksiz seçenekleri filtrele
            if "options" in q_data and isinstance(q_data["options"], list):
                q_data["options"] = [opt for opt in q_data["options"] if opt.strip()]
                if not q_data["options"]: # Eğer filtreleme sonrası boş kalırsa 'options' anahtarını sil
                    del q_data["options"]
            cleaned_questions.append(q_data)

        save_questions(game_name, cleaned_questions)
        self.current_questions = cleaned_questions # Listeyi güncelleyelim
        self.current_question_index = 0 if self.current_questions else -1 # İndeksi sıfırla/ayarla
        self.display_question() # UI'ı yeniden çiz
        messagebox.showinfo("Başarılı", f"'{game_name}' oyununun soruları başarıyla kaydedildi!")
        # Oyun listesini de yenile ki yeni oluşturulan oyunlar varsa görünsün
        self.game_names = get_all_game_names_with_questions()
        manual_add_games = ["Kod Hafızası", "GuessOutput", "SyntaxRush", "NumberGuessGame", "TypingGame"]
        for g_name in manual_add_games:
            if g_name not in self.game_names:
                self.game_names.append(g_name)
        self.game_names.sort()
        self.game_selector.config(values=self.game_names)


    def on_show(self):
        """Bu frame her gösterildiğinde çağrılacak metot."""
        print("DEBUG (QuestionEditorFrame): on_show çağrıldı. UI yeniden inşa ediliyor.")
        # build_ui'yi doğrudan çağırmak yerine, mevcut UI'ı güncelleyelim
        self.apply_theme() # Temayı uygula
        # Oyun isimlerini yeniden yükle ve combobox'ı güncelle
        self.game_names = get_all_game_names_with_questions()
        manual_add_games = ["Kod Hafızası", "Output Tahmini", "SyntaxRush", "NumberGuessGame", "TypingGame"]
        for g_name in manual_add_games:
            if g_name not in self.game_names:
                self.game_names.append(g_name)
        self.game_names.sort()
        self.game_selector.config(values=self.game_names)

        # Eğer seçili bir oyun varsa veya yeni bir oyun seçildiyse soruları yükle
        if self.selected_game.get() and self.selected_game.get() != "Oyun Seçin":
            self.on_game_selected() # Seçili oyunu yeniden yükle
        else:
            # Eğer henüz bir oyun seçili değilse veya "Oyun Seçin" ise, varsayılanı ayarla
            if self.game_names:
                self.selected_game.set(self.game_names[0])
                self.on_game_selected()
            else:
                self.selected_game.set("Oyun Seçin") # Hiç oyun yoksa varsayılan
                self.current_questions = []
                self.current_question_index = -1
                self.display_question() # Boş göster


        print("DEBUG (QuestionEditorFrame): on_show tamamlandı.")

    def apply_theme(self):
        print("DEBUG (QuestionEditorFrame): apply_theme başladı.")
        super().apply_theme() # BaseGameFrame'in tema uygulamasını çağır
        theme = get_theme()

        self.config(bg=theme["bg"])

        # Header temalama
        if hasattr(self, 'header_frame') and self.header_frame.winfo_exists():
            self.header_frame.config(bg=theme["header_bg"])
            if hasattr(self, 'header_label') and self.header_label.winfo_exists():
                self.header_label.config(bg=theme["header_bg"], fg=theme["header_fg"])

        if hasattr(self, 'main_content_frame') and self.main_content_frame.winfo_exists():
            self.main_content_frame.config(bg=theme["bg"])

        if hasattr(self, 'game_selection_frame') and self.game_selection_frame.winfo_exists():
            self.game_selection_frame.config(bg=theme["panel_bg"])
            for widget in self.game_selection_frame.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.config(bg=theme["panel_bg"], fg=theme["fg"])
                elif isinstance(widget, ttk.Combobox):
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
                    widget.config(style='TCombobox')


        if hasattr(self, 'question_edit_frame') and self.question_edit_frame.winfo_exists():
            self.question_edit_frame.config(bg=theme["panel_bg"])
            for widget in self.question_edit_frame.winfo_children():
                if isinstance(widget, tk.LabelFrame): # Soru Metni, Doğru Cevap, Seçenekler LabelFrame'leri
                    widget.config(bg=theme["panel_bg"], fg=theme["fg"]) # LabelFrame'in kendisi
                    for sub_widget in widget.winfo_children():
                        if isinstance(sub_widget, (tk.Entry, tk.Text)):
                            sub_widget.config(bg=theme["input_bg"], fg=theme["input_fg"],
                                              insertbackground=theme["input_fg"],
                                              highlightbackground=theme["input_border"], # Kenarlık rengi
                                              highlightcolor=theme["input_border"],      # Odaklanınca kenarlık rengi
                                              bd=1, relief="solid", highlightthickness=1)
                elif isinstance(widget, tk.Label): # Soru sayısı bilgisi etiketi
                    if widget is self.question_info_label:
                        widget.config(bg=theme["panel_bg"], fg=theme["fg"])

        if hasattr(self, 'navigation_frame') and self.navigation_frame.winfo_exists():
            self.navigation_frame.config(bg=theme["bg"])
            for btn in self.navigation_frame.winfo_children():
                if isinstance(btn, tk.Button):
                    # Özel durumlar için renk ayarı (success/error butonları)
                    if "Soru Ekle" in btn.cget("text"):
                         btn.config(bg=theme["success"], fg=theme["fg"], # fg düzeltildi
                                    activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"])
                    elif "Soru Sil" in btn.cget("text"):
                         btn.config(bg=theme["error"], fg=theme["fg"], # fg düzeltildi
                                    activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"])
                    else: # Diğer navigasyon butonları
                        btn.config(bg=theme["button_bg"], fg=theme["button_fg"],
                                   activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"])

        # Ana Menüye Dön butonu (doğrudan root'a bağlı)
        for widget in self.winfo_children():
            if isinstance(widget, tk.Button) and "Admin Paneline Dön" in widget.cget("text"):
                widget.config(bg=theme["button_bg"], fg=theme["button_fg"],
                              activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"])

        print("DEBUG (QuestionEditorFrame): apply_theme tamamlandı.")
