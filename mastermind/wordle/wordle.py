import random
import collections

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


NO_MATCH = 0
WRONG_SPOT = 1
RIGHT_SPOT = 2


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


def parse_score_string(score_string):
  score = []
  for s in score_string.upper():
    if s in [NO_MATCH, 'B']:
      score.append(NO_MATCH)
    if s in [WRONG_SPOT, 'Y']:
      score.append(WRONG_SPOT)
    if s in [RIGHT_SPOT, 'G']:
      score.append(RIGHT_SPOT)
  return tuple(score)

assert(auto_scorer('SANDS', 'BRASS') == parse_score_string('yybbg'))
assert(auto_scorer('TURNS', 'BRASS') == parse_score_string('bbybg'))
assert(auto_scorer('SUPER', 'BRASS') == parse_score_string('ybbby'))
assert(auto_scorer('CARBS', 'BRASS') == parse_score_string('byyyg'))
assert(auto_scorer('BARBS', 'BRASS') == parse_score_string('gyybg'))

PRETTY_PRINT = {
    NO_MATCH: '⬛',
    WRONG_SPOT: '🟨',
    RIGHT_SPOT: '🟩',
    'ALTERNATE_NO_MATCH': '⬜️⬜️',
}


def pretty_print(score):
  return ''.join(PRETTY_PRINT[s] for s in score)

assert(pretty_print(parse_score_string('byg')) == '⬛🟨🟩')


def user_choice(prev_guesses=None, prev_scores=None):
  if prev_guesses:
    print()
    for guess, score in zip(prev_guesses, prev_scores):
      pretty_score = pretty_print(score)
      print(f'{guess}: {pretty_score}')
    wordle_keyboard(prev_guesses, prev_scores)
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

