from models import Redditer,Moderator
from autofixture import generators, register, AutoFixture
import random
import string

def generate_string():
	N = random.randint(3,30)
	return ''.join(random.choice(string.ascii_lowercase + string.digits + 2*'_') for _ in range(N))


class MyModelAutoFixture(AutoFixture):
    field_values = {
        'username': generators.CallableGenerator(generate_string),
    }

register(Redditer, MyModelAutoFixture)
register(Moderator,MyModelAutoFixture)