# admin_login_frame.py - Admin Giriş Ekranı
import tkinter as tk
from tkinter import messagebox
from theme import get_theme
from base_frame import BaseGameFrame

class AdminLoginFrame(BaseGameFrame):
    def __init__(self, parent, controller, game_name_str=None):
        self.game_name = "Admin Giriş" # Bu frame'in başlığı
        super().__init__(parent, controller, self.game_name)
        self.build_ui()

    def build_ui(self):
        print("DEBUG: AdminLoginFrame: build_ui başladı.")
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
        print("DEBUG: AdminLoginFrame: Header UI kuruldu.")

        # Giriş alanı çerçevesi
        login_frame = tk.Frame(self, bg=theme["panel_bg"], bd=2, relief="groove")
        login_frame.place(relx=0.5, rely=0.5, anchor="center") # Ortala
        print("DEBUG: AdminLoginFrame: Giriş çerçevesi oluşturuldu.")

        tk.Label(login_frame, text="Admin Girişi", font=("Arial", 24, "bold"),
                 bg=theme["panel_bg"], fg=theme["fg"]).pack(pady=20)

        # Kullanıcı Adı
        tk.Label(login_frame, text="Kullanıcı Adı:", font=("Arial", 16),
                 bg=theme["panel_bg"], fg=theme["fg"]).pack(pady=5)
        self.username_entry = tk.Entry(login_frame, font=("Arial", 16),
                                       bg=theme["entry_bg"], fg=theme["entry_fg"],
                                       insertbackground=theme["entry_fg"],
                                       highlightbackground=theme["input_border"], highlightthickness=1)
        self.username_entry.pack(pady=5, padx=20)
        print("DEBUG: AdminLoginFrame: Kullanıcı adı girişi oluşturuldu.")

        # Şifre
        tk.Label(login_frame, text="Şifre:", font=("Arial", 16),
                 bg=theme["panel_bg"], fg=theme["fg"]).pack(pady=5)
        self.password_entry = tk.Entry(login_frame, show="*", font=("Arial", 16),
                                       bg=theme["entry_bg"], fg=theme["entry_fg"],
                                       insertbackground=theme["entry_fg"],
                                       highlightbackground=theme["input_border"], highlightthickness=1)
        self.password_entry.pack(pady=5, padx=20)
        self.password_entry.bind("<Return>", lambda event: self.check_credentials()) # Enter tuşu ile giriş
        print("DEBUG: AdminLoginFrame: Şifre girişi oluşturuldu.")

        # Giriş Butonu
        login_button = tk.Button(login_frame, text="Giriş Yap", font=("Arial", 16, "bold"),
                                 command=self.check_credentials,
                                 bg=theme["button_bg"], fg=theme["button_fg"],
                                 activebackground=theme["active_button_bg"],
                                 activeforeground=theme["active_button_fg"])
        login_button.pack(pady=20)
        print("DEBUG: AdminLoginFrame: Giriş butonu oluşturuldu.")

        # Ana Menüye Dön butonu
        back_button = tk.Button(self, text="⬅️ Ana Menüye Dön", font=("Arial", 16),
                                command=lambda: self.controller.show_frame("MainMenu"),
                                bg=theme["button_bg"], fg=theme["button_fg"],
                                activebackground=theme["active_button_bg"],
                                activeforeground=theme["active_button_fg"])
        back_button.pack(pady=20)
        print("DEBUG: AdminLoginFrame: Ana Menüye Dön butonu kuruldu.")

        self.apply_theme() # Temayı uygula
        print("DEBUG: AdminLoginFrame: build_ui tamamlandı.")

    def check_credentials(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Basit bir örnek admin kullanıcı adı ve şifresi
        # GERÇEK BİR UYGULAMADA ASLA BU KADAR BASİT BİR YÖNTEM KULLANMAYIN!
        # Veritabanı veya güvenli bir kimlik doğrulama sistemi kullanılmalıdır.
        if username == "admin" and password == "admin123":
            messagebox.showinfo("Giriş Başarılı", "Admin Paneline hoş geldiniz!", parent=self)
            self.controller.show_frame("AdminPanel") # Admin paneline yönlendir
            print("DEBUG: AdminLoginFrame: Giriş başarılı, AdminPanel'e yönlendiriliyor.")
        else:
            messagebox.showerror("Giriş Başarısız", "Yanlış kullanıcı adı veya şifre.", parent=self)
            print("DEBUG: AdminLoginFrame: Giriş başarısız.")

    def on_show(self):
        """Bu frame her gösterildiğinde çağrılır."""
        print("DEBUG: AdminLoginFrame: on_show çağrıldı.")
        self.apply_theme() # Tema güncellemelerini uygula
        # Giriş alanlarını temizle
        if hasattr(self, 'username_entry') and self.username_entry.winfo_exists():
            self.username_entry.delete(0, tk.END)
        if hasattr(self, 'password_entry') and self.password_entry.winfo_exists():
            self.password_entry.delete(0, tk.END)
        print("DEBUG: AdminLoginFrame: on_show tamamlandı.")

    def reset_game(self):
        """AdminLogin için reset_game, giriş alanlarını temizler."""
        print("DEBUG: AdminLoginFrame: reset_game çağrıldı (giriş alanları temizleniyor).")
        if hasattr(self, 'username_entry') and self.username_entry.winfo_exists():
            self.username_entry.delete(0, tk.END)
        if hasattr(self, 'password_entry') and self.password_entry.winfo_exists():
            self.password_entry.delete(0, tk.END)
        print("DEBUG: AdminLoginFrame: reset_game tamamlandı.")


    def apply_theme(self):
        print("DEBUG: AdminLoginFrame: apply_theme başladı.")
        super().apply_theme()
        theme = get_theme()

        self.config(bg=theme["bg"])

        if hasattr(self, 'header_frame') and self.header_frame.winfo_exists():
            self.header_frame.config(bg=theme["header_bg"])
        if hasattr(self, 'header_label') and self.header_label.winfo_exists():
            self.header_label.config(bg=theme["header_bg"], fg=theme["header_fg"])

        # Giriş çerçevesi ve içindeki widget'ları temala
        for widget in self.winfo_children():
            if isinstance(widget, tk.Frame) and widget.winfo_exists(): # login_frame'i bul
                # Bu kontrolü daha spesifik hale getirebiliriz, örneğin widget.master == self ve widget'ın belirli bir adı/rolü varsa
                # Ancak şimdilik bu şekilde bırakıyorum, çünkü login_frame tek Frame widget'ı olabilir.
                widget.config(bg=theme["panel_bg"])
                for sub_widget in widget.winfo_children():
                    if isinstance(sub_widget, tk.Label):
                        sub_widget.config(bg=theme["panel_bg"], fg=theme["fg"])
                    elif isinstance(sub_widget, tk.Entry):
                        sub_widget.config(bg=theme["entry_bg"], fg=theme["entry_fg"],
                                          insertbackground=theme["entry_fg"],
                                          highlightbackground=theme["input_border"], highlightthickness=1)
                    elif isinstance(sub_widget, tk.Button):
                        sub_widget.config(bg=theme["button_bg"], fg=theme["button_fg"],
                                          activebackground=theme["active_button_bg"],
                                          activeforeground=theme["active_button_fg"])
            elif isinstance(widget, tk.Button) and widget.winfo_exists(): # Ana Menüye Dön butonu
                widget.config(bg=theme["button_bg"], fg=theme["button_fg"],
                              activebackground=theme["active_button_bg"],
                              activeforeground=theme["active_button_fg"])
        print("DEBUG: AdminLoginFrame: apply_theme tamamlandı.")
