import random
import collections

WORD_LENGTH = 5
HARD_MODE = False


def load_words():
  print('loading words...')
  legal_targets = [word.strip().upper() for word in open('legal-targets.txt')]
  legal_guesses = [word.strip().upper() for word in open('legal-guesses.txt')]
  num_targets = len(legal_targets)
  num_guesses = len(legal_guesses)
  print(f'finished loading {num_targets} legal targets and {num_guesses} additional legal guesses.')
  return legal_targets, sorted(legal_targets + legal_guesses)

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
}


def pretty_print(score):
  return ''.join(PRETTY_PRINT[s] for s in score)

assert(pretty_print(parse_score_string('byg')) == '⬛🟨🟩')


def user_choice(prev_guesses=None, prev_scores=None):
  if prev_guesses:
    for guess, score in zip(prev_guesses, prev_scores):
      pretty_score = pretty_print(score)
      print(f'{guess}: {pretty_score}')
    wordle_keyboard(prev_guesses, prev_scores)
  return input('next guess: ').strip().upper()

LEGAL_TARGETS, LEGAL_GUESSES = load_words()


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
    ():  ('RAISE', 168),
    ((0, 0, 0, 0, 0),): ('BLUDY', 13),
    ((0, 0, 0, 0, 1),): ('DENET', 9),
    ((0, 0, 0, 0, 2),): ('CLOUD', 5),
    ((0, 0, 0, 1, 0),): ('MUTON', 7),
    ((0, 0, 0, 1, 1),): ('BETEL', 4),
    ((0, 0, 0, 1, 2),): ('CLONK', 3),
    ((0, 0, 0, 2, 0),): ('FLOSS', 2),
    ((0, 0, 0, 2, 1),): ('CLOGS', 1),
    ((0, 0, 0, 2, 2),): ('CLOTH', 3),
    ((0, 0, 1, 0, 0),): ('UNTIL', 11),
    ((0, 0, 1, 0, 1),): ('FINED', 3),
    ((0, 0, 1, 0, 2),): ('BUNDT', 4),
    ((0, 0, 1, 1, 0),): ('CLOUT', 2),
    ((0, 0, 1, 1, 1),): ('ABETS', 1),
    ((0, 0, 1, 1, 2),): ('AGENE', 1),
    ((0, 0, 1, 2, 0),): ('COMPT', 1),
    ((0, 0, 2, 0, 0),): ('CLOOT', 5),
    ((0, 0, 2, 0, 1),): ('CHYND', 2),
    ((0, 0, 2, 0, 2),): ('CLINT', 3),
    ((0, 0, 2, 1, 0),): ('BLUNT', 4),
    ((0, 0, 2, 1, 1),): ('AAHED', 1),
    ((0, 0, 2, 1, 2),): ('ALANT', 3),
    ((0, 0, 2, 2, 0),): ('FOEHN', 2),
    ((0, 0, 2, 2, 2),): ('ABOON', 1),
    ((0, 1, 0, 0, 0),): ('CLOAK', 7),
    ((0, 1, 0, 0, 1),): ('METAL', 5),
    ((0, 1, 0, 0, 2),): ('ALBUM', 7),
    ((0, 1, 0, 1, 0),): ('CLAPT', 4),
    ((0, 1, 0, 1, 1),): ('DWELT', 2),
    ((0, 1, 0, 1, 2),): ('THILK', 4),
    ((0, 1, 0, 2, 0),): ('SLASH', 3),
    ((0, 1, 0, 2, 1),): ('BUFTY', 1),
    ((0, 1, 0, 2, 2),): ('BUTCH', 1),
    ((0, 1, 1, 0, 0),): ('PLANT', 3),
    ((0, 1, 1, 0, 1),): ('AALII', 1),
    ((0, 1, 1, 1, 0),): ('ALANT', 1),
    ((0, 1, 2, 0, 0),): ('ABAND', 2),
    ((0, 1, 2, 0, 2),): ('ALKYD', 1),
    ((0, 2, 0, 0, 0),): ('BUNTY', 11),
    ((0, 2, 0, 0, 1),): ('LIGHT', 3),
    ((0, 2, 0, 0, 2),): ('MULCT', 3),
    ((0, 2, 0, 1, 0),): ('POULT', 3),
    ((0, 2, 0, 1, 2),): ('BUTCH', 3),
    ((0, 2, 0, 2, 0),): ('PLONG', 1),
    ((0, 2, 0, 2, 2),): ('AMPLE', 1),
    ((0, 2, 1, 0, 0),): ('CELOM', 2),
    ((0, 2, 1, 1, 0),): ('BANCS', 1),
    ((0, 2, 2, 0, 0),): ('ABAFT', 2),
    ((0, 2, 2, 0, 2),): ('ADMAN', 1),
    ((1, 0, 0, 0, 0),): ('COLON', 10),
    ((1, 0, 0, 0, 1),): ('OUTED', 16),
    ((1, 0, 0, 0, 2),): ('COMPT', 6),
    ((1, 0, 0, 1, 0),): ('BURNT', 3),
    ((1, 0, 0, 1, 1),): ('SERED', 3),
    ((1, 0, 0, 1, 2),): ('POTCH', 2),
    ((1, 0, 0, 2, 0),): ('ARCUS', 2),
    ((1, 0, 0, 2, 1),): ('CHOPS', 1),
    ((1, 0, 0, 2, 2),): ('AEONS', 2),
    ((1, 0, 1, 0, 0),): ('AYONT', 3),
    ((1, 0, 1, 0, 1),): ('DELFT', 6),
    ((1, 0, 1, 0, 2),): ('AARGH', 1),
    ((1, 0, 1, 1, 0),): ('ABOUT', 1),
    ((1, 0, 1, 1, 1),): ('ABRIM', 1),
    ((1, 0, 2, 0, 0),): ('CLONK', 5),
    ((1, 0, 2, 0, 1),): ('DECAF', 2),
    ((1, 0, 2, 0, 2),): ('BUMPH', 4),
    ((1, 0, 2, 1, 0),): ('ALTHO', 1),
    ((1, 0, 2, 2, 0),): ('ABACK', 2),
    ((1, 1, 0, 0, 0),): ('TRONC', 9),
    ((1, 1, 0, 0, 1),): ('BRACT', 5),
    ((1, 1, 0, 0, 2),): ('CRAGS', 6),
    ((1, 1, 0, 1, 0),): ('CHANT', 3),
    ((1, 1, 0, 1, 1),): ('BUMPH', 1),
    ((1, 1, 0, 1, 2),): ('CHANT', 1),
    ((1, 1, 0, 2, 0),): ('ABACS', 2),
    ((1, 1, 1, 0, 0),): ('ALAND', 3),
    ((1, 1, 2, 0, 0),): ('ABLED', 1),
    ((1, 2, 0, 0, 0),): ('CLOMP', 4),
    ((1, 2, 0, 0, 1),): ('EMPTY', 7),
    ((1, 2, 0, 0, 2),): ('ABACA', 1),
    ((1, 2, 2, 0, 0),): ('ACHED', 1),
    ((2, 0, 0, 0, 0),): ('BOODY', 1),
    ((2, 0, 0, 0, 1),): ('COLED', 3),
    ((2, 0, 0, 0, 2),): ('ABOUT', 1),
    ((2, 0, 1, 0, 0),): ('ABBOT', 1),
    ((2, 0, 1, 0, 1),): ('ALDER', 2),
    ((2, 0, 1, 1, 1),): ('ABLER', 1),
    ((2, 1, 0, 0, 0),): ('ABAYA', 1),
    ((2, 1, 0, 0, 1),): ('CABAL', 2),
    ((2, 2, 0, 0, 0),): ('LOHAN', 1),
    ((2, 2, 0, 0, 1),): ('AMNIC', 1),
    ((2, 2, 1, 0, 0),): ('ABORD', 1),
}
HARD_MODE_CACHE = {
    (): ('RAISE', 168),
    ((0, 0, 0, 0, 0),): ('BLUDY', 13),
    ((0, 0, 0, 0, 1),): ('DENET', 9),
    ((0, 0, 0, 0, 2),): ('ELUDE', 7),
    ((0, 0, 0, 1, 0),): ('SLOOT', 8),
    ((0, 0, 0, 1, 1),): ('SPEEL', 4),
    ((0, 0, 0, 1, 2),): ('STOPE', 4),
    ((0, 0, 0, 2, 0),): ('FLOSS', 2),
    ((0, 0, 0, 2, 1),): ('GHEST', 2),
    ((0, 0, 0, 2, 2),): ('CHOSE', 5),
    ((0, 0, 1, 0, 0),): ('UNTIL', 11),
    ((0, 0, 1, 0, 1),): ('FINED', 3),
    ((0, 0, 1, 0, 2),): ('LIGNE', 6),
    ((0, 0, 1, 1, 0),): ('CISTS', 3),
    ((0, 0, 1, 1, 1),): ('BENIS', 1),
    ((0, 0, 1, 1, 2),): ('SIEGE', 1),
    ((0, 0, 1, 2, 0),): ('BYSSI', 2),
    ((0, 0, 2, 0, 0),): ('CLINT', 6),
    ((0, 0, 2, 0, 1),): ('TEIND', 2),
    ((0, 0, 2, 0, 2),): ('CLINE', 4),
    ((0, 0, 2, 1, 0),): ('SKINT', 5),
    ((0, 0, 2, 1, 1),): ('HEIDS', 1),
    ((0, 0, 2, 1, 2),): ('SLIPE', 6),
    ((0, 0, 2, 2, 0),): ('FOIST', 3),
    ((0, 0, 2, 2, 2),): ('NOISE', 1),
    ((0, 1, 0, 0, 0),): ('CLOAK', 7),
    ((0, 1, 0, 0, 1),): ('METAL', 5),
    ((0, 1, 0, 0, 2),): ('AMBLE', 8),
    ((0, 1, 0, 1, 0),): ('STALK', 5),
    ((0, 1, 0, 1, 1),): ('ASKED', 3),
    ((0, 1, 0, 1, 2),): ('SHALE', 9),
    ((0, 1, 0, 2, 0),): ('SLASH', 3),
    ((0, 1, 0, 2, 1),): ('BEAST', 3),
    ((0, 1, 0, 2, 2),): ('CEASE', 2),
    ((0, 1, 1, 0, 0),): ('DITAL', 4),
    ((0, 1, 1, 0, 1),): ('AECIA', 1),
    ((0, 1, 1, 1, 0),): ('SLAID', 1),
    ((0, 1, 2, 0, 0),): ('ALIGN', 2),
    ((0, 1, 2, 0, 2),): ('AGILE', 2),
    ((0, 2, 0, 0, 0),): ('BANTY', 12),
    ((0, 2, 0, 0, 1),): ('LATEN', 4),
    ((0, 2, 0, 0, 2),): ('GABLE', 6),
    ((0, 2, 0, 1, 0),): ('NASAL', 4),
    ((0, 2, 0, 1, 2),): ('BASTE', 5),
    ((0, 2, 0, 2, 0),): ('LASSO', 2),
    ((0, 2, 0, 2, 2),): ('LAPSE', 2),
    ((0, 2, 1, 0, 0),): ('CAMPI', 3),
    ((0, 2, 1, 1, 0),): ('LABIS', 2),
    ((0, 2, 2, 0, 0),): ('FAINT', 2),
    ((0, 2, 2, 0, 2),): ('NAIVE', 1),
    ((1, 0, 0, 0, 0),): ('WROOT', 11),
    ((1, 0, 0, 0, 1),): ('OUTER', 16),
    ((1, 0, 0, 0, 2),): ('PRONE', 7),
    ((1, 0, 0, 1, 0),): ('SHORT', 4),
    ((1, 0, 0, 1, 1),): ('SERED', 3),
    ((1, 0, 0, 1, 2),): ('SCORE', 5),
    ((1, 0, 0, 2, 0),): ('CROST', 2),
    ((1, 0, 0, 2, 1),): ('CRESS', 2),
    ((1, 0, 0, 2, 2),): ('EROSE', 3),
    ((1, 0, 1, 0, 0),): ('CHOIR', 3),
    ((1, 0, 1, 0, 1),): ('VINER', 8),
    ((1, 0, 1, 0, 2),): ('BIRLE', 1),
    ((1, 0, 1, 1, 0),): ('DIRTS', 1),
    ((1, 0, 1, 1, 1),): ('MERIS', 1),
    ((1, 0, 2, 0, 0),): ('PRINK', 6),
    ((1, 0, 2, 0, 1),): ('CRIED', 4),
    ((1, 0, 2, 0, 2),): ('TRIPE', 7),
    ((1, 0, 2, 1, 0),): ('SHIRK', 1),
    ((1, 0, 2, 2, 0),): ('BRISK', 3),
    ((1, 1, 0, 0, 0),): ('BRANT', 10),
    ((1, 1, 0, 0, 1),): ('DERAT', 6),
    ((1, 1, 0, 0, 2),): ('GRACE', 6),
    ((1, 1, 0, 1, 0),): ('PRATS', 6),
    ((1, 1, 0, 1, 1),): ('APERS', 3),
    ((1, 1, 0, 1, 2),): ('SCARE', 4),
    ((1, 1, 0, 2, 0),): ('BRASH', 3),
    ((1, 1, 1, 0, 0),): ('BRAIL', 4),
    ((1, 1, 2, 0, 0),): ('ARIOT', 2),
    ((1, 2, 0, 0, 0),): ('CARDY', 6),
    ((1, 2, 0, 0, 1),): ('GATER', 11),
    ((1, 2, 0, 0, 2),): ('CABRE', 1),
    ((1, 2, 2, 0, 0),): ('CAIRD', 2),
    ((2, 0, 0, 0, 0),): ('ROOFY', 2),
    ((2, 0, 0, 0, 1),): ('ROPER', 4),
    ((2, 0, 0, 0, 2),): ('ROGUE', 1),
    ((2, 0, 1, 0, 0),): ('ROBIN', 1),
    ((2, 0, 1, 0, 1),): ('REDIP', 3),
    ((2, 0, 1, 1, 1),): ('RESIN', 1),
    ((2, 1, 0, 0, 0),): ('RHYTA', 1),
    ((2, 1, 0, 0, 1),): ('RECAL', 3),
    ((2, 2, 0, 0, 0),): ('RANDY', 3),
    ((2, 2, 0, 0, 1),): ('RACER', 2),
    ((2, 2, 1, 0, 0),): ('RABID', 2),
}
if HARD_MODE:
  CACHE = HARD_MODE_CACHE
