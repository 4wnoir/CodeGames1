# score_manager.py - GÜNCELLENDİ (delete_score fonksiyonu eklendi, reset_scores_for_game kaldırıldı)
import json
import os
import time
from datetime import datetime # Tarih formatlama için eklendi

SCORE_FILE = 'scores.json'

def load_scores():
    """Skorları JSON dosyasından yükler."""
    if not os.path.exists(SCORE_FILE):
        print(f"DEBUG: '{SCORE_FILE}' dosyası bulunamadı. Boş skorlar döndürülüyor.")
        return {}
    try:
        with open(SCORE_FILE, 'r', encoding='utf-8') as f:
            scores = json.load(f)
            print(f"DEBUG: '{SCORE_FILE}' başarıyla yüklendi.")
            return scores
    except json.JSONDecodeError:
        print(f"Hata: '{SCORE_FILE}' dosyası bozuk veya geçersiz JSON içeriyor. Yeni bir dosya oluşturuluyor.")
        return {}
    except Exception as e:
        print(f"Hata: '{SCORE_FILE}' yüklenirken beklenmeyen bir hata oluştu: {e}")
        return {}

def save_scores(scores):
    """Skorları JSON dosyasına kaydeder."""
    try:
        with open(SCORE_FILE, 'w', encoding='utf-8') as f:
            json.dump(scores, f, indent=4, ensure_ascii=False)
        print(f"DEBUG: Skorlar '{SCORE_FILE}' dosyasına başarıyla kaydedildi.")
    except IOError as e:
        print(f"Hata: Skor dosyası '{SCORE_FILE}' kaydedilirken bir hata oluştu: {e}")
    except Exception as e:
        print(f"Hata: Skorlar kaydedilirken beklenmeyen bir hata oluştu: {e}")

def save_score(game_name, player_name, score_value, is_time_score=False, elapsed_time=None):
    """
    Belirli bir oyun için skoru kaydeder.
    score_value: Oyunun ana skoru (örn. puan).
    is_time_score: Eğer score_value doğrudan zamanı temsil ediyorsa (düşük daha iyi).
    elapsed_time: Oyunun bitirilme süresi (saniye cinsinden).
    """
    print(f"DEBUG: save_score çağrıldı. Oyun: {game_name}, Oyuncu: {player_name}, Skor: {score_value}, Zaman Skoru: {is_time_score}, Geçen Süre: {elapsed_time}")
    scores = load_scores()

    if game_name not in scores:
        scores[game_name] = []

    new_score_entry = {
        "player_name": player_name,
        "score": score_value,
        "timestamp": time.time(), # Zaman damgası eklendi
        "time_taken": elapsed_time # elapsed_time her zaman kaydedilsin, None olabilir
    }
    scores[game_name].append(new_score_entry)

    # Skorları sırala
    # is_time_score True ise, 'score' alanı zamanı temsil eder ve daha düşük daha iyidir.
    # is_time_score False ise, 'score' alanı puanı temsil eder ve daha yüksek daha iyidir.
    # Eğer zaman skoru değilse, önce puana göre azalan, sonra zamana göre artan sırala.
    # Eğer zaman skoru ise, önce zamana göre artan, sonra puana göre azalan sırala.
    if is_time_score:
        scores[game_name].sort(key=lambda x: (x.get('score', float('inf')), -x.get('timestamp', 0))) # Düşük skor (zaman) daha iyi, aynı skorda son kaydedilen önde
    else:
        scores[game_name].sort(key=lambda x: (x.get('score', 0), -x.get('timestamp', 0)), reverse=True) # Yüksek skor (puan) daha iyi, aynı skorda son kaydedilen önde


    scores[game_name] = scores[game_name][:10] # En iyi 10 skoru tut

    save_scores(scores)
    print(f"DEBUG: Skor '{player_name}' ({score_value} puan, {elapsed_time} saniye) başarıyla işlendi ve kaydedildi.")


def get_top_scores_for_game(game_name, num_scores=5):
    """Belirli bir oyun için en iyi skorları döndürür."""
    print(f"DEBUG: get_top_scores_for_game çağrıldı. Oyun: {game_name}, İstenen skor sayısı: {num_scores}")
    scores = load_scores()
    top_scores = scores.get(game_name, [])

    # Sıralama mantığını save_score ile aynı tutalım
    # Ancak burada is_time_score bilgisini bilmiyoruz, bu yüzden varsayılan olarak puana göre sıralayalım.
    # Veya, skor yapısı içinde is_time_score bilgisini de tutabiliriz.
    # Şimdilik, genel bir sıralama yapalım: önce puan (azalan), sonra zaman (artan).
    top_scores.sort(key=lambda x: (x.get('score', 0), x.get('time_taken', float('inf')) if x.get('time_taken') is not None else float('inf')), reverse=True)

    top_scores = top_scores[:num_scores] # En iyi 'num_scores' kadarını al
    print(f"DEBUG: '{game_name}' için döndürülen en iyi skorlar: {top_scores}")
    return top_scores

def delete_score(game_name, player_name=""):
    """
    Belirli bir oyun ve oyuncuya ait skorları siler.
    player_name boş bırakılırsa, o oyuna ait tüm skorları siler.
    """
    print(f"DEBUG: delete_score çağrıldı. Oyun: {game_name}, Oyuncu: '{player_name if player_name else 'TÜM'}'")
    scores = load_scores()
    deleted_count = 0
    message = ""
    success = False

    if game_name in scores:
        initial_count = len(scores[game_name])
        if player_name:
            # Belirtilen oyuncu adına sahip olmayan skorları filtrele
            # Büyük/küçük harf duyarsız arama için .lower() kullanıldı
            scores[game_name] = [
                score for score in scores[game_name]
                if score.get("player_name", "").lower() != player_name.lower()
            ]
            deleted_count = initial_count - len(scores[game_name])
            if deleted_count > 0:
                message = f"'{game_name}' oyunundan '{player_name}' adlı oyuncuya ait {deleted_count} skor silindi."
                success = True
            else:
                message = f"'{game_name}' oyununda '{player_name}' adlı oyuncuya ait skor bulunamadı."
        else:
            # Oyuncu adı boşsa, o oyuna ait tüm skorları sil
            deleted_count = initial_count
            scores[game_name] = []
            message = f"'{game_name}' oyununa ait tüm {deleted_count} skor silindi."
            success = True

        save_scores(scores)
        print(f"DEBUG: Skor silme işlemi tamamlandı. Sonuç: {message}")
        return success, message
    else:
        message = f"'{game_name}' oyunu için skor bulunamadı."
        print(f"DEBUG: Skor silme işlemi başarısız. {message}")
        return False, message

def clear_all_scores():
    """Tüm oyunların skorlarını siler."""
    print("DEBUG: clear_all_scores çağrıldı.")
    try:
        if os.path.exists(SCORE_FILE):
            os.remove(SCORE_FILE)
            print(f"DEBUG: Tüm skor dosyası ('{SCORE_FILE}') silindi.")
        else:
            print(f"DEBUG: '{SCORE_FILE}' zaten mevcut değil, silme işlemi yapılmadı.")
        return True
    except Exception as e:
        print(f"HATA: Tüm skorlar silinirken bir hata oluştu: {e}")
        return False