# theme.py - GÜNCEL (set_theme, get_all_theme_names, get_current_theme_name)

# Mevcut tema ve tema ayarları için global değişkenler
_current_theme_name = "Koyu Tema" # Varsayılan tema
_themes = {
    "Açık Tema": {
        "bg": "#f0f0f0",
        "fg": "#333333",
        "header_bg": "#e0e0e0",
        "header_fg": "#000000",
        "button_bg": "#cccccc",
        "button_fg": "#000000",
        "active_button_bg": "#aaaaaa",
        "active_button_fg": "#000000",
        "panel_bg": "#ffffff",
        "input_bg": "#e6e6e6",
        "input_fg": "#000000",
        "input_border": "#999999",
        "code_bg": "#e0e0e0",
        "code_fg": "#000000",
        "correct_color": "#d4edda", # Açık yeşil
        "wrong_color": "#f8d7da",   # Açık kırmızı
        "error": "#dc3545",         # Kırmızı
        "success": "#28a745",       # Yeşil
        "card_back_color": "#cccccc",
        "card_front_color": "#ffffff",
        "matched_card_color": "#d4edda",
        "card_text_color": "#000000",
        "entry_bg": "#e6e6e6",
        "entry_fg": "#000000",
        "game_card_bg": "#ffffff", # Oyun kartlarının arka planı
        "game_card_fg": "#333333", # Oyun kartlarının metin rengi
        "play_button_bg": "#ffffff", # Oyna düğmesinin arka planı (BEYAZ YAPILDI)
        "play_button_fg": "#333333", # Oyna düğmesinin metin rengi (KOYU GRİ YAPILDI)
        "active_play_button_bg": "#e0e0e0", # Oyna düğmesinin aktif arka planı (AÇIK GRİ YAPILDI)
        "active_play_button_fg": "#333333", # Oyna düğmesinin aktif metin rengi (KOYU GRİ YAPILDI)
    },
    "Koyu Tema": {
        "bg": "#2e2e2e",
        "fg": "#ffffff",
        "header_bg": "#3c3c3c",
        "header_fg": "#ffffff",
        "button_bg": "#555555",
        "button_fg": "#ffffff",
        "active_button_bg": "#777777",
        "active_button_fg": "#ffffff",
        "panel_bg": "#3a3a3a",
        "input_bg": "#4a4a4a",
        "input_fg": "#ffffff",
        "input_border": "#777777",
        "code_bg": "#3a3a3a",
        "code_fg": "#ffffff",
        "correct_color": "#28a745", # Koyu yeşil
        "wrong_color": "#dc3545",   # Koyu kırmızı
        "error": "#dc3545",         # Kırmızı
        "success": "#28a745",       # Yeşil
        "card_back_color": "#555555",
        "card_front_color": "#3a3a3a",
        "matched_card_color": "#28a745",
        "card_text_color": "#ffffff",
        "entry_bg": "#4a4a4a",
        "entry_fg": "#ffffff",
        "game_card_bg": "#222222", # Daha koyu gri
        "game_card_fg": "#ffffff", # Beyaz metin
        "play_button_bg": "#333333", # Daha koyu gri
        "play_button_fg": "#ffffff", # Beyaz metin
        "active_play_button_bg": "#444444", # Aktif durumda biraz daha açık koyu gri
        "active_play_button_fg": "#ffffff", # Beyaz metin
    },
}

def get_theme():
    """Mevcut seçili temanın renk sözlüğünü döndürür."""
    return _themes.get(_current_theme_name, _themes["Koyu Tema"]) # Varsayılan olarak Koyu Tema

def set_theme(theme_name):
    """Uygulamanın temasını ayarlar."""
    global _current_theme_name
    if theme_name in _themes:
        _current_theme_name = theme_name
        print(f"DEBUG (theme.py): Tema '{_current_theme_name}' olarak ayarlandı.")
    else:
        print(f"UYARI (theme.py): '{theme_name}' adında bir tema bulunamadı. Tema değiştirilmedi.")
        if _current_theme_name not in _themes:
            _current_theme_name = list(_themes.keys())[0] if _themes else "Koyu Tema"
            print(f"UYARI (theme.py): Mevcut tema kaldırıldığı için varsayılan tema '{_current_theme_name}' olarak ayarlandı.")

def get_all_theme_names():
    """Mevcut tüm tema isimlerinin bir listesini döndürür."""
    return list(_themes.keys())

def get_current_theme_name():
    """Şu anda aktif olan temanın adını döndürür."""
    return _current_theme_name

# Başlangıçta varsayılan temayı ayarla
set_theme(_current_theme_name)
