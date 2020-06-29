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

from docsim.utils.lang import EnglishCharacters, LanguageCharacters
class FullNameGenerator(TextGenerator):
    def __init__(self, lang='en'):
        
        if lang == 'en':
            self.charset = EnglishCharacters()
            self.title_case = True
        else:
            self.charset = LanguageCharacters(lang)
            self.title_case = False
    
    def generate(self):
        return self.random_fullname()
    
    def random_fullname(self):
        first_name = self.random_name(5, 7)
        initial = random.choice(self.charset.consonants) + '.'
        last_name = self.random_name(6, 8)
        name = first_name
        if random.random() > 0.5:
            name += ' ' + initial
        name += ' ' + last_name
        return name.title() if self.title_case else name

    def random_length_name(self, length=5):
        return ''.join(random.choice((self.charset.consonants, self.charset.vowels)[i%2]) for i in range(length))

    def random_name(self, min_length=5, max_length=5):
        length = random.randrange(min_length, max_length)
        return self.random_length_name(length)
