import utils
import math
import collections
import fractions

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

def start_state():
  done = False
  accumulated_score = 0
  blams = (0,0,0)
  brains = (0,0,0)
  hand = (0,0,0)
  cup = (NUM_GREENS, NUM_YELLOWS, NUM_REDS)
  return (done, accumulated_score, blams, brains, hand, cup)

def verify_state(state):
  done, accumulated_score, blams, brains, hand, cup = state
  assert (sum(blams) + sum(brains) + sum(hand) + sum(cup)
          == NUM_GREENS + NUM_YELLOWS + NUM_REDS)

def mark_done(state):
  return (True,) + state[1:]

def single_outcome(state):
  return {state:1}

def choices(state):
  if state[0]: return  # already done

  yield ('STAND', single_outcome(mark_done(state)))
  if STOP_FUNCTION(state[1]): return # Assumes you stand once reaching MAX_BRAINS.

  done, accumulated_score, blams, brains, hand, cup = state

  roll_outcomes = collections.Counter()

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

  for draw, draw_frequency in draws.iteritems():
    # Given a draw, compute all possible roll outcomes:
    outcomes = utils.cross_counted(
      DIE_GREEN * (hand[GREEN] + draw[GREEN]) +
      DIE_YELLOW * (hand[YELLOW] + draw[YELLOW]) +
      DIE_RED * (hand[RED] + draw[RED]),
      combine_roll)

    num_outcomes = sum(outcomes.values())
    for outcome, outcome_frequency in outcomes.iteritems():
      outcome_blams, outcome_brains, outcome_feet = outcome

      new_state = (False, accumulated_score + sum(outcome_brains),
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

      if sum(new_state[2]) >= MAX_BLAMS:
        new_state = (True, 0) + new_state[2:]  # too many BLAMS; 0 points and done.

      if new_state == state:
        # This would result in a recursive call to evaluate exactly the same 
        # position we were just in. Because math, dropping this outcome entirely works.
        continue

      roll_outcomes[new_state] += draw_frequency * outcome_frequency

  yield ('ROLL', roll_outcomes)

def score_outcomes(states):
  num_states = sum(states.values())
  assert num_states > 0
  return fractions.Fraction(sum(score_state(state)*frequency
                                for state,frequency in states.iteritems()),
                            num_states)

def score_state(state):
  if not state[0]: return best_outcome(state)
  else: return state[1]

def best_outcome(state=start_state()):
  verify_state(state)
  if state[0]: return state[1]  # already done

  best_score, best_choice = max((score_outcomes(outcomes), choice)
                                for choice, outcomes in choices(state))
  emit(state, best_choice, best_score)
  return best_score

# Avoid re-computing scenarios.
best_outcome = utils.Memoize(best_outcome)

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
  done, score, blams_by_color, brains_by_color, hand, cup = key
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
    stand_score = key[1]
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

UTILITY, STOP_FUNCTION = threshold(5)

best_outcome()
