class Memoize:
  def __init__(self, f, display=False):
    self.f = f
    self.memo = {}
    self.display = display
  def __call__(self, *args):
    if not args in self.memo:
      self.memo[args] = self.f(*args)
      if self.display:
        print 'memoized%s = %s' % (args, self.memo[args])
    return self.memo[args]

import math
import collections
import fractions

# Given a list of frequency dictionaries, compute their product.
# Optionally, apply a supplied reduce function to the resulting events sequences.
def cross_counted(args, f=lambda x: x):
  product = reduce(lambda left, right: {l + (r,): lc * rc
                                        for l, lc in left.iteritems()
                                        for r, rc in right.iteritems()},
                   args, {():1})
  result = collections.Counter()
  for event, count in product.iteritems():
    result[f(event)] += count
  return result

assert (cross_counted([{'a':2, 'b':3},
                       {'c':5, 'd':7, 'e':11}]) ==
        {('a', 'c'): 10,
         ('a', 'd'): 14,
         ('a', 'e'): 22,
         ('b', 'c'): 15,
         ('b', 'd'): 21,
         ('b', 'e'): 33,
         })

assert (cross_counted([{'a':2, 'b':3},
                       {'c':5, 'd':7, 'e':11}],
                      lambda x: x[0]) ==
        {'a': 10 + 14 + 22,
         'b': 15 + 21 + 33,})

# Die outcome names.
BRAIN_GREEN = 'bg'
BRAIN_YELLOW = 'by'
BRAIN_RED = 'br'
BLAM_GREEN = '!g'
BLAM_YELLOW = '!y'
BLAM_RED = '!r'
FEET_GREEN = 'fg'
FEET_YELLOW = 'fy'
FEET_RED = 'fr'

# Given a sequence of die outcomes, combine them into a total outcome, as a tuple of tuples:
# ((g,y,r blams), (g,y,r brains), (g,y,r feet))
def combine_roll(dice):
  c = collections.Counter(dice)
  return ((c[BLAM_GREEN], c[BLAM_YELLOW], c[BLAM_RED]),
          (c[BRAIN_GREEN], c[BRAIN_YELLOW], c[BRAIN_RED]),
          (c[FEET_GREEN], c[FEET_YELLOW], c[FEET_RED]))

# Outcome distribution by die color.
DIE_GREEN =  [{ FEET_GREEN:2,  BLAM_GREEN:1,  BRAIN_GREEN:3 }]
DIE_YELLOW = [{ FEET_YELLOW:2, BLAM_YELLOW:2, BRAIN_YELLOW:2 }]
DIE_RED =    [{ FEET_RED:2,    BLAM_RED:3,    BRAIN_RED:1 }]

# Game Rules:
MAX_BLAMS = 3  # You lose when you have this many blams.
HAND_SIZE = 3  # You roll this many dice at a time.

# Behavioral limits.
MAX_BRAINS = 13  # Stop playing when you have this many brains.

# How many of each die color exist.
NUM_GREENS = 6
NUM_YELLOWS = 4
NUM_REDS = 3

# Tuple indices.
GREEN = 0
YELLOW = 1
RED = 2

# Scoring function
UTILITY = lambda score: score
STOP_FUNCTION = lambda score: score >= MAX_BRAINS

