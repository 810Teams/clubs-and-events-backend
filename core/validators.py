'''
    Core Application Validators
    core/validators.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from profanity_filter import ProfanityFilter
from pythainlp.tokenize import word_tokenize
from textblob import TextBlob
from textblob.exceptions import TranslatorError

from clubs_and_events.settings import NLP_EN_MODEL

import spacy


def get_lang(text):
    ''' Get detected language from the text '''
    try:
        return TextBlob(text).detect_language()
    except TranslatorError:
        return None


def tokenize(text, engine='newmm', keep_whitespace=False):
    ''' Tokenize words from a sentence in the Thai language '''
    return word_tokenize(text, engine=engine, keep_whitespace=keep_whitespace)


def validate_profanity(text):
    ''' Validates profanity of the text '''
    if is_profane_en(text):
        raise ValidationError(_('Text contains profanity in English.'), code='profanity_detected')
    elif is_profane_th(text):
        raise ValidationError(_('Text contains profanity in Thai.'), code='profanity_detected')
    return True


def is_profane_en(text):
    ''' Check if the English text contains profanity '''
    nlp = spacy.load(NLP_EN_MODEL)
    profanity_filter = ProfanityFilter(nlps={'en': nlp})
    nlp.add_pipe(profanity_filter.spacy_component, last=True)

    return nlp(text)._.is_profane


def is_profane_th(text):
    ''' Check if the Thai text contains profanity '''
    words = tokenize(text)
    dictionary = open('core/dictionary/profanity_th.txt', encoding='utf-8')
    dictionary = [i.replace('\n', '').replace('\r', '').strip() for i in dictionary if i[0] != '#']

    for i in words:
        if i in dictionary:
            return True

    return False
