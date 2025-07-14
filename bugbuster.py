import tkinter as tk
from tkinter import messagebox
import random

class BugBusterGame:
    def __init__(self, master):
        self.master = master
        master.title("Bug Buster – Hatalı Kod Avı")
        master.geometry("850x550") # Pencere boyutunu ayarla

        self.questions = [
            {
                "code_snippets": [
                    "print('Hello, Python!')", # Python - Doğru
                    "my_var = 10", # Python - Doğru
                    "if x > 5: pass", # Python - Doğru
                    "for i in range(5); # Yanlış noktalı virgül" # Python - Sözdizimi Hatası
                ],
                "correct_bug_index": 3,
                "language": "Python"
            },
            {
                "code_snippets": [
                    "public class Main { public static void main(String[] args) {} }", # Java - Doğru
                    "int number = 10;", # Java - Doğru
                    "String text = \"Java\";", # Java - Doğru
                    "for (int i = 0; i < 5) {" # Java - Sözdizimi Hatası (i++ eksik)
                ],
                "correct_bug_index": 3,
                "language": "Java"
            },
            {
                "code_snippets": [
                    "console.log('Hello');", # JavaScript - Doğru
                    "let x = 10;", # JavaScript - Doğru
                    "function sum(a, b) { return a + b; }", # JavaScript - Doğru
                    "const my-var = 5;" # JavaScript - Sözdizimi Hatası (değişken adı - içeremez)
                ],
                "correct_bug_index": 3,
                "language": "JavaScript"
            },
            {
                "code_snippets": [
                    "Console.WriteLine(\"Hello\");", # C# - Doğru
                    "int age = 30;", # C# - Doğru
                    "string name = \"Alice\";", # C# - Doğru
                    "if (x == 5 {" # C# - Sözdizimi Hatası (parantez eksik)
                ],
                "correct_bug_index": 3,
                "language": "C#"
            },
            {
                "code_snippets": [
                    "int main() { return 0; }", # C - Doğru
                    "printf(\"Hello\\n\");", # C - Doğru
                    "int *ptr;", # C - Doğru
                    "int my var = 10;" # C - Sözdizimi Hatası (boşluk içeremez)
                ],
                "correct_bug_index": 3,
                "language": "C"
            },
            {
                "code_snippets": [
                    "std::cout << \"Hello\";", # C++ - Doğru
                    "int num = 20;", # C++ - Doğru
                    "class MyClass {};", # C++ - Doğru
                    "for (int i=0; i<10; i++)" # C++ - Sözdizimi Hatası (süslü parantez eksik)
                ],
                "correct_bug_index": 3,
                "language": "C++"
            },
            {
                "code_snippets": [
                    "<?php echo \"Hello\"; ?>", # PHP - Doğru
                    "$name = \"John\";", # PHP - Doğru
                    "function greet() { return \"Hi\"; }", # PHP - Doğru
                    "if ($x == 5" # PHP - Sözdizimi Hatası (parantez eksik)
                ],
                "correct_bug_index": 3,
                "language": "PHP"
            },
            {
                "code_snippets": [
                    "SELECT * FROM Users;", # SQL - Doğru
                    "INSERT INTO Products (Name) VALUES ('Laptop');", # SQL - Doğru
                    "UPDATE Orders SET Status = 'Shipped';", # SQL - Doğru
                    "DELET FROM Customers WHERE ID = 1;" # SQL - Yazım Hatası (DELETE yerine DELET)
                ],
                "correct_bug_index": 3,
                "language": "SQL"
            },
            {
                "code_snippets": [
                    "<h1>Hello</h1>", # HTML/CSS - Doğru HTML
                    "p { color: blue; }", # HTML/CSS - Doğru CSS
                    "<img src=\"image.jpg\">", # HTML/CSS - Doğru HTML
                    "div { text-align: center; color:blue }" # HTML/CSS - Sözdizimi Hatası (noktalı virgül eksik)
                ],
                "correct_bug_index": 3,
                "language": "HTML/CSS"
            },
            {
                "code_snippets": [
                    "fun main() { println(\"Hello\"); }", # Kotlin - Doğru
                    "val message = \"Kotlin\";", # Kotlin - Doğru
                    "class MyClass", # Kotlin - Doğru (eğer boş sınıfsa)
                    "var num: Int = \"text\"" # Kotlin - Tip Uyumsuzluğu Hatası
                ],
                "correct_bug_index": 3,
                "language": "Kotlin"
            }
        ]

        self.current_question_index = -1
        self.score = 0
        self.lives = 3
        self.timer_id = None
        self.time_left = 10 # Her soru için 10 saniye

        self.create_widgets()
        self.next_question()

    # ... (Geri kalan tüm fonksiyonlar (next_question, start_timer, update_timer, check_answer, lose_life, end_game, reset_game, show_help) önceki BugBuster kodundan aynen alınır.) ...

    def create_widgets(self):
        # ... (Önceki BugBuster kodundan başlık, skor, can, süre vb. kısımları aynen al) ...
        self.header_frame = tk.Frame(self.master, bg="#555", pady=10)
        self.header_frame.pack(fill=tk.X)

        self.title_label = tk.Label(self.header_frame, text="Bug Buster", fg="white", bg="#555", font=("Arial", 24, "bold"))
        self.title_label.pack(side=tk.LEFT, padx=20)

        self.score_label = tk.Label(self.header_frame, text=f"Skor: {self.score}", fg="white", bg="#555", font=("Arial", 16))
        self.score_label.pack(side=tk.RIGHT, padx=20)

        self.lives_label = tk.Label(self.header_frame, text=f"Can: {self.lives}", fg="red", bg="#555", font=("Arial", 16, "bold"))
        self.lives_label.pack(side=tk.RIGHT, padx=10)

        self.timer_label = tk.Label(self.header_frame, text=f"Süre: {self.time_left}", fg="yellow", bg="#555", font=("Arial", 16))
        self.timer_label.pack(side=tk.RIGHT, padx=10)

        self.question_frame = tk.Frame(self.master, pady=20, padx=20)
        self.question_frame.pack(expand=True, fill=tk.BOTH)

        self.language_label = tk.Label(self.question_frame, text="Dil: ", font=("Courier New", 14, "italic"), fg="#0056b3")
        self.language_label.pack(anchor="nw", pady=(0, 10))

        self.code_buttons = []
        for i in range(4):
            button = tk.Button(self.question_frame, text="", font=("Courier New", 12),
                               bg="#f0f0f0", anchor="w", justify="left", wraplength=700,
                               command=lambda idx=i: self.check_answer(idx))
            button.pack(fill=tk.X, pady=5)
            self.code_buttons.append(button)

        self.footer_frame = tk.Frame(self.master, pady=10)
        self.footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.reset_button = tk.Button(self.footer_frame, text="Yeniden Başla", font=("Arial", 14), command=self.reset_game)
        self.reset_button.pack(side=tk.LEFT, padx=20)

        self.help_button = tk.Button(self.footer_frame, text="Yardım", font=("Arial", 14), command=self.show_help)
        self.help_button.pack(side=tk.RIGHT, padx=20)

    def next_question(self):
        if self.lives <= 0:
            self.end_game()
            return

        if self.timer_id:
            self.master.after_cancel(self.timer_id)

        self.current_question_index = random.randrange(len(self.questions))
        current_q = self.questions[self.current_question_index]

        shuffled_snippets = list(enumerate(current_q["code_snippets"]))
        random.shuffle(shuffled_snippets)

        self.bugged_snippet_index_in_shuffled = -1
        for i, (original_idx, snippet) in enumerate(shuffled_snippets):
            self.code_buttons[i].config(text=f"{i+1}. {snippet}", state=tk.NORMAL, bg="#f0f0f0")
            if original_idx == current_q["correct_bug_index"]:
                self.bugged_snippet_index_in_shuffled = i

        self.language_label.config(text=f"Dil: {current_q['language']}")
        self.time_left = 10
        self.update_timer()
        self.start_timer()

    def start_timer(self):
        self.timer_id = self.master.after(1000, self.update_timer)

    def update_timer(self):
        self.time_left -= 1
        self.timer_label.config(text=f"Süre: {self.time_left}")

        if self.time_left <=