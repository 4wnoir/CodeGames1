# question_manager.py
import json
import os

QUESTIONS_DIR = "game_questions" # Soruların saklanacağı dizin

def _get_game_questions_path(game_name):
    """Bir oyunun soru dosyasının tam yolunu döndürür."""
    os.makedirs(QUESTIONS_DIR, exist_ok=True) # Dizin yoksa oluştur
    return os.path.join(QUESTIONS_DIR, f"{game_name}_questions.json")

def load_questions(game_name):
    """Belirli bir oyun için soruları yükler."""
    file_path = _get_game_questions_path(game_name)
    if not os.path.exists(file_path):
        print(f"DEBUG (question_manager): '{game_name}' için soru dosyası bulunamadı. Boş liste döndürülüyor.")
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            questions = json.load(f)
            print(f"DEBUG (question_manager): '{game_name}' için sorular başarıyla yüklendi: {len(questions)} adet.")
            return questions
    except json.JSONDecodeError:
        print(f"HATA (question_manager): '{game_name}' soru dosyası bozuk veya geçersiz JSON içeriyor. Boş liste döndürülüyor.")
        return []
    except Exception as e:
        print(f"HATA (question_manager): '{game_name}' soruları yüklenirken hata oluştu: {e}. Boş liste döndürülüyor.")
        return []

def save_questions(game_name, questions):
    """Belirli bir oyun için soruları kaydeder."""
    file_path = _get_game_questions_path(game_name)
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(questions, f, indent=4, ensure_ascii=False)
        print(f"DEBUG (question_manager): '{game_name}' için sorular başarıyla kaydedildi: {len(questions)} adet.")
    except IOError as e:
        print(f"HATA (question_manager): '{game_name}' soru dosyası kaydedilirken hata oluştu: {e}")
    except Exception as e:
        print(f"HATA (question_manager): '{game_name}' soruları kaydedilirken beklenmeyen bir hata oluştu: {e}")

def get_all_game_names_with_questions():
    """Soru dosyası olan tüm oyunların adlarını döndürür."""
    game_names = []
    if os.path.exists(QUESTIONS_DIR):
        for filename in os.listdir(QUESTIONS_DIR):
            if filename.endswith("_questions.json"):
                game_name = filename.replace("_questions.json", "")
                game_names.append(game_name)
    print(f"DEBUG (question_manager): Mevcut soru dosyaları olan oyunlar: {game_names}")
    return sorted(game_names)

# Örnek kullanım (test etmek için):
if __name__ == "__main__":
    # Örnek sorular oluşturma
    sample_code_memory_questions = [
        {"question": "Python'da liste nasıl tanımlanır?", "answer": "liste = [1, 2, 3]", "options": ["liste = {1,2,3}", "liste = (1,2,3)", "liste = \"1,2,3\"", "liste = [1, 2, 3]"]},
        {"question": "C++'da bir int değişkeni nasıl tanımlanır?", "answer": "int sayi;", "options": ["int sayi", "sayi int;", "sayi: int;", "int sayi;"]},
        {"question": "Java'da sınıf nasıl tanımlanır?", "answer": "public class MyClass {}", "options": ["class MyClass {}", "public MyClass class {}", "MyClass class {}", "public class MyClass {}"]},
    ]
    save_questions("Kod Hafızası", sample_code_memory_questions)

    sample_guess_output_questions = [
        {"question": "print(2 + 2)", "answer": "4"},
        {"question": "print('hello' + 'world')", "answer": "helloworld"},
    ]
    save_questions("GuessOutput", sample_guess_output_questions)

    # Soruları yükleme
    loaded_cm_questions = load_questions("Kod Hafızası")
    print("\nYüklenen Kod Hafızası Soruları:")
    for q in loaded_cm_questions:
        print(f"- Soru: {q['question']}, Cevap: {q['answer']}")

    loaded_go_questions = load_questions("GuessOutput")
    print("\nYüklenen GuessOutput Soruları:")
    for q in loaded_go_questions:
        print(f"- Soru: {q['question']}, Cevap: {q['answer']}")

    # Soru dosyası olan tüm oyunları listeleme
    all_games = get_all_game_names_with_questions()
    print(f"\nSoru dosyası olan tüm oyunlar: {all_games}")