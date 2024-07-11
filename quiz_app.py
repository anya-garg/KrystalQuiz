import csv
import random
import streamlit as st
import pandas as pd
import ast

class QuestionBank:
    def __init__(self, csv_file='question_bank.csv'):
        self.topics = {}
        self.load_questions_from_csv(csv_file)

    def load_questions_from_csv(self, csv_file):
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                topic = row['topic']
                if topic not in self.topics:
                    self.topics[topic] = []
                
                for key in ['question', 'correct_answer', 'wrong_answer_1', 'wrong_answer_2', 'wrong_answer_3']:
                    try:
                        row[key] = ast.literal_eval(row[key])
                    except (ValueError, SyntaxError):
                        pass
                
                row['explanation'] = row['explanation']
                
                try:
                    row['explanation_pages'] = [int(page) for page in ast.literal_eval(row['explanation_pages'])]
                except (ValueError, SyntaxError):
                    row['explanation_pages'] = []
                
                self.topics[topic].append(row)

    def get_questions_from_topics(self, selected_topics, num_questions):
        all_questions = []
        for topic in selected_topics:
            if topic in self.topics and self.topics[topic]:
                all_questions.extend(self.topics[topic])
        if not all_questions:
            raise ValueError("No questions available for the selected topics.")
        return random.sample(all_questions, min(num_questions, len(all_questions)))

    def get_available_topics(self):
        return list(self.topics.keys())
class Quiz:
    def __init__(self, name, question_bank):
        self.name = name
        self.question_bank = question_bank
        self.score = []
        self.current_question = 0
        self.questions = []
        self.selected_topics = []
        self.start_time = None
        self.end_time = None

    def run(self):
        try:
            self.start_time = datetime.now()
            self.questions = self.question_bank.get_questions_from_topics(self.selected_topics, 10)
            self.current_question = 0
            self.score = []
            self.display_question()
        except ValueError as e:
            print(f"Error: {str(e)}")
            print("Please make sure you've selected topics with available questions.")

    def display_question(self):
        if self.current_question < len(self.questions):
            q = self.questions[self.current_question]

            question_text = widgets.HTML(value=f"<b>{self.current_question + 1}. {q['question']['answer'] if isinstance(q['question'], dict) else q['question']}</b>")

            answers = [
                q['correct_answer']['answer'] if isinstance(q['correct_answer'], dict) else q['correct_answer'],
                q['wrong_answer_1']['answer'] if isinstance(q['wrong_answer_1'], dict) else q['wrong_answer_1'],
                q['wrong_answer_2']['answer'] if isinstance(q['wrong_answer_2'], dict) else q['wrong_answer_2'],
                q['wrong_answer_3']['answer'] if isinstance(q['wrong_answer_3'], dict) else q['wrong_answer_3']
            ]
            random.shuffle(answers)

            options = ['A', 'B', 'C', 'D']
            radio_options = [f"{opt}. {ans}" for opt, ans in zip(options, answers)]

            radio = widgets.RadioButtons(options=radio_options, layout={'width': 'max-content'})

            submit_button = widgets.Button(description="Submit")
            output = widgets.Output()

            def on_submit(b):
                with output:
                    clear_output()
                    if not radio.value:
                        print("Please select an answer.")
                        return

                    selected_option = radio.value[0]  
                    correct_answer = q['correct_answer']['answer'] if isinstance(q['correct_answer'], dict) else q['correct_answer']
                    is_correct = answers[options.index(selected_option)] == correct_answer

                    if is_correct:
                        print("Correct!")
                        self.score.append(True)
                    else:
                        print(f"Wrong! The correct answer was: {correct_answer}")
                        self.score.append(False)

                    print("\nQuote from text:")
                    print(q['explanation'])

                    if q['explanation_pages']:
                        print("\nRelevant Pages:", ", ".join(map(str, q['explanation_pages'])))

                    self.current_question += 1
                    if self.current_question < len(self.questions):
                        print("\nMoving to next question...")
                        self.display_question()
                    else:
                        self.show_results()

            submit_button.on_click(on_submit)

            display(question_text, radio, submit_button, output)


    def show_results(self):
        self.end_time = datetime.now()
        correct_answers = sum(self.score)
        total_questions = len(self.score)
        result_text = f"{self.name}, you got {correct_answers} out of {total_questions} correct!"
        display(widgets.HTML(f"<h3>{result_text}</h3>"))
        
        self.save_results_to_csv(correct_answers, total_questions)

    def save_results_to_csv(self, correct_answers, total_questions):
        results_file = 'quiz_results.csv'
        file_exists = os.path.isfile(results_file)
        
        with open(results_file, 'a', newline='') as csvfile:
            fieldnames = ['Name', 'Date', 'Time', 'Score', 'Total Questions']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow({
                'Name': self.name,
                'Date': self.end_time.strftime('%Y-%m-%d'),
                'Time': self.end_time.strftime('%H:%M:%S'),
                'Score': f"{correct_answers}/{total_questions}",
                'Total Questions': total_questions
            })
def run_quiz_application():
    question_bank = QuestionBank('question_bank.csv')

    print("Welcome to the Securities and Futures Act 2001 Quiz. This quiz contains 10 questions. You may change your answer before entering 'Submit'. all questions are pulled from the document: https://datahub.ucsd.edu/user/a7garg/files/private/Securities%20and%20Futures%20Act%202001.pdf.You may use it as reference. Good luck!")
    output = widgets.Output()

    name_input = widgets.Text(description="Your Name:")
    start_quiz_button = widgets.Button(description="Start Quiz")
    start_quiz_button.disabled = True  

    def on_selection_confirmed(b):
        with output:
            clear_output()
            print("Topics selected. Please enter your name and click 'Start Quiz'.")
        name_input.layout.visibility = 'visible'
        start_quiz_button.disabled = False

    def start_quiz(b):
        name = name_input.value
        if name:
            with output:
                clear_output()
                print(f"Starting quiz for {name}")
                quiz = Quiz(name, question_bank)
                quiz.selected_topics = [widget.description for widget in topic_widgets if widget.value]
                quiz.run()
        else:
            with output:
                print("Please enter your name before starting the quiz.")

    def confirm_selection(b):
        selected_topics = [widget.description for widget in topic_widgets if widget.value]
        with output:
            clear_output()
            print(f"Selected topics: {', '.join(selected_topics)}")
        on_selection_confirmed(b)

    available_topics = question_bank.get_available_topics()
    topic_widgets = [widgets.Checkbox(value=False, description=topic) for topic in available_topics]
    select_all_button = widgets.Button(description="Select All")
    deselect_all_button = widgets.Button(description="Deselect All")
    confirm_button = widgets.Button(description="Confirm Selection")

    def select_all(b):
        for widget in topic_widgets:
            widget.value = True

    def deselect_all(b):
        for widget in topic_widgets:
            widget.value = False

    select_all_button.on_click(select_all)
    deselect_all_button.on_click(deselect_all)
    confirm_button.on_click(confirm_selection)
    start_quiz_button.on_click(start_quiz)

    name_input.layout.visibility = 'hidden'

    display(widgets.VBox([
        widgets.HBox([select_all_button, deselect_all_button, confirm_button]),
        widgets.VBox(topic_widgets),
        name_input,
        start_quiz_button,
        output
    ]))