'''
    Core Application Loaders
    core/utils/loaders.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from math import gcd

import pathlib


def load_project_path():
    return str(pathlib.Path().absolute()).replace('\\', '/') + '/'


def load_key(key=str(), decrypt=False):
    ''' Load key from file '''
    path = '_keys/KEY_{}.txt'.format(key.upper())
    data = [i.replace('\n', '') for i in open(path)]

    if decrypt:
        data = [[int(j) for j in i.split()] for i in data]

        for i in range(len(data)):
            data[i] = decrypt_key(data[i][0], data[i][1], data[i][2], data[i][3:])

    if len(data) == 0:
        return str()
    elif len(data) == 1:
        return data[0]
    return data


def decrypt_key(p, d, c1, c2):
    ''' Decrypt key '''
    message = str()

    for i in range(len(c2)):
        message += chr(((c2[i] % p) * modulo_inverse(c1 ** d, p)) % p)

    return message


def modulo_inverse(a, b):
    ''' Inverse modulo '''
    if gcd(a, b) != 1:
        return None

    i = 1

    while (i * a) % b != 1:
        i += 1

    return i
