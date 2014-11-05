'''
Classic 2-egg puzzle.
'''

from utils import Memoize

# Given a fixed number of eggs and drops, return the number of floors that can be covered.
def eggdrop(eggs, drops):
  if drops == 0 or eggs == 0: return 0
  return eggdrop(eggs-1, drops-1) + 1 + eggdrop(eggs, drops-1)
eggdrop = Memoize(eggdrop)

MAX_EGGS = 50
for e in range(MAX_EGGS):
  print 'eggdrop(%d, 100): %d' % (e, eggdrop(e, MAX_EGGS * 2))