EASY_MODE_CACHE = {
    (): ('RAISE', (168, 0)),
    ((0, 0, 0, 0, 0),): ('BLUDY', (13, 1)),
    ((0, 0, 0, 0, 1),): ('DENET', (9, 1)),
    ((0, 0, 0, 0, 2),): ('CLOUD', (5, 1)),
    ((0, 0, 0, 1, 0),): ('MUTON', (7, 1)),
    ((0, 0, 0, 1, 1),): ('SPELT', (4, 0)),
    ((0, 0, 0, 1, 2),): ('CLONK', (3, 1)),
    ((0, 0, 0, 2, 0),): ('FLOSS', (2, 0)),
    ((0, 0, 0, 2, 1),): ('CLOGS', (1, 1)),
    ((0, 0, 0, 2, 2),): ('CLOTH', (3, 1)),
    ((0, 0, 1, 0, 0),): ('UNTIL', (11, 0)),
    ((0, 0, 1, 0, 1),): ('FINED', (3, 1)),
    ((0, 0, 1, 0, 2),): ('BUNDT', (4, 1)),
    ((0, 0, 1, 1, 0),): ('CLOUT', (2, 1)),
    ((0, 0, 1, 1, 1),): ('ISLET', (1, 0)),
    ((0, 0, 1, 1, 2),): ('SIEGE', (1, 0)),
    ((0, 0, 1, 2, 0),): ('COMPT', (1, 1)),
    ((0, 0, 2, 0, 0),): ('CLOOT', (5, 1)),
    ((0, 0, 2, 0, 1),): ('CHYND', (2, 1)),
    ((0, 0, 2, 0, 2),): ('CLINT', (3, 1)),
    ((0, 0, 2, 1, 0),): ('BLUNT', (4, 1)),
    ((0, 0, 2, 1, 1),): ('SHIED', (1, 0)),
    ((0, 0, 2, 1, 2),): ('ALANT', (3, 1)),
    ((0, 0, 2, 2, 0),): ('FOEHN', (2, 1)),
    ((0, 0, 2, 2, 2),): ('NOISE', (1, 0)),
    ((0, 1, 0, 0, 0),): ('CLOAK', (7, 0)),
    ((0, 1, 0, 0, 1),): ('METAL', (5, 0)),
    ((0, 1, 0, 0, 2),): ('ALBUM', (7, 1)),
    ((0, 1, 0, 1, 0),): ('CLAPT', (4, 1)),
    ((0, 1, 0, 1, 1),): ('DWELT', (2, 1)),
    ((0, 1, 0, 1, 2),): ('THILK', (4, 1)),
    ((0, 1, 0, 2, 0),): ('SLASH', (3, 0)),
    ((0, 1, 0, 2, 1),): ('BUFTY', (1, 1)),
    ((0, 1, 0, 2, 2),): ('BUTCH', (1, 1)),
    ((0, 1, 1, 0, 0),): ('PLANT', (3, 1)),
    ((0, 1, 1, 0, 1),): ('EMAIL', (1, 0)),
    ((0, 1, 1, 1, 0),): ('SLAIN', (1, 0)),
    ((0, 1, 2, 0, 0),): ('ALIGN', (2, 0)),
    ((0, 1, 2, 0, 2),): ('ALKYD', (1, 1)),
    ((0, 2, 0, 0, 0),): ('BUNTY', (11, 1)),
    ((0, 2, 0, 0, 1),): ('LIGHT', (3, 1)),
    ((0, 2, 0, 0, 2),): ('MULCT', (3, 1)),
    ((0, 2, 0, 1, 0),): ('POULT', (3, 1)),
    ((0, 2, 0, 1, 2),): ('BUTCH', (3, 1)),
    ((0, 2, 0, 2, 0),): ('PLONG', (1, 1)),
    ((0, 2, 0, 2, 2),): ('AMPLE', (1, 1)),
    ((0, 2, 1, 0, 0),): ('CELOM', (2, 1)),
    ((0, 2, 1, 1, 0),): ('BANCS', (1, 1)),
    ((0, 2, 2, 0, 0),): ('FAINT', (2, 0)),
    ((0, 2, 2, 0, 2),): ('NAIVE', (1, 0)),
    ((1, 0, 0, 0, 0),): ('COLON', (10, 1)),
    ((1, 0, 0, 0, 1),): ('OUTER', (16, 0)),
    ((1, 0, 0, 0, 2),): ('COMPT', (6, 1)),
    ((1, 0, 0, 1, 0),): ('BURNT', (3, 1)),
    ((1, 0, 0, 1, 1),): ('SEWER', (3, 0)),
    ((1, 0, 0, 1, 2),): ('POTCH', (2, 1)),
    ((1, 0, 0, 2, 0),): ('CRUST', (2, 0)),
    ((1, 0, 0, 2, 1),): ('CHOPS', (1, 1)),
    ((1, 0, 0, 2, 2),): ('AEONS', (2, 1)),
    ((1, 0, 1, 0, 0),): ('CHOIR', (3, 0)),
    ((1, 0, 1, 0, 1),): ('DELFT', (6, 1)),
    ((1, 0, 1, 0, 2),): ('DIRGE', (1, 0)),
    ((1, 0, 1, 1, 0),): ('SPRIG', (1, 0)),
    ((1, 0, 1, 1, 1),): ('MISER', (1, 0)),
    ((1, 0, 2, 0, 0),): ('CLONK', (5, 1)),
    ((1, 0, 2, 0, 1),): ('DECAF', (2, 1)),
    ((1, 0, 2, 0, 2),): ('BUMPH', (4, 1)),
    ((1, 0, 2, 1, 0),): ('SHIRK', (1, 0)),
    ((1, 0, 2, 2, 0),): ('ABACK', (2, 1)),
    ((1, 1, 0, 0, 0),): ('TRONC', (9, 1)),
    ((1, 1, 0, 0, 1),): ('BRACT', (5, 1)),
    ((1, 1, 0, 0, 2),): ('GRACE', (6, 0)),
    ((1, 1, 0, 1, 0),): ('CHANT', (3, 1)),
    ((1, 1, 0, 1, 1),): ('BUMPH', (1, 1)),
    ((1, 1, 0, 1, 2),): ('CHANT', (1, 1)),
    ((1, 1, 0, 2, 0),): ('ABACS', (2, 1)),
    ((1, 1, 1, 0, 0),): ('ALAND', (3, 1)),
    ((1, 1, 2, 0, 0),): ('ABLED', (1, 1)),
    ((1, 2, 0, 0, 0),): ('CLOMP', (4, 1)),
    ((1, 2, 0, 0, 1),): ('EMPTY', (7, 1)),
    ((1, 2, 0, 0, 2),): ('ABACA', (1, 1)),
    ((1, 2, 2, 0, 0),): ('ACHED', (1, 1)),
    ((2, 0, 0, 0, 0),): ('BOODY', (1, 1)),
    ((2, 0, 0, 0, 1),): ('COLED', (3, 1)),
    ((2, 0, 0, 0, 2),): ('ROGUE', (1, 0)),
    ((2, 0, 1, 0, 0),): ('ROBIN', (1, 0)),
    ((2, 0, 1, 0, 1),): ('ALDER', (2, 1)),
    ((2, 0, 1, 1, 1),): ('RESIN', (1, 0)),
    ((2, 1, 0, 0, 0),): ('ROYAL', (1, 0)),
    ((2, 1, 0, 0, 1),): ('CABAL', (2, 1)),
    ((2, 2, 0, 0, 0),): ('LOHAN', (1, 1)),
    ((2, 2, 0, 0, 1),): ('AMNIC', (1, 1)),
    ((2, 2, 1, 0, 0),): ('ABORD', (1, 1)),
}
HARD_MODE_CACHE = {
    (): ('RAISE', (168, 0)),
    ((0, 0, 0, 0, 0),): ('BLUDY', (13, 1)),
    ((0, 0, 0, 0, 1),): ('DENET', (9, 1)),
    ((0, 0, 0, 0, 2),): ('ELUDE', (7, 0)),
    ((0, 0, 0, 1, 0),): ('STOOL', (8, 0)),
    ((0, 0, 0, 1, 1),): ('SPELT', (4, 0)),
    ((0, 0, 0, 1, 2),): ('STOPE', (4, 1)),
    ((0, 0, 0, 2, 0),): ('FLOSS', (2, 0)),
    ((0, 0, 0, 2, 1),): ('GHEST', (2, 1)),
    ((0, 0, 0, 2, 2),): ('CHOSE', (5, 0)),
    ((0, 0, 1, 0, 0),): ('UNTIL', (11, 0)),
    ((0, 0, 1, 0, 1),): ('FINED', (3, 1)),
    ((0, 0, 1, 0, 2),): ('LIGNE', (6, 1)),
    ((0, 0, 1, 1, 0),): ('STOIC', (3, 0)),
    ((0, 0, 1, 1, 1),): ('ISLET', (1, 0)),
    ((0, 0, 1, 1, 2),): ('SIEGE', (1, 0)),
    ((0, 0, 1, 2, 0),): ('GIPSY', (2, 0)),
    ((0, 0, 2, 0, 0),): ('CLINT', (6, 1)),
    ((0, 0, 2, 0, 1),): ('TEIND', (2, 1)),
    ((0, 0, 2, 0, 2),): ('CLINE', (4, 1)),
    ((0, 0, 2, 1, 0),): ('STINK', (5, 0)),
    ((0, 0, 2, 1, 1),): ('SHIED', (1, 0)),
    ((0, 0, 2, 1, 2),): ('SLIPE', (6, 1)),
    ((0, 0, 2, 2, 0),): ('FOIST', (3, 0)),
    ((0, 0, 2, 2, 2),): ('NOISE', (1, 0)),
    ((0, 1, 0, 0, 0),): ('CLOAK', (7, 0)),
    ((0, 1, 0, 0, 1),): ('METAL', (5, 0)),
    ((0, 1, 0, 0, 2),): ('AMBLE', (8, 0)),
    ((0, 1, 0, 1, 0),): ('STALK', (5, 0)),
    ((0, 1, 0, 1, 1),): ('STEAD', (3, 0)),
    ((0, 1, 0, 1, 2),): ('SHALE', (9, 0)),
    ((0, 1, 0, 2, 0),): ('SLASH', (3, 0)),
    ((0, 1, 0, 2, 1),): ('BEAST', (3, 0)),
    ((0, 1, 0, 2, 2),): ('CEASE', (2, 0)),
    ((0, 1, 1, 0, 0),): ('TIDAL', (4, 0)),
    ((0, 1, 1, 0, 1),): ('EMAIL', (1, 0)),
    ((0, 1, 1, 1, 0),): ('SLAIN', (1, 0)),
    ((0, 1, 2, 0, 0),): ('ALIGN', (2, 0)),
    ((0, 1, 2, 0, 2),): ('AGILE', (2, 0)),
    ((0, 2, 0, 0, 0),): ('BANTY', (12, 1)),
    ((0, 2, 0, 0, 1),): ('LATEN', (4, 1)),
    ((0, 2, 0, 0, 2),): ('GABLE', (6, 1)),
    ((0, 2, 0, 1, 0),): ('NASAL', (4, 0)),
    ((0, 2, 0, 1, 2),): ('BASTE', (5, 0)),
    ((0, 2, 0, 2, 0),): ('LASSO', (2, 0)),
    ((0, 2, 0, 2, 2),): ('LAPSE', (2, 0)),
    ((0, 2, 1, 0, 0),): ('CAMPI', (3, 1)),
    ((0, 2, 1, 1, 0),): ('LABIS', (2, 1)),
    ((0, 2, 2, 0, 0),): ('FAINT', (2, 0)),
    ((0, 2, 2, 0, 2),): ('NAIVE', (1, 0)),
    ((1, 0, 0, 0, 0),): ('WROOT', (11, 1)),
    ((1, 0, 0, 0, 1),): ('OUTER', (16, 0)),
    ((1, 0, 0, 0, 2),): ('PRONE', (7, 0)),
    ((1, 0, 0, 1, 0),): ('SHORT', (4, 0)),
    ((1, 0, 0, 1, 1),): ('SEWER', (3, 0)),
    ((1, 0, 0, 1, 2),): ('SCORE', (5, 0)),
    ((1, 0, 0, 2, 0),): ('CRUST', (2, 0)),
    ((1, 0, 0, 2, 1),): ('CRESS', (2, 0)),
    ((1, 0, 0, 2, 2),): ('EROSE', (3, 1)),
    ((1, 0, 1, 0, 0),): ('CHOIR', (3, 0)),
    ((1, 0, 1, 0, 1),): ('VINER', (8, 1)),
    ((1, 0, 1, 0, 2),): ('DIRGE', (1, 0)),
    ((1, 0, 1, 1, 0),): ('SPRIG', (1, 0)),
    ((1, 0, 1, 1, 1),): ('MISER', (1, 0)),
    ((1, 0, 2, 0, 0),): ('PRINK', (6, 1)),
    ((1, 0, 2, 0, 1),): ('CRIED', (4, 0)),
    ((1, 0, 2, 0, 2),): ('TRIPE', (7, 0)),
    ((1, 0, 2, 1, 0),): ('SHIRK', (1, 0)),
    ((1, 0, 2, 2, 0),): ('BRISK', (3, 0)),
    ((1, 1, 0, 0, 0),): ('BRANT', (10, 1)),
    ((1, 1, 0, 0, 1),): ('DERAT', (6, 1)),
    ((1, 1, 0, 0, 2),): ('GRACE', (6, 0)),
    ((1, 1, 0, 1, 0),): ('STARK', (6, 0)),
    ((1, 1, 0, 1, 1),): ('SHEAR', (3, 0)),
    ((1, 1, 0, 1, 2),): ('SCARE', (4, 0)),
    ((1, 1, 0, 2, 0),): ('BRASH', (3, 0)),
    ((1, 1, 1, 0, 0),): ('BRAIN', (4, 0)),
    ((1, 1, 2, 0, 0),): ('BRIAR', (2, 0)),
    ((1, 2, 0, 0, 0),): ('CARRY', (6, 0)),
    ((1, 2, 0, 0, 1),): ('GATER', (11, 1)),
    ((1, 2, 0, 0, 2),): ('CABRE', (1, 1)),
    ((1, 2, 2, 0, 0),): ('DAIRY', (2, 0)),
    ((2, 0, 0, 0, 0),): ('ROOMY', (2, 0)),
    ((2, 0, 0, 0, 1),): ('RUDER', (4, 0)),
    ((2, 0, 0, 0, 2),): ('ROGUE', (1, 0)),
    ((2, 0, 1, 0, 0),): ('ROBIN', (1, 0)),
    ((2, 0, 1, 0, 1),): ('RIDER', (3, 0)),
    ((2, 0, 1, 1, 1),): ('RESIN', (1, 0)),
    ((2, 1, 0, 0, 0),): ('ROYAL', (1, 0)),
    ((2, 1, 0, 0, 1),): ('RELAY', (3, 0)),
    ((2, 2, 0, 0, 0),): ('RANDY', (3, 0)),
    ((2, 2, 0, 0, 1),): ('RACER', (2, 0)),
    ((2, 2, 1, 0, 0),): ('RABID', (2, 0)),
}


