#!/usr/bin/env python
"""This script retrieves a user-defined number of questions
the user have to answer. A result is written to disk."""

import json
import html
import random
import sys
import requests

#Number of tries a user has to insert a valid answer.
MAX_TRIES = 5
MAX_QUESTS = 15

print("Welcome to our QUIZ! Let's start with the first question.\n")

tries = 0
while True:

    tries+=1
    try:
        num_quests = int(input("How many questions do you want to get: "))
        if num_quests > MAX_QUESTS or num_quests < 1:
            raise ValueError
    except ValueError:
        if tries < MAX_TRIES:
            print("Sorry, I can't parse your answer."
                "Please try again and insert a number between 1 and %i." % (MAX_QUESTS))
        else:
            print("I'm sorry, but it will probably not get better if you try again. "
                "Let's quit the QUIZ.")
            sys.exit()
    else:
        break

req_config = {'amount': num_quests, 'category': '9', 'difficulty': 'hard'}
req_questions = requests.get("https://opentdb.com/api.php", params=req_config)
questions = json.loads(req_questions.text)

for question in questions["results"]:

    print("\n---\n")

    if question["type"] == "multiple":
        possible_answers = [question["correct_answer"]] + question["incorrect_answers"]
        random.shuffle(possible_answers)
    else:
        possible_answers = ["True", "False"]

    print(html.unescape(question["question"]))

    # pylint: disable-msg=W0631
    for idx, answer in enumerate(possible_answers):
        print("%i) %a" % (idx+1, html.unescape(answer)))

    # pylint: disable-msg=C0103
    tries = 0

    # pylint: enable-msg=C0103
    while True:

        tries+=1
        try:
            user_answer = int(input("Please type the number of the correct answer: "))
            if user_answer > idx+1 or user_answer < 1:
                raise ValueError
        except ValueError:
            if tries < MAX_TRIES:
                print("Sorry, I can't parse your answer."
                      "Please try again and insert a number between 1 and %i." % (idx+1))
            else:
                print("I'm sorry, but it will probably not get better if you try again. "
                      "Let's proceed with the next question (if any left).")
                break
        else:
            if possible_answers[user_answer-1] == question["correct_answer"]:
                print("Congratulations, your answer %a is "
                      "\033[1;32;49mright\033[0m!" % (possible_answers[user_answer-1]))
            else:
                print("Sorry, but your answer %a is "
                      "\033[1;31;49mwrong\033[0m!" % (possible_answers[user_answer-1]))
            break
