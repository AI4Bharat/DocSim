import random
class TextGenerator:
    def generate(self):
        return 'ERROR'

from rstr import xeger
class TextFromRegexGenerator(TextGenerator):
    def __init__(self, regex):
        self.pattern = regex
    
    def generate(self):
        return xeger(self.pattern)

class TextFromArrayGenerator(TextGenerator):
    def __init__(self, array):
        self.options = array
    
    def generate(self):
        return random.choice(self.options)

from docsim.utils.random import random_fullname
class FullNameGenerator(TextGenerator):
    def __init__(self, lang='en'):
        if lang == 'en':
            self.generate = random_fullname
        else:
            raise NotImplementedError

