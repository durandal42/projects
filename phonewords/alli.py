lexicon = set(line.strip() for line in open('/usr/share/dict/words'))
phone_letters = {'2':['a', 'b', 'c'],
                 '3':['d', 'e', 'f'],
                 '4':['g', 'h', 'i'],
                 '5':['j', 'k', 'l'],
                 '6':['m', 'n', 'o'],
                 '7':['p', 'q', 'r', 's'],
                 '8':['t', 'u', 'v'],
                 '9':['w', 'x', 'y', 'z']}
 
def is_word(word):
    return word in lexicon
 
def find_real_words(number):
    for word in find_strings(number):
        if is_word(word):
            yield word
 
def find_strings(number, i=0):
    end = len(number)-1
    if i > end:
        yield ''
    if i <= end:
        digit = number[i]
        for string in find_strings(number, i+1):
            for l in phone_letters[digit]:
                yield l + string

for word in find_real_words('222'): print word
