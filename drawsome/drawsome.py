'''
Given a rack of tiles and a word length, print all known DRAW SOMETHING words that could match.
'''

from utils import count

import itertools
import sys

legal_words = set()
difficulty_counts = {1:0, 2:0, 3:0}
def load_words():
    print 'loading words...',
    for line in open('wordlist.csv'):
        tokens = line.split(',')
        word = tokens[0]
        difficulty = int(tokens[1])
        legal_words.add(word)
        difficulty_counts[difficulty] += 1
    print 'finished loading', len(legal_words), 'legal words.', difficulty_counts

def subset(needle, haystack):
    for k,v in needle.iteritems():
        if not k in haystack:
            return False
        if haystack[k] < needle[k]:
            return False
    return True

def possible_words(rack, num):
    rack_count = count(rack)
    result = []
    for word in legal_words:
        if len(word) != num: continue
        if subset(count(word), rack_count):
            result.append(word)
    result = sorted(result, cmp=lambda x,y: cmp(len(x), len(y)))
    return result

if __name__ == '__main__':
    load_words()
    for word in possible_words(sys.argv[1], int(sys.argv[2])):
        print word
