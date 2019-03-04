import fractions
import random
class RNG:
  def die(self, size):
    return random.randint(1,size)
  def dice(self, num, size):
    return sum(self.die(size) for _ in range(num))
  def coin(self, weight=fractions.Fraction(1,2)):
    return self.die(weight.denominator) <= weight.numerator
  def choose(self, list):
    return list[self.die(len(list)) - 1]
  def improbability(self):
    return 1
  def next(self):
    return True

def die(size):
  return lambda r: r.die(size)

def dice(num, size):
  return lambda r: r.dice(num, size)

class SamplingRNG(RNG):
  def __init__(self, num_samples):
    self.num_samples = num_samples
    self.samples_remaining = num_samples
  def improbability(self):
    return self.num_samples
  def next(self):
    self.samples_remaining -= 1
    return self.samples_remaining > 0

class ExploringRNG(RNG):
  def __init__(self):
    self._choices = []
    self._options = []
    self._improbability = 1
    self._index = 0  # TODO(durandal): max index to stop DFS blowout

  def die(self, size):
    if self._index < len(self._options):
      assert self._options[self._index] == size
    else:
      self._options.append(size)

    if self._index < len(self._choices):
      assert self._choices[self._index] < size
      result = self._choices[self._index]
    else:
      result = 0
      self._choices.append(result)

    self._index += 1
    self._improbability *= size

    return result + 1

  def coin(self, weight=fractions.Fraction(1,2)):
    result = (self.die(2) == 1)
    if weight < fractions.Fraction(1,2): result = not result
    # adjust improbability
    self._improbability /= 2
    if result:
      self._improbability /= weight
    else:
      self._improbability /= 1 - weight
    return result

  def improbability(self):
    return self._improbability

  def next(self):
    assert self._index == len(self._choices)
    assert self._index == len(self._options)
#    print self._choices
#    print self._options
#    print
    while self._choices:
      self._choices[-1] += 1
      if self._choices[-1] == self._options[-1]:
        self._choices.pop()
        self._options.pop()
      else:
        break
    if not self._choices: return False
    self._index = 0
    self._improbability = 1
    return True

def is_power2(num):
  'states if a number is a power of two'
  return num != 0 and ((num & (num - 1)) == 0)

import collections
import itertools
def histogram(f, r=None):
  if r is None: r = ExploringRNG()
  results = collections.defaultdict(fractions.Fraction)
  mass = fractions.Fraction()
  for i in itertools.count(1):
    outcome = f(r)
    probability = fractions.Fraction(1, r.improbability())
    mass += probability
    if is_power2(i):
      print 'result #%d:\t%s (%s);\tprogress: %0.4f' % (i, outcome, probability, mass)
    results[outcome] += probability
    if not r.next(): break

  print 'number of leaf outcomes:', i
  return results

def summarize(f, r=None):
  h = histogram(f, r)
  print 'summary:'
  for outcome, probability in sorted(h.iteritems()):
    print '%s\t%5.2f%%\t%s' % (outcome, round(100*probability, 2), probability)
  try: 
    ev = sum(outcome*probability for outcome,probability in h.iteritems())
    print 'expected value:\t%0.4f' % ev
    print '-'*20
    return ev
  except TypeError:
    return None

def vanilla_2d6(r):
  return r.dice(2,6)

def sicherman_2d6(r):
  return r.choose([1,2,2,3,3,4]) + r.choose([1,3,4,5,6,8])

def recast_2d6(r): 
  return r.die(3) + r.choose([1,2,3,4,4,5,5,6,6,7,8,9])

def d20(r):
  return r.die(20)
def advantage(r):
  return max(r.die(20), r.die(20))
def disadvantage(r):
  return min(r.die(20), r.die(20))

MISS = 0
HIT = 1
CRIT = 2
def attack(r, roll, modifier, ac):
  roll = roll(r)
  if roll == 1: return MISS
  if roll == 20: return HIT # can't crit, for now
  if roll + modifier >= ac: return HIT
  return MISS

