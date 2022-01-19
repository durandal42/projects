import random
import collections
import functools
import itertools
import re
import sys
import dataclasses

import guess_cache

WORD_LENGTH = 5
HARD_MODE = False

LEGAL_TARGETS = []
LEGAL_GUESSES = []


def load_words():
  global LEGAL_TARGETS
  global LEGAL_GUESSES
  print('loading words...')
  LEGAL_TARGETS = [word.strip().upper() for word in open('legal-targets.txt')]
  legal_guesses = [word.strip().upper() for word in open('legal-guesses.txt')]
  num_targets = len(LEGAL_TARGETS)
  num_guesses = len(legal_guesses)
  print(f'finished loading {num_targets} legal targets and {num_guesses} additional legal guesses.')
  LEGAL_GUESSES = sorted(LEGAL_TARGETS + legal_guesses)


# scoring constants:
NO_MATCH = 0
WRONG_SPOT = 1
RIGHT_SPOT = 2


@functools.cache
def auto_scorer(guess, target):
  score = [NO_MATCH] * WORD_LENGTH
  target_counts = collections.Counter(target)
  for i, g in enumerate(guess):
    if target[i] == g:
      score[i] = RIGHT_SPOT
      target_counts[g] -= 1
  for i, g, in enumerate(guess):
    if target[i] != g and target_counts[g] > 0:
      score[i] = WRONG_SPOT
      target_counts[g] -= 1
  return tuple(score)


def user_scorer(word, target):
  # we don't know what the target is, but we want the same interface as
  # auto_scorer.
  score = parse_score_string(input(f'score {word}, please: ').strip())
  # "delete" the previous line, so we can pretty-print over it.
  print("\033[A                             \033[A")
  return score

PRETTY_PRINT = {
    NO_MATCH: '⬛',
    WRONG_SPOT: '🟨',
    RIGHT_SPOT: '🟩',
}

PRETTY_PRINT_DARK_MODE = {
    NO_MATCH: '⬜',
    WRONG_SPOT: '🟨',
    RIGHT_SPOT: '🟩',
}

UGLY_PRINT = {
    NO_MATCH: 'B',
    WRONG_SPOT: 'Y',
    RIGHT_SPOT: 'G',
}

UGLY_PRINT_LOWER = {k: v.lower() for k, v in UGLY_PRINT.items()}

INTERNAL_PRINT = {
    NO_MATCH: NO_MATCH,
    WRONG_SPOT: WRONG_SPOT,
    RIGHT_SPOT: RIGHT_SPOT,
}

PRINT_METHODS = [
    PRETTY_PRINT,
    PRETTY_PRINT_DARK_MODE,
    UGLY_PRINT,
    UGLY_PRINT_LOWER,
    INTERNAL_PRINT,
]

PARSE_MAP = {}
for s, c in itertools.chain.from_iterable(p.items() for p in PRINT_METHODS):
  PARSE_MAP[c] = s


SLACK_EMOJIS = {
    ':black_large_square:': NO_MATCH,
    ':white_large_square:': NO_MATCH,
    ':large_yellow_square:': WRONG_SPOT,
    ':large_green_square:': RIGHT_SPOT,
}


def parse_score_string(score_string):
  for k, v in SLACK_EMOJIS.items():
    score_string = score_string.replace(k, UGLY_PRINT[v])
  return tuple(PARSE_MAP[c] for c in score_string)

assert(auto_scorer('SANDS', 'BRASS') == parse_score_string('yybbg'))
assert(auto_scorer('TURNS', 'BRASS') == parse_score_string('bbybg'))
assert(auto_scorer('SUPER', 'BRASS') == parse_score_string('ybbby'))
assert(auto_scorer('CARBS', 'BRASS') == parse_score_string('byyyg'))
assert(auto_scorer('BARBS', 'BRASS') == parse_score_string('gyybg'))


def pretty_print(score):
  return ''.join(PRETTY_PRINT[s] for s in score)

assert(pretty_print(parse_score_string('byg')) == '⬛🟨🟩')
assert(pretty_print(parse_score_string('⬛🟨🟩')) == '⬛🟨🟩')


