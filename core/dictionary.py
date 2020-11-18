'''
    Core Application Dictionary Cleaning Script
    core/dictionary.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from datetime import datetime
from pythainlp.util import collate

DICTIONARY = 'core/dictionary/profanity_th.txt'
ENCODING = 'utf-8'


def clean():
    ''' Clean dictionary '''
    word_list = [i.replace('\n', str()).replace('\r', str()) for i in open(DICTIONARY, 'r', encoding=ENCODING)]

    dictionary = open('{}-{}.txt'.format(DICTIONARY.replace('.txt', str()), get_datetime_now()), 'w', encoding=ENCODING)
    dictionary.write('\n'.join(word_list))
    dictionary.close()

    print('[Log] Successfully backed up dictionary file.')

    dictionary = open(DICTIONARY, 'w', encoding=ENCODING)
    dictionary.write('\n'.join(collate(list(dict.fromkeys(word_list)))))
    dictionary.close()

    print('[Log] Successfully cleaned and created a new dictionary file.')


def get_datetime_now():
    ''' Get current date and time in normalized format for file saving '''
    return str(datetime.now()).split('.')[0].replace('-', str()).replace(':', str()).replace(' ', '-')


clean()
