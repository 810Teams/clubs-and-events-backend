'''
    Core Application Natural Language Processing (NLP) Utility Functions
    core/utils/nlp.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from profanity_filter import ProfanityFilter
from pythainlp.corpus.common import thai_words
from pythainlp.tokenize import word_tokenize
from pythainlp.util import dict_trie
from textblob import TextBlob
from textblob.exceptions import TranslatorError

from clubs_and_events.settings import NLP_EN_MODEL

import spacy


def validate_profanity(text, lang=('en', 'th')):
    ''' Validates profanity of the text '''
    if 'en' in lang and is_profane_en(text):
        raise ValidationError(_('Text contains profanity in English.'), code='profanity_detected')
    elif 'th' in lang and is_profane_th(text):
        raise ValidationError(_('Text contains profanity in Thai.'), code='profanity_detected')
    return True


def is_profane_en(text):
    ''' Check if the English text contains profanity '''
    nlp = spacy.load(NLP_EN_MODEL)
    profanity_filter = ProfanityFilter(nlps={'en': nlp})
    nlp.add_pipe(profanity_filter.spacy_component, last=True)

    if isinstance(text, str):
        return nlp(text)._.is_profane
    return False


def is_profane_th(text):
    ''' Check if the Thai text contains profanity '''
    # Dictionary set-up
    custom_dictionary = set(thai_words())
    profane_dictionary = open('core/dictionary/profanity_th.txt', encoding='utf-8')
    profane_dictionary = [i.replace('\n', '').replace('\r', '').strip() for i in profane_dictionary]

    for i in profane_dictionary:
        custom_dictionary.add(i)

    # Data preparation
    text = text.replace(' ', str()).replace('เเ', 'แ').replace('ํา', 'ำ')

    # Tokenize
    words = word_tokenize(
        text,
        engine='newmm',
        keep_whitespace=False,
        custom_dict=dict_trie(dict_source=custom_dictionary)
    )

    # Text scan
    for i in words:
        if i in profane_dictionary:
            return True

    return False


def get_lang(text):
    ''' Get detected language from the text '''
    try:
        return TextBlob(text).detect_language()
    except TranslatorError:
        return None


def is_en(text):
    ''' Detect a language and returns True if is in English '''
    return not is_th(text)


def is_th(text):
    ''' Detect a language and returns True if is in the Thai language '''
    return get_lang(text) == 'th'
