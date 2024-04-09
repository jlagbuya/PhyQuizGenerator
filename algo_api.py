from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import mysql.connector
import json

app = Flask(__name__)
CORS(app)

# Function to connect to the MySQL database and fetch questions
def fetch_questions_from_mysql(table_name, term_value):
    # Connect to MySQL database
    connection = mysql.connector.connect(
        host="153.92.15.7",
        user="u464153715_Wandat",
        password="1dotThesis",
        database="u464153715_RevQuestions"
    )

    # Query to fetch all rows from the specified table
    query = f"SELECT * FROM {table_name} WHERE TERM='{term_value}';"

    cursor = connection.cursor()
    cursor.execute(query)

    # Fetch all rows
    rows = cursor.fetchall()

    # Extract questions from the second column of each row
    questions = [row[1] for row in rows]
    
    choices = {}
    for i, options in enumerate(rows, start=1):
        choice_item = []
        for choice in range(2, 7):
            choice_item.append(options[choice])
            choices[i] = choice_item

    answers = {}
    for i, row in enumerate(rows, start=1):
        answers[i] = row[7]

    cursor.close()
    connection.close()

    return questions, choices, answers

def update_student_score(sid, target, score):
    connection = mysql.connector.connect(
        host="153.92.15.7",
        user="u464153715_login",
        password="Wandat1!",
        database="u464153715_login"
    )

    cursor = connection.cursor()

    query = f"UPDATE students SET {target} = {score} WHERE sid = {sid};"

    cursor.execute(query)

    connection.commit()

    cursor.close()
    connection.close()
    

def main(subject,score, term):
    
    # CONSTANTS
    WEAKNESS = 100 - score

    NOT_SATISFACTORY = WEAKNESS >= 31
    SATISFACTORY = WEAKNESS in range(20,31)
    VERY_SATISFACTORY = WEAKNESS in range(0,20)

    PRELIMS = (term == "prelims")
    MIDTERM = (term == "midterm")
    FINALS = (term == "finals")

    # Store term value
    if PRELIMS:
        term_value = 1
    elif MIDTERM:
        term_value = 2
    elif FINALS:
        term_value = 3
    else:
        print("Invalid term!")
        return
    

    # 12 Questions Easy
    if NOT_SATISFACTORY:
        # Your code for NOT_SATISFACTORY condition
        fetched = fetch_questions_from_mysql(f"avephysics{subject}", term_value)
        questions = fetched[0]
        choices = fetched[1]
        answers = fetched[2]
        
    # 4 Questions Easy, 4 Questions Average
    elif SATISFACTORY:
        # Fetch from Easy
        easy_fetched = fetch_questions_from_mysql(f"easyphysics{subject}", term_value)
        questions = easy_fetched[0][:4]
        choices_easy = easy_fetched[1]
        answers_easy = easy_fetched[2]

        # Fetch from Average
        avg_fetch = fetch_questions_from_mysql(f"avephysics{subject}", term_value)
        questions = questions + avg_fetch[0][:4]
        choices_easy_avg = list(choices_easy.values())[:4] + list(avg_fetch[1].values())[:4]
        answers_easy_avg = list(answers_easy.values())[:4] + list(avg_fetch[2].values())[:4]

        choices = {}
        answers = {}
        for i in range(len(choices_easy_avg)):
            choices[i+1] = choices_easy_avg[i]
            answers[i+1] = answers_easy_avg[i]
 
    # 2 Questions Easy, 1 Question Average, 2 Questions Difficult
    elif VERY_SATISFACTORY:
         # Fetch from Easy
        fetched = fetch_questions_from_mysql(f"easyphysics{subject}", term_value)
        questions = fetched[0][:2]
        choices_easy = fetched[1]
        answers_easy = fetched[2]

        # Fetch from Average
        avg_fetch = fetch_questions_from_mysql(f"avephysics{subject}", term_value)
        questions = questions + avg_fetch[0][:1]
        choices_easy_avg = list(choices_easy.values())[:2] + list(avg_fetch[1].values())[:1]
        answers_easy_avg = list(answers_easy.values())[:2] + list(avg_fetch[2].values())[:1]

        # Fetch from Difficult
        diff_fetch = fetch_questions_from_mysql(f"diffphysics{subject}", term_value)
        questions = questions + diff_fetch[0][:2]
        choices_easy_avg_diff = choices_easy_avg + list(diff_fetch[1].values())[:2]
        answers_easy_avg_diff = answers_easy_avg + list(diff_fetch[2].values())[:2]

        choices = {}
        answers = {}
        for i in range(len(choices_easy_avg_diff)):
            choices[i+1] = choices_easy_avg_diff[i]
            answers[i+1] = answers_easy_avg_diff[i]


    # Print the number of questions fetched based on weakness
    # print(f"Total questions fetched based on weakness: {len(questions)}")

    # print("Term value:", term_value)

    # Create a dictionary to store questions
    quiz = {}
    for i, question in enumerate(questions, start=1):
        quiz_item = {}
        quiz_item["question"] = question
        quiz_item["choices"] = choices[i]
        quiz_item["answer"] = answers[i]
        quiz[f"{i}"] = quiz_item

    quiz["num_items"] = len(questions)


    # Convert the dictionary to a JSON string
    question_json = json.dumps(quiz)
    
    # Print each item in the JSON for checking
    # for key, value in quiz.items():
    #     if key == "num_items":
    #         print(f"{key}: {value}")

    #     else:
    #         print(f"{key}:")
    #         print(f"Q: {value["question"]}")

    #         for choice in value["choices"]:
    #             print(f"{choice}")

    #         print()
    #         print(f"A: {value["answer"]}")
    #         print()

    # print("Questions (JSON format):")
    # print(question_json)
            
    return quiz
            
@app.route('/pseudo_algo_site')
def serve_html():
    return send_file('pseudo_algo_site.html')

@app.route('/quiz', methods=['POST'])
def get_quiz():
    data = request.json
    subject = int(data.get('subject'))
    score = int(data.get('score'))
    term = data.get('term')

    # Your main logic here
    # Call your main function passing subject, score, and term
    # Return JSON response containing quiz data
    # Example: return jsonify({"quiz": quiz_data})
    res = main(subject, score, term)
    print(res)
    return res

@app.route('/update_score', methods=['POST'])
def update_score():
    data = request.json
    sid = int(data.get('sid'))
    subject = data.get('target')
    score = int(data.get('score'))

    update_student_score(sid, subject, score)
    print(sid, subject, score)
    return "okay"

if __name__ == '__main__':
    app.run(debug=True)
