#!/usr/bin/env python
"""This script retrieves a user-defined number of questions
the user have to answer. A result is written to disk."""

import json
import html
import random
import sys
import http.server
import socketserver
import requests

class ResultRequestHandler(http.server.SimpleHTTPRequestHandler):
    """The request handler for our webserver, to visualize the results."""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        content = open('./results.html', 'r').read()
        content = content.replace("%questions_right%", str(quests_right))
        content = content.replace("%questions_wrong%", str(quests_wrong))
        self.wfile.write(bytes(content, "utf8"))

def get_user_input_int(minval: int, maxval: int, input_quest: str):
    """Get user input and verify, if it's really an integer and if the input
    is within a defined range."""

    tries = 0
    while True:

        tries+=1
        try:
            input_user = int(input(input_quest))
            if input_user > maxval or input_user < minval:
                raise ValueError
        except ValueError:
            if tries < MAX_TRIES:
                print("Sorry, I can't parse your answer. "
                      "Please try again and insert a number between %i and %i." % (minval, maxval))
            else:
                print("I'm sorry, but it will probably not get better if you try again.")
                sys.exit()
        else:
            break

    return input_user

MAX_TRIES = 5 # Number of attempts a user has to make a valid input.
MAX_QUESTS = 15 # Max number of questions a user can retrieve during a run.

# pylint: disable-msg=C0103
quests_right = 0 # Number of questions the user answered correctly.
quests_wrong = 0 # Number of questions the user answered wrong.
# pylint: enable-msg=C0103

# ask the user, how many questions he/she wants to answer
print("Welcome to our QUIZ! Let's start with the first question.\n")
num_quests = get_user_input_int(1, MAX_QUESTS, "How many questions do you want to get: ")

# get the questions
req_config = {'amount': num_quests, 'category': '9', 'difficulty': 'easy'}
req_questions = requests.get("https://opentdb.com/api.php", params=req_config)
questions = json.loads(req_questions.text)

# print the questions and let the user answer it
for question in questions["results"]:

    print("\n---\n")

    if question["type"] == "multiple":
        possible_answers = [question["correct_answer"]] + question["incorrect_answers"]
        random.shuffle(possible_answers)
        printed_answers = possible_answers
    else:
        possible_answers = ["True", "False"]
        printed_answers = ["Yes", "No"]

    print(html.unescape(question["question"]))

    # pylint: disable-msg=W0631
    for idx, answer in enumerate(printed_answers):
        print("%i) %s" % (idx+1, html.unescape(answer)))

    user_answer = get_user_input_int(1, idx+1, "Please type the number of the correct answer: ")

    if possible_answers[user_answer-1] == question["correct_answer"]:
        print("Congratulations, your answer %s is "
              "\033[1;32;49mright\033[0m!" % (printed_answers[user_answer-1]))
        quests_right += 1
    else:
        print("Sorry, but your answer %s is "
              "\033[1;31;49mwrong\033[0m!" % (printed_answers[user_answer-1]))
        quests_wrong += 1

# create the analysis
quests_right_perc = quests_right / num_quests * 100
print("\n---\n")
print("You answered %i of your %i (%i %%) questions correctly! "
      "Thank you for playing!" % (quests_right, num_quests, quests_right_perc))

# start a webserver, to visualize the results
try:
    MyResults = ResultRequestHandler
    serve_results = socketserver.TCPServer(("127.0.0.1", 8000), MyResults)

    print("You can view your results here: http://localhost:8000 .")
    print("If you are done, you can close the app by pressing CTRL+C .")

    serve_results.serve_forever()
except KeyboardInterrupt:
    print("CTRL+C received, shutting down the web server.")
    serve_results.socket.close()