def user_choice(prev_guesses=None, prev_scores=None):
  if prev_guesses:
    print()
    for guess, score in zip(prev_guesses, prev_scores):
      pretty_score = pretty_print(score)
      print(f'{guess}: {pretty_score}')
    wordle_keyboard(prev_guesses, prev_scores)
  remaining_targets = restrict_many(LEGAL_TARGETS, prev_guesses, prev_scores)
  print("Remaining targets:", len(remaining_targets))
  if len(remaining_targets) < 20:
    print(remaining_targets)
  response = input('next guess: ').strip().upper()
  if response == '?':
    return conservative_restricted_choice(prev_guesses, prev_scores)
  return response


def random_choice(prev_guesses=None, prev_scores=None, guess_domain=None):
  if guess_domain is None:
    guess_domain = LEGAL_TARGETS
  guess = random.choice(guess_domain)
  print(guess, '(randomly chosen)')
  return guess


def restrict_one(targets, prev_guess, prev_score):
  return [w for w in targets if auto_scorer(prev_guess, w) == prev_score]


def restrict_many(targets, prev_guesses, prev_scores):
  for guess, score in zip(prev_guesses, prev_scores):
    targets = restrict_one(targets, guess, score)
  return targets


def random_restricted_choice(prev_guesses, prev_scores):
  remaining_targets = restrict_many(LEGAL_TARGETS, prev_guesses, prev_scores)
  return random_choice(None, None, remaining_targets)


def conservative_restricted_choice(prev_guesses, prev_scores):
  remaining_targets = restrict_many(LEGAL_TARGETS, prev_guesses, prev_scores)
  remaining_targets_set = set(remaining_targets)
  cache = guess_cache.cache(HARD_MODE)
  if HARD_MODE:
    legal_guesses = restrict_many(LEGAL_GUESSES, prev_guesses, prev_scores)
  else:
    legal_guesses = LEGAL_GUESSES

  # print('%d possible targets remain' % len(remaining_targets))
  cache_key = ()
  for score, guess in zip(prev_scores, prev_guesses):
    if cache_key in cache and guess == cache[cache_key][0]:
      cache_key = cache_key + (score,)
    else:
      cache_key = None
      break
  if cache_key is not None and cache_key in cache:
    print('(precomputed) worst case for guess %s: %s (remaining targets, tiebreaker)' %
          cache[cache_key])
    return cache[cache_key][0]

  if len(remaining_targets) <= 2:
    print('remaining targets down to %s; guessing %s' %
          (remaining_targets, remaining_targets[0]))
    return remaining_targets[0]

  worst_case_by_guess = {}
  best_worst_case_so_far = len(remaining_targets)
  for guess in legal_guesses:
    score_counts = collections.defaultdict(int)
    for target in remaining_targets:
      score = auto_scorer(guess, target)
      score_counts[score] += 1
      #      if score_counts[score] > best_worst_case_so_far:
      #        break
    else:
      worst_score, worst_case = max(score_counts.items(), key=lambda x: x[1])
      if guess in remaining_targets_set:
        eligibility_tiebreaker = 0
      else:
        eligibility_tiebreaker = 1
      worst_case_by_guess[guess] = (worst_case, eligibility_tiebreaker)
      best_worst_case_so_far = min(best_worst_case_so_far, worst_case)

  best_guess, best_worst_case = min(
      worst_case_by_guess.items(), key=lambda x: x[1])
  n = 100
  print(f'Top {n} guesses:', sorted([(v, k) for k, v in worst_case_by_guess.items()])[:n])
  print(f'worst case for guess {best_guess}: {best_worst_case} remaining possibilities')

  if cache_key not in cache:
    # print('updating cache: %s:%s' % (cache_key, (best_guess, best_worst_case)))
    cache[cache_key] = (best_guess, best_worst_case)

  return best_guess


def wordle_target(i):
  return LEGAL_TARGETS[i]


def random_target():
  target = random.choice(LEGAL_TARGETS)
  #  print(f'spoiler: the target word is {target}')
  return target


def user_target():
  return input('choose a target: ').strip().upper()


def no_target():
  return None


