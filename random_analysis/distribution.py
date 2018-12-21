import fractions
import collections
import operator

class Distribution:
  def __init__(self, dist=None):
    if dist is None:
      self._dist = collections.defaultdict(fractions.Fraction)
    else:
      self._dist = dist

  def __repr__(self):
    if not self._dist: return "Distribution()"
    return "Distribution(\n\t%s\n)" % (",\n\t".join("%s:\t%s" % item for item in self._dist.iteritems()))

  HISTOGRAM_WIDTH = 50
  def __str__(self):
    if not self._dist: return "Distribution()"
    max_p = max(self._dist.values())
    return "Distribution(\n\t%s\n)" % ("\n\t".join("%s:\t%0.4f - [%s]" % (x,px,"*"*int(Distribution.HISTOGRAM_WIDTH*px/max_p))
                                       for x,px in sorted(self._dist.iteritems())))

  def equivalent(left, right):
    if isinstance(left, Distribution):
      left = left._dist
    if isinstance(right, Distribution):
      right = right._dist
    if isinstance(left, dict) and isinstance(right, dict):
      keys = set(left.keys()) | set(right.keys())
      for x in keys:
        if not left.get(x,0) == right.get(x,0): return False
      return True
    return False

  def combine(self, other, operator):
    result = collections.defaultdict(fractions.Fraction)
    for x, px in self._dist.iteritems():
      if isinstance(other, self.__class__):
        for y, py in other._dist.iteritems():
          result[operator(x, y)] += px * py
      else:
        result[operator(x, other)] += px
    return self.__class__(result)

  def map(self, operator):
    # print "mapping:", self, operator
    result = collections.defaultdict(fractions.Fraction)
    for x, px in self._dist.iteritems():
      mapped = operator(x)
      # print 'mapped:', mapped
      if isinstance(mapped, self.__class__):
        for y, py in mapped._dist.iteritems():
          result[y] += px * py
      else:
        result[mapped] += px
    # print 'map complete:', result
    return self.__class__(result)

  def ev(self):
    return sum(x * px for x, px in self._dist.iteritems())

  def __add__(self, other):
    return self.combine(other, operator.__add__)
  def __radd__(self, other):
    return self + other

  def __sub__(self, other):
    return self.combine(other, operator.__sub__)
  def __rsub__(self, other):
    return self.combine(other, lambda x,y: y-x)

  def __mul__(self, other):
    return self.combine(other, operator.__mul__)
  def __rmul__(self, other):
    return self + other

  def __eq__(self, other):
    return self.combine(other, operator.__eq__)
  def __lt__(self, other):
    return self.combine(other, operator.__lt__)
  def __le__(self, other):
    return self.combine(other, operator.__le__)
  def __gt__(self, other):
    return self.combine(other, operator.__gt__)
  def __ge__(self, other):
    return self.combine(other, operator.__ge__)

  # def mktuple(self, other):
  #   return self.combine(other, lambda x,y: (x,y))

  def __nonzero__(self):
    for x, px in self._dist.iteritems():
      if not x: return False
    return True


def die(size):
  return Distribution(dict((i+1, fractions.Fraction(1, size))
                       for i in range(size)))

def dice(num, size):
  return sum(die(size) for _ in range(num))

def ifthenelse(condition, iftrue, iffalse):
  return condition.map(lambda x: x and iftrue or iffalse)

def ifthen(condition, iftrue):
  return ifthenelse(condition, iftrue, 0)

def switch_f(x, condition_result_list):
  for condition,result in condition_result_list:
    if condition(x): return result
  return 0
def switch(input, condition_result_list):
  return input.map(lambda x: switch_f(x, condition_result_list))

