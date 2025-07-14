import tkinter as tk
from tkinter import messagebox
from base_frame import BaseGameFrame
from theme import get_theme


class FeedbackFrame(BaseGameFrame):

    def __init__(self, parent, controller):
        print("FeedbackFrame: __init__ başladı.")
        self.game_name = "Geri Bildirim"  # Game adı olarak kullandık
        super().__init__(parent, controller)
        print("FeedbackFrame: __init__ tamamlandı.")

    def build_ui(self):
        print("FeedbackFrame: build_ui başladı.")
        super().build_ui()  # BaseGameFrame'in temel bg ayarını yapar
        theme = get_theme()

        # Başlık ve header_frame oluşturma (Feedback'e özel)
        if not hasattr(self, 'header_frame') or not self.header_frame.winfo_exists():
            self.header_frame = tk.Frame(self, bg=theme["header_bg"])
            self.header_frame.pack(side="top", fill="x", pady=10)
            self.header_label = tk.Label(self.header_frame, text=self.game_name,
                                         font=("Arial", 28, "bold"),
                                         bg=theme["header_bg"], fg=theme["header_fg"])
            self.header_label.pack(expand=True)
        else:
            self.header_label.config(text=self.game_name)

        # Ana içerik çerçevesi
        if hasattr(self, 'main_content_frame') and self.main_content_frame.winfo_exists():
            self.main_content_frame.destroy()

        self.main_content_frame = tk.Frame(self, bg=theme["bg"])
        self.main_content_frame.pack(side="top", fill="both", expand=True, padx=20, pady=20)
        print("FeedbackFrame: main_content_frame oluşturuldu ve pack edildi.")

        # Geri Bildirim Formu Çerçevesi
        self.feedback_form_frame = tk.Frame(self.main_content_frame, bg=theme["panel_bg"], bd=2, relief="groove")
        self.feedback_form_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        self.feedback_form_frame.grid_columnconfigure(0, weight=1)
        self.feedback_form_frame.grid_columnconfigure(1, weight=3)
        self.feedback_form_frame.grid_rowconfigure(0, weight=0)
        self.feedback_form_frame.grid_rowconfigure(1, weight=0)
        self.feedback_form_frame.grid_rowconfigure(2, weight=1)
        self.feedback_form_frame.grid_rowconfigure(3, weight=0)

        tk.Label(self.feedback_form_frame, text="Adınız (İsteğe Bağlı):", font=("Arial", 16),
                 bg=theme["panel_bg"], fg=theme["fg"]).grid(row=0, column=0, sticky="w", padx=20, pady=10)
        self.name_entry = tk.Entry(self.feedback_form_frame, font=("Arial", 16),
                                   bg=theme["input_bg"], fg=theme["input_fg"], insertbackground=theme["input_fg"])
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=20, pady=10)

        tk.Label(self.feedback_form_frame, text="Konu:", font=("Arial", 16),
                 bg=theme["panel_bg"], fg=theme["fg"]).grid(row=1, column=0, sticky="w", padx=20, pady=10)
        self.subject_entry = tk.Entry(self.feedback_form_frame, font=("Arial", 16),
                                      bg=theme["input_bg"], fg=theme["input_fg"], insertbackground=theme["input_fg"])
        self.subject_entry.grid(row=1, column=1, sticky="ew", padx=20, pady=10)

        tk.Label(self.feedback_form_frame, text="Mesajınız:", font=("Arial", 16),
                 bg=theme["panel_bg"], fg=theme["fg"]).grid(row=2, column=0, sticky="nw", padx=20, pady=10)
        self.message_text = tk.Text(self.feedback_form_frame, height=10, font=("Arial", 16),
                                    bg=theme["input_bg"], fg=theme["input_fg"], insertbackground=theme["input_fg"])
        self.message_text.grid(row=2, column=1, sticky="nsew", padx=20, pady=10)

        button_frame = tk.Frame(self.feedback_form_frame, bg=theme["panel_bg"])
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        tk.Button(button_frame, text="Gönder", font=("Arial", 16), command=self.send_feedback,
                  bg=theme["button_bg"], fg=theme["button_fg"],
                  activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"]).grid(row=0,
                                                                                                               column=0,
                                                                                                               padx=10,
                                                                                                               sticky="ew")
        tk.Button(button_frame, text="Ana Menü", font=("Arial", 16),
                  command=lambda: self.controller.show_frame("MainMenu"),
                  bg=theme["button_bg"], fg=theme["button_fg"],
                  activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"]).grid(row=0,
                                                                                                               column=1,
                                                                                                               padx=10,
                                                                                                               sticky="ew")

        print("FeedbackFrame: build_ui tamamlandı.")

    def send_feedback(self):
        name = self.name_entry.get().strip()
        subject = self.subject_entry.get().strip()
        message = self.message_text.get(1.0, tk.END).strip()

        if not subject or not message:
            messagebox.showwarning("Uyarı", "Lütfen konu ve mesaj alanlarını doldurun.", parent=self)
            return

        feedback_info = f"Ad: {name if name else 'Anonim'}\nKonu: {subject}\nMesaj:\n{message}\n\n"
        print("Geri Bildirim Alındı:\n", feedback_info)

        # Geri bildirimi dosyaya kaydet
        with open("feedback.txt", "a", encoding="utf-8") as file:
            file.write(feedback_info)

        messagebox.showinfo("Teşekkürler!", "Geri bildiriminiz için teşekkür ederiz!", parent=self)

        # Alanları temizle
        self.name_entry.delete(0, tk.END)
        self.subject_entry.delete(0, tk.END)
        self.message_text.delete(1.0, tk.END)

        # Ana menüye dön
        self.controller.show_frame("MainMenu")

    def apply_theme(self):
        print("FeedbackFrame: apply_theme başladı.")
        super().apply_theme()  # BaseGameFrame'in tema uygulamasını çağır
        theme = get_theme()

        # Header temalama
        if hasattr(self, 'header_frame') and self.header_frame.winfo_exists():
            self.header_frame.config(bg=theme["header_bg"])
        if hasattr(self, 'header_label') and self.header_label.winfo_exists():
            self.header_label.config(bg=theme["header_bg"], fg=theme["header_fg"])

        # main_content_frame'i temala
        if hasattr(self, 'main_content_frame') and self.main_content_frame.winfo_exists():
            self.main_content_frame.config(bg=theme["bg"])

            # feedback_form_frame ve içindeki widget'ları temala
            if hasattr(self, 'feedback_form_frame') and self.feedback_form_frame.winfo_exists():
                self.feedback_form_frame.config(bg=theme["panel_bg"])
                for widget in self.feedback_form_frame.winfo_children():
                    if isinstance(widget, tk.Label):
                        widget.config(bg=theme["panel_bg"], fg=theme["fg"])
                    elif isinstance(widget, (tk.Entry, tk.Text)):
                        widget.config(bg=theme["input_bg"], fg=theme["input_fg"], insertbackground=theme["input_fg"])
                    elif isinstance(widget, tk.Frame):  # button_frame
                        widget.config(bg=theme["panel_bg"])
                        for btn in widget.winfo_children():
                            if isinstance(btn, tk.Button):
                                btn.config(bg=theme["button_bg"], fg=theme["button_fg"],
                                           activebackground=theme["active_button_bg"],
                                           activeforeground=theme["active_button_fg"])
        print("FeedbackFrame: apply_theme tamamlandı.")
