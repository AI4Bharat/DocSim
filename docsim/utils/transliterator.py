class Transliterator:
    def __init__(self, src_lang, dest_lang):
        if src_lang in IndicTransliterator.LANG2SCHEME and dest_lang in IndicTransliterator.LANG2SCHEME:
            self.transliterator = IndicTransliterator(src_lang, dest_lang)
        elif src_lang in EuropeanTransliterator.LANGS and dest_lang in EuropeanTransliterator.LANGS:
            self.transliterator = EuropeanTransliterator(src_lang, dest_lang)
        else:
            raise NotImplementedError
        
        self.transliterate = self.transliterator.transliterate
        self.reverse_transliterate = self.transliterator.reverse_transliterate


import transliterate as euro_transliterate
class EuropeanTransliterator:
    LANGS = set(euro_transliterate.get_available_language_codes() + ['en'])
    def __init__(self, src_lang, dest_lang):
        self.src_lang = src_lang
        self.dest_lang = dest_lang
        
    def transliterate(self, phrase):
        en_phrase = phrase if self.src_lang == 'en' else euro_transliterate.translit(phrase, self.src_lang, reversed=True)
        return euro_transliterate.translit(en_phrase, self.dest_lang)
        
    def reverse_transliterate(self, phrase):
        en_phrase = phrase if self.dest_lang == 'en' else euro_transliterate.translit(phrase, self.dest_lang, reversed=True)
        return euro_transliterate.translit(en_phrase, self.src_lang)


from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate as indic_transliterate
class IndicTransliterator:
    LANG2SCHEME = {
        'en': sanscript.HK, # sanscript.ITRANS
        'ta': sanscript.TAMIL,
        'te': sanscript.TELUGU,
        'ml': sanscript.MALAYALAM,
        'kn': sanscript.KANNADA,
        'or': sanscript.ORIYA,
        'bn': sanscript.BENGALI,
        'as': sanscript.BENGALI, # Assamese uses bn script
        'gu': sanscript.GUJARATI,
        'pa': sanscript.GURMUKHI, # Punjabi / Panjabi
        'hi': sanscript.DEVANAGARI, # Hindi
        'mr': sanscript.DEVANAGARI, # Marathi
        'ne': sanscript.DEVANAGARI, # Nepali
        'new': sanscript.DEVANAGARI, # Newari - NepalBhasa
        'raj': sanscript.DEVANAGARI, # Rajasthani
        # Minorities
        'ks': sanscript.DEVANAGARI, # Current Kashmiri is moving towards Urdu script
        'gom': sanscript.DEVANAGARI, # Konkani (Goan)
        'mai': sanscript.DEVANAGARI, # Maithili
        'sat': sanscript.DEVANAGARI, # Santali
        'gon': sanscript.GUNJALA_GONDI,
    }
    
    def __init__(self, src_lang, dest_lang):
        self.src_lang = src_lang
        self.dest_lang = dest_lang
        
        self.src_script = IndicTransliterator.LANG2SCHEME[src_lang]
        self.dest_script = IndicTransliterator.LANG2SCHEME[dest_lang]
    
    def transliterate(self, phrase):
        return indic_transliterate(phrase, self.src_script, self.dest_script)
    
    def reverse_transliterate(self, phrase):
        return indic_transliterate(phrase, self.dest_script, self.src_script)
