'''
Generalization of the classic 2-egg puzzle.
'''

class Memoize:
  def __init__(self, f):
    self.f = f
    self.memo = {}
  def __call__(self, *args):
    if not args in self.memo:
      self.memo[args] = self.f(*args)
    return self.memo[args]

# Given a fixed number of eggs and drops, return the number of floors that can be covered.
def eggdrop(eggs, drops):
  if drops == 0 or eggs == 0: return 0
  return eggdrop(eggs-1, drops-1) + 1 + eggdrop(eggs, drops-1)
eggdrop = Memoize(eggdrop)

MAX_EGGS = 50
DROPS = MAX_EGGS
for e in range(MAX_EGGS+1):
  print 'eggdrop(%d, %d): %d' % (e, DROPS, eggdrop(e, DROPS))

print '2**%d = %d' % (MAX_EGGS, 2**MAX_EGGS)
