from models import Subreddit
from autofixture import generators, register, AutoFixture
import random
import string

def generate_string():
	N = random.randint(3,20)
	return ''.join(random.choice(string.ascii_letters) for _ in range(N))


class MyModelAutoFixture(AutoFixture):
    field_values = {
        'title': generators.CallableGenerator(generate_string),
    }

register(Subreddit, MyModelAutoFixture)