def absurdle_score(guesses, scores):
  assert len(guesses) == len(scores) + 1
  targets = restrict_many(LEGAL_TARGETS, guesses[:-1], scores)
  buckets = collections.Counter()
  g = guesses[-1]
  for t in targets:
    score = auto_scorer(g, t)
    buckets[score] += 1
    if score == (RIGHT_SPOT,) * WORD_LENGTH:
      buckets[score] -= 1
  worst_bucket, score = max((v, k) for k, v in buckets.items())
  return score


def play(targeter=random_target, guesser=user_choice, scorer=auto_scorer, absurdle=False):
  target = targeter()

  guesses = []
  scores = []
  legal_guesses = LEGAL_GUESSES
  while not guesses or scores[-1] != (RIGHT_SPOT,) * WORD_LENGTH:
    guess = guesser(guesses, scores)
    if guess not in legal_guesses and not absurdle:
      print("Illegal guess. Try again.")
      continue
    guesses.append(guess)
    if absurdle:
      score = absurdle_score(guesses, scores)
    else:
      score = scorer(guess, target)
    scores.append(score)
    pretty_score = pretty_print(score)
    print(f'{guess}: {pretty_score}')
    if HARD_MODE:
      legal_guesses = restrict_one(legal_guesses, guess, score)

  print('\n')
  if target is None:
    target = guesses[-1]
  if absurdle:
    print(absurdle_snippet(scores))
  else:
    print(wordle_snippet(scores, LEGAL_TARGETS.index(target)))
  print()
  print('\t'.join(['guesses:'] + guesses))
  print('\n')

  return len(scores)


def wordle_snippet(scores, i='?'):
  num_guesses = len(scores)
  hard_mode_star = HARD_MODE and '*' or ''
  return f'Wordle {i} {num_guesses}/6{hard_mode_star}\n\n' + '\n'.join(pretty_print(s) for s in scores)


def absurdle_snippet(scores, i='?'):
  num_guesses = len(scores)
  return f'Absurdle {num_guesses}/∞\n\n' + '\n'.join(pretty_print(s) for s in scores)


@dataclasses.dataclass
class GameSummary:
  """Class for summarizing a single game of Wordle."""
  game_type: str = "Wordle"
  day: int = None
  guess_count: int = None
  scores: list[tuple] = dataclasses.field(default_factory=list)


def parse_snippet(snippet):
  header_regex = '(Wordle|Absurdle) (\\d+ )?(\\d+|X)/(6|∞)(\\*?)'
  result = GameSummary()
  for line in snippet.splitlines():
    if not line: continue
    m = re.match(header_regex, line)
    if m:
      result.game_type = m.group(1)
      result.day = int(m.group(2))
      if m.group(3) == 'X':
        result.guess_count = 'X'
      else:
        result.guess_count = int(m.group(3))
    else:
      result.scores.append(parse_score_string(line))
  return result

assert parse_snippet(wordle_snippet([(0, 1, 2), (2, 1, 0)], 5)).scores == [
    (0, 1, 2), (2, 1, 0)]


def wordle_keyboard(guesses, scores):
  UNKNOWN = 0
  ABSENT = 1
  PRESENT = 2
  LOCATED = 3
  alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  alphamap = collections.defaultdict(int)

  for guess, score in zip(guesses, scores):
    for g, s in zip(guess, score):
      if s == NO_MATCH:
        alphamap[g] = max(alphamap[g], ABSENT)
      if s == WRONG_SPOT:
        alphamap[g] = max(alphamap[g], PRESENT)
      if s == RIGHT_SPOT:
        alphamap[g] = max(alphamap[g], LOCATED)

  qwerty = ['QWERTYUIOP', 'ASDFGHJKL', 'ZXCVBNM']
  pretty_print = {
      UNKNOWN: '0;30;47',
      ABSENT: '1;37;40',
      PRESENT: '1;37;43',
      LOCATED: '1;37;42',
  }

  for i, line in enumerate(qwerty):
    print(' ' * i, end='')
    for c in line:
      color = pretty_print[alphamap[c]]
      print(f'\x1b[{color}m {c} \x1b[0m ', end='')
    print()


def human_guesser(): play(targeter=random_target, guesser=user_choice)


