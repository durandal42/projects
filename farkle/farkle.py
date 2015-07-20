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

def combine(rolls):
  return tuple(sorted(rolls))

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

# Outcome distribution by die color.
DIE = {result:1 for result in range(1,7)}

# Game Rules:
STARTING_HAND_SIZE = 2  # You roll this many dice at a time.

# Behavioral limits.
MAX_SCORE = 10000  # Stop playing when you have this many points.

# Scoring function
STOP_FUNCTION = lambda score: score >= MAX_SCORE

def best_outcome(score=0,
                 hand=STARTING_HAND_SIZE):
  key = (score, hand)
  assert hand <= STARTING_HAND_SIZE

  if hand == 0: return score
  #TODO(durandal): hot dice: "S"TOP_FUNCTION(score) and ""

  # Given a draw, compute all possible roll outcomes:
  outcomes = cross_counted([DIE] * hand, combine)

  num_outcomes = sum(outcomes.values())
  expected_score = fractions.Fraction(0)  # Running total of the value of this draw.
  for outcome, outcome_frequency in outcomes.iteritems():
    print outcome, outcome_frequency

    # find best scoring strategy per dice-used count
    best_by_used = {}
    for points, used in scoring_strategies(outcome):
      print '\t', points, used
      result = (points, used)
      num_used = len(used)
      if num_used not in best_by_used or points > best_by_used[num_used]:
        best_by_used[num_used] = result
    #print best_by_used

    if len(best_by_used) == 1:  # only option: score nothing
      continue  # farkled out

    if hand in best_by_used:
      # TODO(durandal): hot dice
      pass

    # Recursively score the resulting situations.
    best_plan, outcome_score = max((used, best_outcome(score+plan[0], hand-len(plan[1])))
                                   for score,plan in best_by_used.iteritems())

    print score, hand, best_plan, outcome_score

    expected_score += outcome_frequency * outcome_score

  # Normalize by outcome counts.
  expected_score /= num_outcomes

  return expected_score

# Avoid re-computing scenarios.
best_outcome = Memoize(best_outcome)

def scoring_strategies(dice):
  # TODO
  print dice
  yield (0, ())

# Print a situation, the correct decision for that situation,
# the score obtained by making that decision, and the loss incurred by following the
# heuristic instead.
def emit(key, choice, result):
  '''
  error = 0
  if heuristic(key) != choice:
    stand_score = key[0]
    if stand_score != result:
      error = math.fabs(result - stand_score) / stand_score
  '''
  print "%s\t%s\t%4f\t%4f" % (key, choice, result, error)

print "banked, hand, recommendation, score, importance"

best_outcome()