def best_outcome(score=0,
                 blams=(0,0,0),
                 brains=(0,0,0),
                 hand=(0,0,0),
                 cup=(NUM_GREENS, NUM_YELLOWS, NUM_REDS)):
  key = (score, blams, brains, hand, cup)
  # print key
  assert (sum(blams) + sum(brains) + sum(hand) + sum(cup)
          == NUM_GREENS + NUM_YELLOWS + NUM_REDS)

  if sum(blams) >= MAX_BLAMS: return UTILITY(0)  # Too many blams loses everything.
  if STOP_FUNCTION(score): return UTILITY(score)  # Assumes you stand once reaching MAX_BRAINS.

  dice_needed = HAND_SIZE - sum(hand)  # How many dice we'll need to draw from the cup.

  if dice_needed > sum(cup):
    # Refill cup with brains, but remember the score for them.
    cup = (cup[GREEN] + brains[GREEN],
              cup[YELLOW] + brains[YELLOW],
              cup[RED] + brains[RED])
    brains = (0,0,0)

  # Possible outcomes for drawing from the cup.
  # If dice_needed == 0, this will be {(), 1}; we draw nothing 100% of the time.
  draws = collections.Counter(possible_draws(dice_needed, cup))
  num_draws = sum(draws.values())

  total_expected_utils = fractions.Fraction(0)  # Running total of the value of our current situation.
  for draw, draw_frequency in draws.iteritems():
    # Given a draw, compute all possible roll outcomes:
    outcomes = cross_counted(
      DIE_GREEN * (hand[GREEN] + draw[GREEN]) +
      DIE_YELLOW * (hand[YELLOW] + draw[YELLOW]) +
      DIE_RED * (hand[RED] + draw[RED]),
      combine_roll)

    num_outcomes = sum(outcomes.values())
    draw_expected_utils = fractions.Fraction(0)  # Running total of the value of this draw.
    for outcome, outcome_frequency in outcomes.iteritems():
      outcome_blams, outcome_brains, outcome_feet = outcome
      if sum(outcome_feet) == HAND_SIZE and dice_needed == 0:
        # Triple feet, and we were allowed to stand already.
        # This would result in a recursive call to evaluate exactly the same 
        # position we were just in. Because math, dropping this outcome entirely works.
        num_outcomes -= outcome_frequency
        continue
      # Recursively score the resulting situation.
      outcome_score = best_outcome(score + sum(outcome_brains),
                                   (blams[GREEN] + outcome_blams[GREEN],
                                    blams[YELLOW] + outcome_blams[YELLOW],
                                    blams[RED] + outcome_blams[RED]),
                                   (brains[GREEN] + outcome_brains[GREEN],
                                    brains[YELLOW] + outcome_brains[YELLOW],
                                    brains[RED] + outcome_brains[RED]),
                                   outcome_feet,
                                   (cup[GREEN] - draw[GREEN],
                                    cup[YELLOW] - draw[YELLOW],
                                    cup[RED] - draw[RED]))
      # Add the score for this outcome to the value of the draw.
      # Don't normalize by outcome count yet, because outcomes we haven't considered yet
      # may get dropped.
      draw_expected_utils += outcome_frequency * outcome_score

    # Add the value for this draw to the total value, normalized by draw and outcome counts.
    total_expected_utils += draw_frequency * draw_expected_utils / num_outcomes / num_draws

  utils, choice = max((total_expected_utils, 'ROLL'), (UTILITY(score), 'STAND'))
  emit(key, choice, utils)
  return utils

# Avoid re-computing scenarios.
best_outcome = Memoize(best_outcome)

# Given a requested number of dice, and a cup population, yield all possible draws.
def possible_draws(needed, cup):
  assert needed <= sum(cup)
  if needed == 0 or min(cup) < 0:
    yield (0,0,0)
    return

  # Try drawing one green:
  for draw in possible_draws(needed - 1, (cup[GREEN]-1, cup[YELLOW], cup[RED])):
    for i in range(cup[GREEN]):
      yield (draw[GREEN]+1, draw[YELLOW], draw[RED])
  # Try drawing one yellow:
  for draw in possible_draws(needed - 1, (cup[GREEN], cup[YELLOW]-1, cup[RED])):
    for i in range(cup[YELLOW]):
      yield (draw[GREEN], draw[YELLOW]+1, draw[RED])
  # Try drawing one red:
  for draw in possible_draws(needed - 1, (cup[GREEN], cup[YELLOW], cup[RED]-1)):
    for i in range(cup[RED]):
      yield (draw[GREEN], draw[YELLOW], draw[RED]+1)

# A local heuristic for estimating whether one should roll or stand.
# To be graded against the actual optimal behavior in every situation.
def heuristic(key):
  score, blams_by_color, brains_by_color, hand, cup = key
  blams = sum(blams_by_color)
  brains = score
  if brains == 0: return 'ROLL' # gotta play to win
  if blams == 2 and brains == 1 and hand[RED] == 0 and (hand[GREEN] > hand[YELLOW]):
    return 'ROLL' # take risks with not many brains at stake, and good dice in hand
  if blams == 2: return 'STAND' # be afraid of getting shot
  if blams + hand[RED] >= 3: return 'STAND' # don't reroll reds
  if brains + blams + hand[RED] - hand[GREEN] >= 9: return 'STAND'
  return 'ROLL'

# Print a situation, the correct decision for that situation,
# the score obtained by making that decision, and the loss incurred by following the
# heuristic instead.
def emit(key, choice, result):
  error = 0
  if heuristic(key) != choice:
    stand_score = key[0]
    if stand_score != result:
      error = math.fabs(result - stand_score) / stand_score
  print "%s\t%s\t%4f\t%4f" % (key, choice, result, error)
  #print "%s\t%s\t%s\t%s" % (key, choice, result, error)

def threshold_utility(score, brains_needed, leaders=1):
  if score < brains_needed: return fractions.Fraction(0)
  if score > brains_needed: return fractions.Fraction(1)
  return fractions.Fraction(1, leaders+1)

def threshold(brains_needed, leaders=1):
  return (lambda score: threshold_utility(score, brains_needed, leaders)), (lambda score: score > brains_needed)

print "(g, y, r blams), (g, y, r brains), (g, y, r in hand), (g, y, r in cup), recommendation, score, importance"

import sys
sys.setrecursionlimit(10000)

UTILITY, STOP_FUNCTION = threshold(0)

best_outcome()