def ai_guesser(): play(targeter=no_target,
                       guesser=conservative_restricted_choice, scorer=user_scorer)


def test_mode(): play(targeter=user_target, guesser=conservative_restricted_choice)


def random_test_mode(): play(targeter=random_target,
                             guesser=conservative_restricted_choice)


def history_mode(i): play(targeter=lambda: wordle_target(i),
                          guesser=conservative_restricted_choice)


def solve_everything():
  solve_times = {}
  meta_score = collections.defaultdict(int)
  for word in LEGAL_TARGETS:  # [:10]:
    #        print(f'Solving: {word}...')
    guesses_needed = play(targeter=lambda: word,
                          guesser=conservative_restricted_choice)
    solve_times[word] = guesses_needed
    meta_score[guesses_needed] += 1

  #  print('Guesses needed, by word:')
  #  for word,guesses_needed in solve_times.items():
  #    print(f'\t{word}\t{guesses_needed}')
  print("Distribution of guesses_needed:", sorted(meta_score.items()))
  # dump_cache()


def dump_cache():
  print("High-value cache items:")
  for k, v in sorted(guess_cache.cache(HARD_MODE).items()):
    if len(k) < 2:
      print(f'  {k}: {v},')


def reverse_engineer_starting_guess(game_summary):
  target = LEGAL_TARGETS[game_summary.day]
  scores = game_summary.scores
  approximate_best_starting_guesses = [
      l.strip() for l in open('best-starting-guesses.txt')]
  frequency_ranks = [line.strip().split(' ')
                     for line in open('common-words.txt')]
  frequency_ranks = {t[0]: int(t[1]) for t in frequency_ranks}
  remaining_targets = LEGAL_TARGETS
  print('guess', 'guess strength', 'guess frequency', 'strength * frequency',
        'num_remaining_targets', 'remaining_targets', sep='\t')
  for s in scores:
    print(pretty_print(s))
    guess_candidates = []
    for guess in LEGAL_GUESSES:
      if auto_scorer(guess, target) != s:
        continue
      buckets = collections.defaultdict(list)
      for t in remaining_targets:
        buckets[auto_scorer(guess, t)].append(t)
      targets = buckets[s]
      # approximate_best_starting_guesses.index(guess),
      guess_strength = max(len(ts) for s, ts in buckets.items())
      guess_frequency = frequency_ranks[guess]
      guess_candidates.append((
          guess,
          guess_strength,
          guess_frequency,
          guess_strength * guess_frequency,
          len(targets),
          len(targets) < 10 and targets or (
              "too many remaining targets (%d) to display" % len(targets)),
      ))
    for gc in sorted(guess_candidates, key=lambda gc: gc[1], reverse=True):
      print('\t'.join(str(x) for x in gc))
    g = None
    while g not in LEGAL_GUESSES:
      g = input('Use human intuition to select the guesser\'s last guess from the %d above options: ' % len(
          guess_candidates)).upper()
    remaining_targets = restrict_one(remaining_targets, g, s)


def find_max_branching_factor():
  scores = {}
  max_score_count_per_target = 0
  for t in LEGAL_TARGETS:
    scores_per_target = set()
    for g in LEGAL_GUESSES:
      s = auto_scorer(g, t)
      scores[s] = (g, t)
      scores_per_target.add(s)
    max_score_count_per_target = max(
        max_score_count_per_target, len(scores_per_target))
  for score, words in scores.items():
    print(f'{score}:\t{words}')
  print('max_score_count_per_target:', max_score_count_per_target)
  # This is the largest number of buckets any single guess can split the
  # solution space into. (192)


def deep_search():
  approximate_best_starting_guesses = [
      l.strip() for l in open('best-starting-guesses.txt')]
  print('deep_searching...')
  n = len(LEGAL_GUESSES)
  max_bucket_size_by_first_guess = {}
  for i, g1 in enumerate(approximate_best_starting_guesses):
    print(f'trying {g1} ({i}/{n})')
    buckets1 = collections.defaultdict(list)
    for t in LEGAL_TARGETS:
      buckets1[auto_scorer(g1, t)].append(t)
    max_bucket_size, worst_score = max((len(v), k) for k, v in buckets1.items())
    print(f'{g1} -> {worst_score} leaves {max_bucket_size} possible targets in a single bucket.')
