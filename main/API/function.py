import random

def generate_code():
    characters = 'abcdefghijklmnopqrstuvwxyz1234567890'
    code = ''

    for num in range(6):
        index = random.randint(0, (len(characters) - 1))
        code += characters[index]
    return code
