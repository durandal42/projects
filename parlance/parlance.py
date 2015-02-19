import random
import sys
import itertools
import math

word_ranks = {}
word_freqs = {}
for line in itertools.chain(itertools.islice(open('words.txt'), 1, None),
                            #itertools.islice(open('words2.txt'), 1, None),
                            ):
  rank, word, _, freq, _ = (word.strip() for word in line.strip().split('\t'))
  if not rank or not freq:
    # print line
    continue
  word_ranks[word] = int(rank)
  word_freqs[word] = int(freq)

BATCH_SIZE = 4

max_word_length = max(len(word) for word in word_ranks)
while True:
  words = random.sample(word_ranks.keys(), BATCH_SIZE)
  print
  print
  print 'Which of the following words is more commonly used?'
  print words
  sys.stdin.readline()
  max_freq = max(word_freqs[word] for word in words)
  for rank, freq, word in sorted([(word_ranks[word], word_freqs[word], word) for word in words]):
    print '%s %s [%s] (#%d)' % (
      word,
      ' ' * (max_word_length - len(word)),
      '-' * int(20 * freq / max_freq),
      rank
      )