def conservative_restricted_choice(prev_guesses, prev_scores):
  remaining_targets = restrict_many(LEGAL_TARGETS, prev_guesses, prev_scores)
  remaining_targets_set = set(remaining_targets)
  if HARD_MODE:
    legal_guesses = restrict_many(LEGAL_GUESSES, prev_guesses, prev_scores)
    cache = HARD_MODE_CACHE
  else:
    legal_guesses = LEGAL_GUESSES
    cache = EASY_MODE_CACHE

  # print('%d possible targets remain' % len(remaining_targets))
  cache_key = ()
  for score, guess in zip(prev_scores, prev_guesses):
    if cache_key in cache and guess == cache[cache_key][0]:
      cache_key = cache_key + (score,)
    else:
      cache_key = None
      break
  if cache_key is not None and cache_key in cache:
    # print('(precomputed) worst case for guess %s: %d remaining possibilities' % cache[cache_key])
    return cache[cache_key][0]

  if len(remaining_targets) <= 2:
    # print('remaining targets down to %s; guessing %s' % (remaining_targets, remaining_targets[0]))
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
  # print(f'worst case for guess {best_guess}: {best_worst_case} remaining
  # possibilities')

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


def play(targeter=random_target, guesser=user_choice, scorer=auto_scorer):
  target = targeter()

  guesses = []
  scores = []
  legal_guesses = LEGAL_GUESSES
  while not guesses or scores[-1] != (RIGHT_SPOT,) * WORD_LENGTH:
    guess = guesser(guesses, scores)
    if guess not in legal_guesses:
      print("Illegal guess. Try again.")
      continue
    guesses.append(guess)
    score = scorer(guess, target)
    scores.append(score)
    pretty_score = pretty_print(score)
    print(f'{guess}: {pretty_score}')
    if HARD_MODE:
      legal_guesses = restrict_one(legal_guesses, guess, score)

  print('\n')
  if target is None:
    target = guesses[-1]
  print(wordle_snippet(scores, LEGAL_TARGETS.index(target)))
  print('\n')

  return len(scores)