def damage(r, result, hit_dmg, crit_dmg):
  if result == CRIT: return hit_dmg(r) + crit_dmg(r)
  if result == HIT: return hit_dmg(r)
  return 0

NORMAL = 0
ADVANTAGE = 1
DISADVANTAGE = -1

def roll(adv):
  if adv >= ADVANTAGE: return advantage
  if adv <= DISADVANTAGE: return disadvantage
  return d20

AC = 14
def bear(r, adv):
  return (damage(r, attack(r, roll(adv), 6, AC),
                 lambda r: r.die(8)+4,
                 lambda r: r.die(8)) +
          damage(r, attack(r, roll(adv), 6, AC),
                 lambda r: r.dice(2,6)+4,
                 lambda r: r.dice(2,6))
          )

'''
function: wolf at ADV:n :
  return [damage [attack [roll at ADV] plus 5 vs AC] for 2d6+3 crit 2d6]


FAILED:0
SAVED:1
function: save ROLL:n vs THRESHOLD:n :
  if ROLL >= THRESHOLD : return SAVED 
  return FAILED


function: tigerhelp CLAW:n save SAVE:n at ADV:n :
  DAMAGE: 0
  DAMAGE: DAMAGE + [damage CLAW for 1d8+3 crit 1d8]
  if CLAW != MISS :
    if SAVE = FAILED :
      ADV: ADV + ADVANTAGE
      DAMAGE: DAMAGE + [damage [attack [roll at ADV] plus 5 vs AC] for 1d10+3 crit 1d10]
    
  
  return DAMAGE

function: tiger at ADV:n :
  return [tigerhelp [attack [roll at ADV] plus 5 vs AC] save [save d20 vs 13] at ADV]


AC:14
output [bear at NORMAL] named "bear ()"
output [bear at ADVANTAGE] named "bear (advantage)"
output [wolf at ADVANTAGE] named "wolf (pack tactics)"
output [tiger at NORMAL] named "tiger (pounce)"
output [tiger at ADVANTAGE] named "tiger (pounce, advantage)"
'''

def cardchoose(rng, n, k):
  t = n - k + 1
  d = [None] * k
  for i in range(k):
    r = rng.die(t + i) - 1
    if r < t:
      d[i] = r
    else:
      d[i] = d[r - t]
  d.sort()
  for i in range(k):
    d[i] += i
  return tuple(d)

def krs_choose(rng, n, k):
  d = []
  needed = k
  left = n
  for i in range(n):
    r = rng.die(left)-1
    if r < needed:
      d.append(i)
      needed -= 1
    left -= 1
    if left < 1: break
  return tuple(d)

def okimhere(rng, payoff=36, house_edge=fractions.Fraction(2,38)):
  funds, target = 1, 2
  while funds > 0 and funds < target:
    bet = min(funds, fractions.Fraction(target-funds, payoff-1))
    funds -= bet
    if rng.coin((1-house_edge) * fractions.Fraction(1,payoff)):
      funds += bet * payoff
  return funds

def black(rng):
  if rng.coin(fractions.Fraction(18,38)): return 2
  else: return 0

functions = [
#  vanilla_2d6,
#  sicherman_2d6,
#  recast_2d6,
#  disadvantage,
#  d20,
#  advantage,
#  lambda r: bear(r, NORMAL),
#  lambda r: bear(r, ADVANTAGE),
#  lambda r: cardchoose(r, 8, 3),
#  lambda r: krs_choose(r, 8, 3),
#  black,
  lambda r: okimhere(r, 2),
  lambda r: okimhere(r, 4),
  lambda r: okimhere(r, 8),
  lambda r: okimhere(r, 16),
  lambda r: okimhere(r, 32),
]

if __name__ == "__main__":
  # execute only if run as a script
  for f in functions:
    print f
    summarize(f,
              r=SamplingRNG(10 ** 6)
  #            r=ExploringRNG()
          )