import sys

from collections import Counter
from collections import defaultdict
from itertools import islice

def parse_available(string):
  result = defaultdict(list)
  for letter, duration in zip(string[::2], string[1::2]):
    duration = int(duration)
    if duration == 0: duration = 10
    result[letter].append(duration)
  for letter, durations in result.iteritems():
    durations.sort()
  return result

def legal_plays(available, words):
  available_tiles = Counter(dict((letter, len(durations)) for letter, durations in available.iteritems()))
  num_available = sum(available_tiles.values()) 
  print available_tiles
  for word in words:
    if len(word) > num_available: continue
    if available_tiles | Counter(word) == available_tiles:
      yield word

def score_play(available, play):
  play = Counter(play)
  result = 0
  for letter, durations in available.iteritems():
    for unused_tile_duration in durations[play[letter]:]:
      result -= 10 ** (10 - unused_tile_duration)
  return result

def best_plays(available, words):
  return sorted((score_play(available, play), play) for play in legal_plays(available, words))

def main(words):
  while True:
    print '$ ',
    input = sys.stdin.readline()
    if not input:
      return
    available_string = input.strip().lower()
    available = parse_available(available_string)
    for result in best_plays(available, words):
      print result

if __name__ == '__main__':
  words = set(line.lower().strip() for line in open('TWL06.txt'))
  main(words)