# basic combinations
assert Distribution.equivalent(die(6), dict((i, fractions.Fraction(1,6)) for i in range(1,7)))
assert Distribution.equivalent(die(6)+3, dict((i+3, fractions.Fraction(1,6)) for i in range(1,7)))
assert Distribution.equivalent(die(6)+3, 3+die(6))
assert Distribution.equivalent(dice(2,6), die(6) + die(6))
assert Distribution.equivalent(dice(2,2), {2:fractions.Fraction(1,4), 3:fractions.Fraction(2,4), 4:fractions.Fraction(1,4)})
assert Distribution.equivalent(die(2) - die(2), die(2)+die(2) - 3)
assert Distribution.equivalent(1 - die(2), die(2) - 2)
assert Distribution.equivalent(die(2) * die(2), {1:fractions.Fraction(1,4), 2:fractions.Fraction(2,4), 4:fractions.Fraction(1,4)})

# expected value
assert 6.5 == die(12).ev()
assert 7 == dice(2,6).ev()
assert 19.5 == (die(8)+4+dice(2,6)+4).ev()


# boolean magic
assert Distribution.equivalent(die(6) == 3, {True:fractions.Fraction(1,6), False:fractions.Fraction(5,6)})

def d20():
  return die(20)
assert 10.5 == d20().ev()

def advantage(d=d20()):
  return d.combine(d, lambda x,y: max(x,y))
assert 13.825 == float(advantage().ev())

def disadvantage(d=d20()):
  return d.combine(d, lambda x,y: min(x,y))
assert 7.175 == float(disadvantage().ev())

MISS = 0
HIT = 1
CRIT = 2
def attack(roll, modifier, ac):
  return switch(roll,
                [(lambda r: r==20, CRIT),
                 (lambda r: r + modifier >= ac, HIT)])

def damage(result, hit_dmg, crit_dmg):
  return switch(result,
                [(lambda r: r==CRIT, hit_dmg+crit_dmg),
                 (lambda r: r==HIT, hit_dmg)])

NORMAL = 0
ADVANTAGE = 1
DISADVANTAGE = -1

def roll(adv):
  if adv >= ADVANTAGE: return advantage()
  if adv <= DISADVANTAGE: return disadvantage()
  return d20()

AC = 18
def bear(adv):
  return (damage(attack(roll(adv), 6, AC), die(8)+4, die(8)) +
          damage(attack(roll(adv), 6, AC), dice(2,6)+4, dice(2,6)))

def tiger(adv):
  first_hit = damage(attack(roll(adv), 5, AC), die(8)+3, die(8))
  second_hit = damage(attack(roll(adv), 5, AC), die(10)+3, die(10))
  return first_hit.map(lambda f: f+second_hit if f>0 else 0)


def lightpaw(raging=False, reckless=False, gwm=False):
  return damage(attack(roll(ADVANTAGE if reckless else NORMAL), 5 if not gwm else 0, AC),
                dice(2,6) + 3 + (2 if raging else 0) + (10 if gwm else 0),
                dice(2,6))

def lintilla():
  return damage(attack(roll(ADVANTAGE), 7, AC),
                die(8)

def summarize(d):
  print d, float(d.ev())

# summarize(bear(NORMAL))
# summarize(bear(ADVANTAGE))
# summarize(tiger(NORMAL))

'''
for raging in [False, True]:
  for reckless in [False, True]:
    print "raging, reckless:", raging, reckless
    for AC in range(10,20):
      gwm = lightpaw(raging, reckless, True).ev()
      nogwm = lightpaw(raging, reckless, False).ev()
      print AC, ("gwm" if gwm>nogwm else "nogwm")
#      for gwm in [False, True]:
#        print "raging, reckless, gwm: %s, %s, %s" % (raging, reckless, gwm)
#        summarize(lightpaw(raging, reckless, gwm))
'''

'''
def dtuple(d1, d2):
  if not isinstance(d1, Distribution): d1 = Distribution({d1:1})
  if not isinstance(d2, Distribution): d2 = Distribution({d2:1})
  print d1, d2
  return d1.combine(d2, lambda x,y: (x,y))

def deinonychus():
  total, adv = 0, NORMAL
#  total, adv = 
  print ifthenelse(roll(adv) > AC,
                          dtuple(total + die(10), ifthenelse(die(2) == 1, ADVANTAGE, adv)),
                          dtuple(total, adv))
  return total

summarize(deinonychus())
'''
