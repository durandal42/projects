import utils
import fractions

## GENERAL HELPER STUFF ###

def mark_done(state):  # helper to mark a state as done
  return (True,) + state[1:]

def single_outcome(state):
  return {state:1}

def score_outcomes(states, score_state=lambda state: 0):
  num_states = sum(states.values())
  assert num_states > 0
  return fractions.Fraction(sum(score_state(state)*frequency
                                for state,frequency in states.iteritems()),
                            num_states)

@utils.memoized
def best_outcome(state):
  if state[0]: return state[1]  # already done

  best_score, best_choice = max((score_outcomes(outcomes, SCORER), choice)
                                for choice, outcomes in CHOOSER(state))
  print "%s\t%s\t%4f" % (state, best_choice, best_score)
  return best_score

### GAME SPECIFIC STUFF - OVERRIDE THESE ###

def start_state():  # starting state of the game
  return None

def choices(state):
  yield ('FLIP_TABLE',
         {(
           True,  # game is over
           None   # other game state
           ):1})

def score_state(state):
  if not state[0]:  # if we can still act...
    return best_outcome(state)  # ... recurse on all possible choices.
  return state[1]  # assume current score is in state[1]

SCORER = score_state
CHOOSER = choices