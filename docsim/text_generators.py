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
class NameGenerator(TextGenerator):
    def __init__(self, lang='en'):
        if lang == 'en':
            self.charset = EnglishCharacters()
            self.title_case = True
        else:
            self.charset = LanguageCharacters(lang)
            self.title_case = False
        
        if hasattr(self.charset, 'letter_combinations'):
            self.random_length_name = self.random_length_name_from_combinations
    
    def generate(self, min_len=5, max_len=5):
        return self.random_name(min_len, max_len)
    
    def random_length_name_from_combinations(self, length=5):
        return ''.join(random.choice(self.charset.letter_combinations) for i in range(length))
    
    def random_length_name(self, length=5):
        return ''.join(random.choice((self.charset.consonants, self.charset.vowels)[i%2]) for i in range(length))

    def random_name(self, min_length=5, max_length=5):
        length = random.randrange(min_length, max_length)
        return self.random_length_name(length)
            
class FullNameGenerator(NameGenerator):
    def __init__(self, lang='en'):
        super().__init__(lang)
    
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

from docsim.utils.transliterator import Transliterator
class ReferntialTextTransliterator(TextGenerator):
    def __init__(self, src_lang, dest_lang, src_component):
        self.transliterator = Transliterator(src_lang, dest_lang)
        self.src_component = src_component # Reference to the component from which we have to xlit
        
    def generate(self):
        return self.transliterator.transliterate(self.src_component['last_generated'])