else:
  CACHE = EASY_MODE_CACHE


def conservative_restricted_choice(prev_guesses, prev_scores, scorer=auto_scorer):
  remaining_targets = restrict_many(LEGAL_TARGETS, prev_guesses, prev_scores)
  if HARD_MODE:
    legal_guesses = restrict_many(LEGAL_GUESSES, prev_guesses, prev_scores)
  else:
    legal_guesses = LEGAL_GUESSES

  # print('%d possible targets remain' % len(remaining_targets))
  cache_key = ()
  for score in prev_scores:
    cache_key = cache_key + (score,)
  if cache_key in CACHE:
    # print('(precomputed) worst case for guess %s: %d remaining possibilities' % CACHE[cache_key])
    return CACHE[cache_key][0]

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
      if score_counts[score] > best_worst_case_so_far:
        break
    else:
      worst_score, worst_case = max(score_counts.items(), key=lambda x: x[1])
      worst_case_by_guess[guess] = worst_case
      best_worst_case_so_far = min(best_worst_case_so_far, worst_case)

  best_guess, best_worst_case = min(
      worst_case_by_guess.items(), key=lambda x: x[1])
  # print(f'worst case for guess {best_guess}: {best_worst_case} remaining
  # possibilities')

  if cache_key not in CACHE:
    # print('updating cache: %s:%s' % (cache_key, (best_guess, best_worst_case)))
    CACHE[cache_key] = (best_guess, best_worst_case)

  return best_guess


def wordle_target(i):
  return LEGAL_TARGETS[i - 1]


def random_target():
  target = random.choice(LEGAL_TARGETS)
  print(f'spoiler: the target word is {target}')
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
  print(wordle_snippet(scores, LEGAL_TARGETS.index(target) + 1))
  print('\n')

  return len(scores)


def wordle_snippet(scores, i='?'):
  num_guesses = len(scores)
  return f'Wordle {i} {num_guesses}/6\n\n' + '\n'.join(pretty_print(s) for s in scores)


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
  for k, v in sorted(CACHE.items()):
    if len(k) < 2:
      print(f'    {k}: {v},')


import cProfile
if __name__ == '__main__':
  # test_mode()
  ai_guesser()
  # human_guesser()
  # solve_everything()
  # history_mode(206)
  # cProfile.run('solve_everything()', 'solve_everything_profile')
