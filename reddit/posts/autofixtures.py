from models import TextPost,LinkPost
from autofixture import generators, register, AutoFixture
import random
import string

def generate_string():
	N = random.randint(3,199)
	first_char = random.choice(string.ascii_uppercase)
	return (first_char + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(N)))


class MyModelAutoFixture(AutoFixture):
    field_values = {
        'title': generators.CallableGenerator(generate_string),
    }

register(TextPost, MyModelAutoFixture)
register(LinkPost,MyModelAutoFixture)