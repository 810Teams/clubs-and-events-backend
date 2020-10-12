from math import gcd


def load_key(path, many=False, decrypt=False):
    data = [i.replace('\n', '') for i in open(path)]

    if decrypt:
        data = [[int(j) for j in i.split()] for i in data]

        for i in range(len(data)):
            data[i] = decrypt_key(data[i][0], data[i][1], data[i][2], data[i][3:])

    if len(data) == 0:
        return str()
    if not many:
        return data[0]
    return data


def decrypt_key(p, d, c1, c2):
    message = str()

    for i in range(len(c2)):
        message += chr(((c2[i] % p) * modulo_inverse(c1 ** d, p)) % p)

    return message


def modulo_inverse(a, b):
    if gcd(a, b) != 1:
        return None

    i = 1

    while (i * a) % b != 1:
        i += 1

    return i
