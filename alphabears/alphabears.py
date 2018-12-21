import sys

from collections import Counter
from collections import defaultdict
from itertools import islice

def parse_available(string):
  '''A1 B2 C2 D3 -> '1a2bc3d' '''
  result = defaultdict(list)
  duration = -1
  for c in string:
    if c.isdigit():
      duration = int(c)
      if duration == 0: duration = 10
    else:
      result[c].append(duration)
  for letter, durations in result.iteritems():
    durations.sort()
  return result

def legal_plays(available, words):
  available_tiles = Counter(dict((letter, len(durations))
                                 for letter, durations in available.iteritems()))
  num_available = sum(available_tiles.values()) 
  #print available_tiles
  for word in words:
    if len(word) > num_available: continue
    if available_tiles | Counter(word) == available_tiles:
      yield word

def score_play(available, play, letter_frequencies):
  play = Counter(play)
  result = 0
  for letter, durations in available.iteritems():
    for unused_tile_duration in durations[play[letter]:]:
      result -= 2.0 ** -unused_tile_duration  # imminently expiring: -2.0
      result -= 1000.0 / float(letter_frequencies[letter])
  return result

def best_plays(available, words, letter_frequencies):
  return sorted((score_play(available, play, letter_frequencies), play)
                for play in legal_plays(available, words))

def main(words):
  letter_frequencies = Counter(c for word in words for c in word)
  print 'letter_frequencies:', letter_frequencies
  print 'available letters format: 1abc2def3ghi'
  while True:
    print '$ ',
    input = sys.stdin.readline()
    if not input:
      return
    available_string = input.strip().lower()
    available = parse_available(available_string)
    print 'penalty\tword'
    for score,word in best_plays(available, words, letter_frequencies):
      print '%0.2f\t%s' % (-score, word)

if __name__ == '__main__':
  words = set(line.lower().strip() for line in open('TWL06.txt'))
  main(words)
