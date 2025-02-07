import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
import json


# Question Loader Class to manage questions
class QuestionLoader:
    def __init__(self, filepath):
        self.filepath = filepath

    def load_questions(self):
        """Load questions from the provided JSON file."""
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
            return data['questions']
        except FileNotFoundError:
            messagebox.showerror("File Not Found", f"Could not find the file: {self.filepath}")
            return []
        except json.JSONDecodeError:
            messagebox.showerror("Invalid File", "There was an error reading the file.")
            return []


# User Progress Tracker
class UserProgress:
    def __init__(self):
        self.correct_answers = 0

    def update_progress(self, is_correct):
        """Update progress based on answer correctness."""
        if is_correct:
            self.correct_answers += 1
        return self.correct_answers


# Main Bot Application Class
class PythonBotApp:
    def __init__(self, root, question_loader, user_progress):
        self.root = root
        self.root.title("CodeBuddy Kai")
        self.root.geometry("800x600")
        self.root.configure(bg="#fefefe")

        self.question_loader = question_loader
        self.user_progress = user_progress
        self.current_question = None
        self.asked_questions = set()

        self.header_label = tk.Label(root, text="CodeBuddy Kai", font=("Comic Sans MS", 28, "bold"), bg="#ffd700")
        self.header_label.pack(fill=tk.X, pady=10)

        self.question_label = tk.Label(root, text="Kai's Question:", font=("Comic Sans MS", 16, "bold"))
        self.question_label.pack()

        self.question_text = tk.Label(root, text="", font=("Comic Sans MS", 14), wraplength=700, justify=tk.LEFT)
        self.question_text.pack(pady=10)

        self.level_label = tk.Label(root, text="Cognitive Level: ", font=("Comic Sans MS", 14, "bold"))
        self.level_label.pack(pady=5)

        self.answer_frame = tk.Frame(root)
        self.answer_frame.pack(pady=10)

        self.code_input = scrolledtext.ScrolledText(root, height=8, width=80, font=("Consolas", 12))
        self.code_input.pack(pady=10)

        self.submit_button = tk.Button(root, text="Submit Answer", command=self.submit_answer, font=("Comic Sans MS", 14, "bold"), state=tk.DISABLED)
        self.submit_button.pack(pady=5)

        self.next_button = tk.Button(root, text="Next Question", command=self.generate_question, font=("Comic Sans MS", 14, "bold"), state=tk.NORMAL)
        self.next_button.pack(pady=5)

        self.progress_label = tk.Label(root, text="Progress: 0 correct answers", font=("Comic Sans MS", 14))
        self.progress_label.pack(pady=10)

        self.log = scrolledtext.ScrolledText(root, height=5, width=80, font=("Comic Sans MS", 12), state=tk.DISABLED)
        self.log.pack(pady=10)

        self.questions = question_loader.load_questions()
        if self.questions:
            self.generate_question()

    def generate_question(self):
        """Generate a random question from the loaded set of questions."""
        if len(self.asked_questions) == len(self.questions):
            messagebox.showinfo("Quiz Complete", "You've answered all questions!")
            return

        self.current_question = random.choice(self.questions)
        while id(self.current_question) in self.asked_questions:
            self.current_question = random.choice(self.questions)

        self.asked_questions.add(id(self.current_question))
        self.display_question()

    def display_question(self):
        """Display the current question and answers."""
        self.question_text.config(text=self.current_question['question'])
        self.level_label.config(text=f"Cognitive Level: {self.current_question['level']}")
        self.code_input.delete('1.0', tk.END)  # Clear the input for the next question
        self.submit_button.config(state=tk.NORMAL)

        # Clear any existing answer checkboxes
        for widget in self.answer_frame.winfo_children():
            widget.destroy()

        if 'answers' in self.current_question:  # Multiple choice question
            self.answer_vars = []
            shuffled_answers = self.current_question['answers'].copy()
            random.shuffle(shuffled_answers)

            for answer in shuffled_answers:
                var = tk.BooleanVar()
                cb = tk.Checkbutton(self.answer_frame, text=answer, variable=var, font=("Comic Sans MS", 12), wraplength=700, justify=tk.LEFT, anchor='w')
                cb.pack(anchor='w', padx=10, pady=2, fill='x')
                self.answer_vars.append((var, answer))
        else:
            self.answer_vars = None

    def submit_answer(self):
        """Handle answer submission and update the progress."""
        if self.answer_vars:  # Multiple choice question
            selected_answers = [ans for var, ans in self.answer_vars if var.get()]
            is_correct = set(selected_answers) == set(self.current_question.get('correct', []))
        else:  # Code question
            user_code = self.code_input.get('1.0', tk.END).strip()
            is_correct = user_code == self.current_question.get('correct_code', '').strip()

        progress = self.user_progress.update_progress(is_correct)

        if is_correct:
            self.log_message(f"Correct answer! Cognitive Level: {self.current_question['level']}")
        else:
            correct_answers = self.current_question.get('correct', [])
            self.log_message(f"Wrong answer! Correct answer(s): {', '.join(correct_answers)}")

        self.progress_label.config(text=f"Progress: {progress} correct answers")
        self.submit_button.config(state=tk.DISABLED)

    def log_message(self, message):
        """Log messages to the application log."""
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, message + "\n")
        self.log.config(state=tk.DISABLED)
        self.log.yview(tk.END)


# Helper function for application initialization
def run_app():
    root = tk.Tk()
    question_loader = QuestionLoader("questions.json")  # Replace with actual file path
    user_progress = UserProgress()
    app = PythonBotApp(root, question_loader, user_progress)
    root.mainloop()


if __name__ == "__main__":
    run_app()
