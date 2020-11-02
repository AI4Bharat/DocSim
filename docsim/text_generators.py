import random
class TextGeneratorBase:
    def generate(self):
        return 'ERROR'

from rstr import xeger
class TextFromRegexGenerator(TextGeneratorBase):
    def __init__(self, regex):
        self.pattern = regex
    
    def generate(self):
        return xeger(self.pattern)

class TextFromArrayGenerator(TextGeneratorBase):
    def __init__(self, array):
        self.options = array
    
    def generate(self):
        return random.choice(self.options)

from docsim.utils.lang import EnglishCharacters, LanguageCharacters
class NameGenerator(TextGeneratorBase):
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
        if random.random() < 0.25:
            # Two initials
            initial += ' ' + random.choice(self.charset.consonants) + '.'
            if random.random() < 0.4:
                # Three initials
                initial += ' ' + random.choice(self.charset.consonants) + '.'
        
        middle_name = self.random_name(4, 7)
        last_name = self.random_name(6, 8)
        
        # Either add middle name or initial
        if random.random() > 0.5:
            if random.random() > 0.5:
                # Add initial in middle
                name = first_name + ' ' + initial
            else:
                # Add initial at the beginning
                name = initial + ' ' + first_name
            
        else:
            name = first_name + ' ' + middle_name
        
        # Add last name for majority
        if random.random() > 0.15:
            name += ' ' + last_name
        
        return name.title() if self.title_case else name

class MultilineFullNameGenerator(FullNameGenerator):
    
    def generate(self):
        full_name = self.random_fullname()
        if random.random() > 0.3:
            return full_name
        else:
            return full_name + '\n' + self.random_name(6, 8)

class ReferentialTextGenerator(TextGeneratorBase):
    def __init__(self, src_component):
        self.src_component = src_component # Reference to the component from which we have to xlit
        
    def generate(self):
        return self.src_component['last_generated']

from docsim.utils.transliterator import Transliterator
class ReferentialTextTransliterator(ReferentialTextGenerator):
    def __init__(self, src_lang, dest_lang, src_component):
        super().__init__(src_component)
        self.transliterator = Transliterator(src_lang, dest_lang)
        
    def generate(self):
        return self.transliterator.transliterate(super().generate())

class TextPostProcessor():
    def __init__(self, upper_case=False, lower_case=False,
                 multiline=True):
        self.upper_case = upper_case
        self.lower_case = lower_case
        self.multiline = multiline
        
    def process(self, text):
        if self.upper_case:
            text = text.upper()
        elif self.lower_case:
            text = text.lower()
        
        if not self.multiline:
            text = text.split('\n')[0]
        return text

from faker import Faker
class AddressGenerator():
    LANG2CODE = {
        'en' : 'en-US',
        'hi': 'hi_IN'
    }
    def __init__(self, language='en', type="full"):
        lang_code = AddressGenerator.LANG2CODE[language]
        self.faker = Faker(lang_code)
        self.type = type
    def generate(self):
        if self.type == "full":
            return self.faker.address()
        if self.type == "street_address":
            return self.faker.street_address()
        elif self.type == "city":
            return self.faker.city()
        elif self.type == "country":
            return self.faker.country()
        elif self.type == "postcode":
            return self.faker.postcode()
        else:
            raise NotImplementedError
            
