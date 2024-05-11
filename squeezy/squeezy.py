import collections
import itertools

ALL_WORDS = set(w.strip() for w in open("../TWL06.txt").readlines())

print(f'loaded {len(ALL_WORDS)} words.')
# print(WORDS[:10])
print()


def find_combinations(input, tiles, max_tiles_used=1):
  # print(input, tiles, max_tiles_used)
  result = collections.defaultdict(set)
  for word in input:
    # print(word)
    for tiles_used in range(1, max_tiles_used + 1):
      for c in itertools.combinations(tiles, tiles_used):
        # print('\tc:', c)
        for p in set(itertools.permutations(c + ('',) * (len(word) + 1 - tiles_used))):
          # print('\t\tp:', p)
          maybe_word = ''.join(itertools.chain(*zip(list(word) + [''], p)))
          # print('\t\t\tw:', maybe_word)
          if maybe_word in ALL_WORDS:
            used_tiles = tuple([t for t in p if t])
            pretty_word = ''.join(itertools.chain(*zip(list(word) + [''], [f'({t})' if t else '' for t in p])))
            print(f'{word} + {c} = {pretty_word}')
            result[word].add((used_tiles, pretty_word))
  return result


def print_possible(possible):
  # print(possible)
  for input_word, possibilities in possible.items():
    print(input_word)
    for tiles, result_word in possibilities:
      print(f'\t+ {tiles} -> {result_word}')
  print()


def squeezy(input, tiles_available, multitile=False):
  input = input.split(',')
  tiles_available = tiles_available.split(',')
  backsolve(tiles_available)
  max_tiles_used = 1
  if multitile:
    max_tiles_used = len(tiles_available) - len(input)
  print('all possible substitutions:')
  possible = find_combinations(
      input, tiles_available, max_tiles_used)
  print()
  tile_counts = collections.Counter(tiles_available)
  while possible:
    # print_possible(possible)
    most_constrained = min(
        possible.items(), key=lambda kv: (len(kv[1]), len(kv[0])))
    # print(most_constrained)
    input_word, options = most_constrained
    if len(options) > 1:
      print("human can solve this from here?")
      print_possible(possible)
      return
    tiles_used, result = list(options)[0]
    print(f'fully constrained: {input_word} + {tiles_used} -> {result}')
    for tile in tiles_used:
      tile_counts[tile] -= 1
    del possible[input_word]
    for input_word, options in possible.items():
      invalidated = set()
      for option in options:
        for tile in tiles_used:
          if tile_counts[tile] <= 0 and tile in option[0]:
            invalidated.add(option)
            # print("no longer possible:", input_word, tile, option)
      possible[input_word] = [o for o in options if o not in invalidated]


def backsolve(tiles):
  for p in itertools.permutations(tiles, len(tiles) - 1):
    # print(p)
    if ''.join(p) in ALL_WORDS:
      print('backsolved:', ','.join(p))

squeezy('METIER,FILLY,PEAL,SEER,MISSING,GANDER',
        'A,U,H,N,R,R,T')
squeezy('BANS,INSETS,MOSSES,DEFIES,INDIES,RATED,SPLIT',
        'EL,OT,C,LA,N,R,RO,SI')
squeezy('FED,SIRES,PURSE,MALE,FRETS',
        'AT,E,ER,CHA,M,N,NT,THE,TI', multitile=True)