def wordle_snippet(scores, i='?'):
  num_guesses = len(scores)
  hard_mode_star = HARD_MODE and '*' or ''
  return f'Wordle {i} {num_guesses}/6{hard_mode_star}\n\n' + '\n'.join(pretty_print(s) for s in scores)


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
      ABSENT:  '1;37;40',
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
  meta_score = collections.defaultdict(int)
  for word in LEGAL_TARGETS:  # [:10]:
    #        print(f'Solving: {word}...')
    guesses_needed = play(targeter=lambda: word,
                          guesser=conservative_restricted_choice)
    meta_score[guesses_needed] += 1
  print("Distribution of guesses_needed:", sorted(meta_score.items()))
  print("High-value cache items:")
  if HARD_MODE:
    cache = HARD_MODE_CACHE
  else:
    cache = EASY_MODE_CACHE
  for k, v in sorted(cache.items()):
    if len(k) < 2:
      print(f'  {k}: {v},')


def reverse_engineer_starting_guess():
  recent_targets = [
      'ABBEY',
      #'FAVOR',
      #'DRINK',
  ]
  for guess in LEGAL_GUESSES:
    for target in recent_targets:
      if auto_scorer(guess, target) != auto_scorer('RAISE', target):
        break
    else:
      print(guess)


import sys


def main():
  load_words()

  reverse_engineer_starting_guess()

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

  guesser, scorer = None, None
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

    if arg.isnumeric():
      targeter = lambda: wordle_target(int(arg))
    elif arg.upper() in LEGAL_TARGETS:
      targeter = lambda: arg.upper()
    elif arg == '-r':
      targeter = random_target
    else:
      print(f'Don\'t know what to do with arg: {arg}')
      continue

    if guesser is None or scorer is None:
      print('You must specify one of [-m|-a] before selecting a target.')
      continue
    play(targeter=targeter, guesser=guesser, scorer=scorer)

  # test_mode()
  # ai_guesser()
  # human_guesser()
  # solve_everything()
  # history_mode(206)

import cProfile
if __name__ == '__main__':
  # cProfile.run('main()', 'main_profile')
  main()
