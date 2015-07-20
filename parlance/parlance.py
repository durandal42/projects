import random
import sys
import itertools
import math
import collections

combined_word_freqs = collections.Counter()
for line in itertools.chain(itertools.islice(open('words.txt'), 1, None),
                            #itertools.islice(open('words2.txt'), 1, None),
                            ):
  rank, word, _, freq, _ = (word.strip() for word in line.strip().split('\t'))
  if not rank or not freq:
    # print line
    continue
  combined_word_freqs[word] += int(freq)

word_ranks = {}
word_freqs = {}
combined_words = sorted([(count, word) for word,count in combined_word_freqs.iteritems()],
                        reverse=True)
for rank, counted_word in enumerate(combined_words):
  count, word = counted_word
  # print rank, word, count
  word_ranks[word] = rank
  word_freqs[word] = count

BATCH_SIZE = 4

max_word_length = max(len(word) for word in word_ranks)
while True:
  words = random.sample(word_ranks.keys(), BATCH_SIZE)
  try:
    raw_input('\n\nWhich of the following words is more commonly used?\n%s\n' % words)
  except EOFError:
    break
  max_freq = max(word_freqs[word] for word in words)
  for rank, freq, word in sorted([(word_ranks[word], word_freqs[word], word) for word in words]):
    print '%s %s [%s] (#%d)' % (
      word,
      ' ' * (max_word_length - len(word)),
      '-' * int(20 * freq / max_freq),
      rank
      )
