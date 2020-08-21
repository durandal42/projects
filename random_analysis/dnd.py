from distribution import *


def d20():
  return die(20)
assert 10.5 == d20().ev()


def highest(ds):
  return reduce(lambda d1, d2: d1.combine(d2, lambda x, y: max(x, y)), ds)


def lowest(ds):
  return reduce(lambda d1, d2: d1.combine(d2, lambda x, y: min(x, y)), ds)


def advantage(d=d20()):
  return highest([d, d])
assert 13.825 == float(advantage().ev())


def disadvantage(d=d20()):
  return lowest([d, d])
assert 7.175 == float(disadvantage().ev())

MISS = 0
HIT = 1
CRIT = 2


def monsterAC(cr):
  chart = [(4, 13),  (5, 14),  (8, 15),  (10, 16),
           (13, 17),  (17, 18), (99, 19)]
  return next(x for x in chart if cr < x[1])[1]


def attack(roll, modifier, ac):
  return switch(roll,
                [(lambda r: r == 20, CRIT),
                 (lambda r: r + modifier >= ac, HIT)])


def damage(result, hit_dmg, crit_dmg):
  return switch(result,
                [(lambda r: r == CRIT, hit_dmg + crit_dmg),
                 (lambda r: r == HIT, hit_dmg)])

NORMAL = 0
ADVANTAGE = 1
DISADVANTAGE = -1


def roll(adv):
  if adv >= ADVANTAGE:
    return advantage()
  if adv <= DISADVANTAGE:
    return disadvantage()
  return d20()

AC = 18


def bear(adv):
  return (damage(attack(roll(adv), 6, AC), die(8) + 4, die(8)) +
          damage(attack(roll(adv), 6, AC), dice(2, 6) + 4, dice(2, 6)))


def tiger(adv):
  first_hit = damage(attack(roll(adv), 5, AC), die(8) + 3, die(8))
  second_hit = damage(attack(roll(adv), 5, AC), die(10) + 3, die(10))
  return first_hit.map(lambda f: f + second_hit if f > 0 else 0)


def lightpaw(raging=False, reckless=False, gwm=False):
  return damage(attack(roll(ADVANTAGE if reckless else NORMAL), 5 if not gwm else 0, AC),
                dice(2, 6) + 3 + (2 if raging else 0) + (10 if gwm else 0),
                dice(2, 6))


# def lintilla():
#   return damage(attack(roll(ADVANTAGE), 7, AC),
#                 die(8)

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
                          dtuple(total + die(10),
                                 ifthenelse(die(2) == 1, ADVANTAGE, adv)),
                          dtuple(total, adv))
  return total

summarize(deinonychus())
'''
