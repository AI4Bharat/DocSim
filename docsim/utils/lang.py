import unicodedata as ud
import random
import string

# ISO Language code to script name
LANG2SCRIPT = {
    'ta': 'tamil',
    'ml': 'malayalam'
}

MAX_RANGE = 1114112
ALLOWED_CATEGORIES = ['L', 'M', 'N', 'P']
def get_characters(script_name, only_prefix_match=False, skip_punctuations=False, skip_numbers=False, verbose=True):
    characters = {}
    script_name = script_name.upper()
    for i in range(MAX_RANGE):
        try:
            name = ud.name(chr(i))
        except ValueError:
            continue
        if only_prefix_match:
            if not name.startswith(script_name):
                continue
        elif script_name not in name:
            continue
        
        # Got a character of that script
        cat = ud.category(chr(i))
        if skip_numbers and cat[0] == 'N':
            continue
        if skip_punctuations and cat[0] == 'P':
            continue
        
        if cat[0] not in ALLOWED_CATEGORIES:
            if verbose:
                print('SKIPPED:', chr(i), name, cat)
        else:
            characters[chr(i)] = (name, cat)
        
    return characters

def get_vowels(characters):
    vowels = []
    for c, (name, category) in characters.items():
        if 'VOWEL' in name or 'VIRAMA' in name:
            vowels.append(c)
    return vowels

def get_consonants(characters):
    consonants = []
    for c, (name, category) in characters.items():
        if 'LETTER' in name:
            consonants.append(c)
    return consonants

class EnglishCharacters:
    def __init__(self, skip_punctuations=True, skip_numbers=True):
        self.lang_code = 'en'
        self.characters = string.ascii_uppercase
        if not skip_punctuations:
            self.characters += string.punctuation
        if not skip_numbers:
            self.characters += string.digits
        
        self.vowels = 'AEIOU'
        self.consonants = 'BCDFGHJKLMNPQRSTVWXYZ'

class LanguageCharacters:
    def __init__(self, lang_code, only_prefix_match=True, skip_punctuations=True, skip_numbers=True, 
                 verbose=False):
        
        if lang_code not in LANG2SCRIPT:
            exit('Lang code %s not found' % lang_code)
        
        self.lang_code = lang_code
        self.script = LANG2SCRIPT[lang_code]
        self.characters = get_characters(self.script, only_prefix_match, skip_punctuations, skip_numbers, verbose)
        self.vowels = get_vowels(self.characters)
        self.consonants = get_consonants(self.characters)
        self.import_letter_combinations()
        
        if verbose: self.print_details()
        
    def import_letter_combinations(self):
        if self.lang_code == 'ta':
            import tamil
            self.letter_combinations = tamil.utf8.tamil247
        
        return
    
    def print_details(self):
        print('LANGUAGE CODE:', self.lang_code)
        print('SCRIPT NAME:', self.script)
        print('CHARACTERS:'); print(self.characters)
        print('VOWELS:'); print(self.vowels)
        print('CONSONANTS:'); print(self.consonants)
        return
        

if __name__ == '__main__':
    c = LanguageCharacters('ta', only_prefix_match=True, skip_punctuations=True, skip_numbers=True, verbose=True)
