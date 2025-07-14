import tkinter as tk
from theme import get_theme

class BaseGameFrame(tk.Frame):
    def __init__(self, parent, controller, game_name_str=None): # game_name_str argümanı eklendi
        super().__init__(parent)
        self.controller = controller
        self.game_name = game_name_str # Oyun adını saklıyoruz
        self.configure(bg=get_theme()["bg"])
        # build_ui'ı burada çağırmıyoruz, çünkü her alt sınıf kendi __init__ metodunda çağıracak.

    def build_ui(self):
        # Ortak UI öğelerini burada tanımlayabilirsiniz, ancak her alt sınıf kendi özel UI'ını oluşturur.
        # Bu metod alt sınıflar tarafından override edilmelidir.
        pass

    def apply_theme(self):
        theme = get_theme()
        self.configure(bg=theme["bg"])
        # Alt sınıflar bu metodu çağırarak kendi widget'larını tema bilgilerine göre güncelleyebilir.