'''
    for s, ts in sorted(buckets1.items()):
      best_worst_case = (n, None)
      for i2,g2 in enumerate(approximate_best_starting_guesses):
        #        print(f'\ttrying {g2} ({i}/{n})')
        buckets2 = collections.defaultdict(list)
        for t in ts:
          buckets2[auto_scorer(g2, t)].append(t)

        worst_case = max((len(v), k) for k,v in buckets2.items())
        max_bucket_size, worst_score = worst_case
        # print(f'\t{g1} -> {s} -> {g2} never leaves more than {max_bucket_size} targets in a single bucket.')
        best_worst_case = min(best_worst_case, (max_bucket_size, g2))
      smallest_largest_bucket_size, guess = best_worst_case
      print(f'{g1} -> {s} -> {guess} never leaves more than {smallest_largest_bucket_size} targets in a single bucket.')
'''
#    max_bucket_size_by_first_guess[g1] = max(len(v) for k,v in buckets1.items())
#  best_first_guesses_by_max_bucket_size = sorted(max_bucket_size_by_first_guess.items(), key=lambda x: x[1])
#  print(best_first_guesses_by_max_bucket_size[:10])


def main():
  load_words()

  # deep_search()
  # find_all_scores()

  if len(sys.argv) < 2:
    print("Usage: python3 wordle.py [-h] [-c | -m TARGET | -a TARGET | -e]")
    print("\t-c: cheat; AI will solve the wordle if you score its guesses. No target can be provided.")
    print("\t-m: manual; You'll solve this wordle yourself, and the AI will score your guesses. A TARGET must be provided.")
    print("\t-a: auto; The AI will solve this wordle itself, scoring its own guesses. A TARGET must be provided.")
    print("\t-e: everything; the AI will solve every wordle, and display the distribution of guesses required. No target can be provided.")
    print()
    print("\tTARGET can be any one of:")
    print("\t\ta 5-letter word from the list of valid targets")
    print("\t\ta (0-based) index into the list of valid targets")
    print("\t\t'-r', in which case a random target will be selected")
    print("\t\t'-s', in which case 'absurdle' logic will put off picking a specific target for as long as possible.")

  guesser, scorer = None, None
  absurdle = False
  for arg in sys.argv[1:]:
    if arg == '-h':  # enable hard mode
      global HARD_MODE
      HARD_MODE = True
      continue
    elif arg == '-c':  # cheat
      # AI will solve this wordle for you.
      guesser = conservative_restricted_choice
      scorer = user_scorer  # You'll need to score words as it makes guesses.
      play(targeter=no_target, guesser=guesser, scorer=scorer)
      continue
    elif arg == '-m':  # manual
      guesser = user_choice  # You'll be solving this wordle.
      scorer = auto_scorer  # The computer will score your guesses.
      continue
    elif arg == '-a':  # auto
      # AI will solve this wordle for you.
      guesser = conservative_restricted_choice
      scorer = auto_scorer  # The computer will score its own guesses.
      continue
    elif arg == '-e':  # everything
      solve_everything()
      continue
    elif arg == '-v':  # reverse-engineer
      reverse_engineer_starting_guess(parse_snippet("".join(sys.stdin)))
      continue

    if arg.isnumeric():
      targeter = lambda: wordle_target(int(arg))
    elif arg.upper() in LEGAL_TARGETS:
      targeter = lambda: arg.upper()
    elif arg == '-r':
      targeter = random_target
    elif arg == '-s':  # absurdle
      targeter = lambda: None
      absurdle = True
    else:
      print(f'Don\'t know what to do with arg: {arg}')
      continue

    if guesser is None or scorer is None:
      print('You must specify one of [-m|-a] before selecting a target.')
      continue
    play(targeter=targeter, guesser=guesser, scorer=scorer, absurdle=absurdle)

  # test_mode()
  # ai_guesser()
  # human_guesser()
  # solve_everything()
  # history_mode(206)

import cProfile
if __name__ == '__main__':
  # cProfile.run('main()', 'main_profile')
  main()
