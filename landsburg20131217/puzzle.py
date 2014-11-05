'''
Landsburg puzzle:

Here I have a well shuffled deck of 52 cards, half of them red and half of them
black. I plan to slowly turn the cards face up, one at a time. You can raise
your hand at point any either just before I turn over the first card, or the
second, or the third, et cetera. When you raise your hand, you win a prize if
the next card I turn over is black. What's your strategy?
'''

from fractions import Fraction
from utils import Memoize

'''
Given how many blacks and reds are known to remain in the deck, what's the best
odds of winning we can manage?

Recursively consider possible worlds in which we draw a red or a black, weight
them accordingly, and compare against stopping immediately.
'''
def max_chance(blacks, reds):
  stand = Fraction(blacks, blacks + reds)  # if we stop now, the odds are simple
  if not blacks or not reds:
      # if the deck is now monochrome, we can no longer affect the outcome
      return stand
  draw = (stand * max_chance(blacks - 1, reds) +
          (1 - stand) * max_chance(blacks, reds - 1))
  print '%d\t%d\t%s\t%s\t' % (blacks, reds, stand, draw),
  if draw == stand: print 'TIE'
  if draw > stand: print 'DRAW'
  if draw < stand: print 'STAND'
  return max(stand, draw)

max_chance = Memoize(max_chance)

print 'blacks\treds\tstand\tdraw\tchoice'
print max_chance(26, 26)

'''
Consider the following strategy:
"Draw cards until more blacks than reds remain, then stop."

If we ever stop, we'll have a >50% chance of success at that point.
However, we might exhaust the deck before that happens, in which case we fail.

Compute the chance of failure of this strategy.
'''
def chance_of_failure(blacks, reds):
  if blacks > reds: return 0
  if not blacks: return 1
  proportion_black = Fraction(blacks, blacks + reds)
  return (proportion_black * chance_of_failure(blacks-1, reds) +
      (1-proportion_black) * chance_of_failure(blacks, reds-1))
chance_of_failure = Memoize(chance_of_failure, display=True)
print chance_of_failure(26, 26)
