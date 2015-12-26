from collections import Counter
import random

def playable_words(hand, words):
  hand_count = Counter(hand)
  for word in words:
    word_count = Counter(word)
    diff_count = word_count - hand_count
    wilds_needed = sum(diff_count.values())
    if wilds_needed <= hand_count[' ']:
      yield len(word) - wilds_needed, word

if __name__ == '__main__':

  print 'loading words...',
  words = set(line.upper().strip() for line in open('TWL06.txt'))
  print 'done.'

  deck = "RSTLN     "
  hand = random.sample(deck, 5)
  print 'hand:', hand
  for word in sorted(playable_words(hand, words))[-10:]:
    print '\t', word
