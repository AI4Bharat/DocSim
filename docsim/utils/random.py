from uuid import uuid4
import random
import string

def random_id():
    return uuid4().hex

def get_rand_string(min_l=10, max_l=20):
    length = random.randint(min_l, max_l)
    return ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
                   for i in range(length))
