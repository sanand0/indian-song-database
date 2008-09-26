import re

def trans(word, lang='tamil'):
    return mapTamil(word)

def mapTamil(word):
    word = re.sub(r'%20', ' ', word)
    word = re.sub(r'%2520', ' ', word)

    word = word.upper()
    word = re.sub(r'[^A-Z0-9]+', ' ', word)

    # Vowel and semi-vowel mapping
    word = re.sub(r'AIY', 'AY', word)
    word = re.sub(r'AE|EA|EI|EY\b', 'E', word)
    word = re.sub(r'IE', 'I', word)
    word = re.sub(r'IU', 'IYU', word)
    word = re.sub(r'OYI|OI|OY|OVI', 'OI', word)

    word = re.sub(r'([AEIOU])H([AEIOU])', r'\1G\2', word)

    word = re.sub(r'AA', 'A', word)
    word = re.sub(r'EE', 'I', word)
    word = re.sub(r'OO', 'U', word)

    # Consonant mapping
    word = re.sub(r'TCH|KSH', 'SH', word)
    word = re.sub(r'CH', 'S', word)
    word = re.sub(r'N[DT]R', 'NR', word)
    word = re.sub(r'ZH?', 'L', word)

    # Not sure about this one...
    word = re.sub(r'H', '', word)

    word = re.sub(r'W', 'V', word)

    word = re.sub(r'G', 'K', word)
    word = re.sub(r'J', 'C', word)
    word = re.sub(r'D', 'T', word)
    word = re.sub(r'B', 'P', word)

    # Generic rules
    word = re.sub(r'TIR', 'TR', word)

    word = re.sub(r'\s', '', word)

    word = re.sub(r'(\w)\1', r'\1', word)
    word = re.sub(r'(\w)\1', r'\1', word)
    word = re.sub(r'(\w)\1', r'\1', word)
    word = re.sub(r'(\w)\1', r'\1', word)

    return word
