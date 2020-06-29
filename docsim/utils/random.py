# Random from regex: https://stackoverflow.com/questions/4627464/generate-a-string-that-matches-a-regex-in-python

import random
from uuid import uuid4

ENG_ALPHABETS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def random_fullname(title_case=True):
    first_name = random_name(5, 7)
    initial = random.choice(ENG_ALPHABETS) + '.'
    last_name = random_name(6, 8)
    name = first_name
    if random.random() > 0.5:
        name += ' ' + initial
    name += ' ' + last_name
    return name.title() if title_case else name

CONSONANTS = "BCDFGHJKLMNPQRSTVWXYZ"
VOWELS = "AEIOU"

def random_length_name(length=5):
    return "".join(random.choice((CONSONANTS, VOWELS)[i%2]) for i in range(length))

def random_name(min_length=5, max_length=5):
    length = random.randrange(min_length, max_length)
    return random_length_name(length)

def random_id():
    return uuid4().hex
