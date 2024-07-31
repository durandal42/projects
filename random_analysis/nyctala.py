from distribution import *
from dnd import *

def sneak_dice(level):
  return math.floor((level + 1) / 2)

def nyctala(level=3, dex=4,
            advantage=True, ac=15,
            elven_accuracy=False, archery=False, sharpshooter=False,
            poison=True):
  sneak = sneak_dice(level)
  prof = (level-1) // 4 + 2
  attack_die = roll(advantage)
  if advantage and elven_accuracy:
    attack_die = highest([d20(), d20(), d20()])
  to_hit = attack(attack_die, dex + prof
                  + (2 if archery else 0)
                  + (-prof if sharpshooter else 0),
                  ac)
  #print("Chance to hit:", to_hit)
  return damage(to_hit,
                die(8) + dex
                + (2*prof if sharpshooter else 0)
                + dice(sneak, 6)
                + (dice(3,4) if poison else 0), # on hit
                die(8)
                + dice(sneak, 6)
                + (dice(3,4) if poison else 0)
                ) # on crit


# summarize(nyctala())


def compare_ea_vs_dex(level, ac):
  ea_adv = (nyctala(level=level, dex=3, ac=ac, elven_accuracy=True).ev() -
            nyctala(level=level, dex=4, ac=ac, elven_accuracy=False).ev())
  ea_noadv = (nyctala(level=level, dex=3, ac=ac, advantage=False).ev() -
              nyctala(level=level, dex=4, ac=ac, advantage=False).ev())
  p = ea_noadv / (ea_noadv - ea_adv)
  if float(p) >= 1:
    conclusion = "EA always worse"
    print("[" + " " * 100 + "]")
  else:
    conclusion = "EA better when at advantage >= %.0f%%" % float(100 * p)
    print("[" + " " * int(100 * p) + "*" * (100 - int(100 * p)) + "]")
  print("%dd6 SA vs %02d AC: %s" % (level, AC, conclusion))


def compare_ss(level, AC, elven_accuracy, archery=False):
  noss = nyctala(level=level, ac=ac, elven_accuracy=elven_accuracy,
                 archery=archery, sharpshooter=False)
  ss = nyctala(level=level, ac=ac, elven_accuracy=elven_accuracy,
               archery=archery, sharpshooter=True)
  print("\t%d\t%d\t%s\t%s" %
        (level, AC, ("ss" if ss.ev() > noss.ev() else "noss"), float(ss.ev() - noss.ev())))
  #summarize(noss)
  #summarize(ss)


def likely_ac(level):
  ac_by_level = monsterAC(level)
  return range(ac_by_level - 5, ac_by_level + 6)


def circumstances_by_level_range(levels):
  for l in levels:
    for ac in likely_ac(l):
      yield (l, ac)


'''
for level, AC in circumstances_by_level_range(range(1, 13)):
  compare_ea_vs_dex(level, AC)
  # pass

for elven_accuracy in [False, True]:
  print "elven_accuracy: ", elven_accuracy
  print "\tlevel, AC, judgment, delta"
  for level, AC in circumstances_by_level_range(range(1, 13)):
    print "\t", level,
    compare_ss(level, AC, elven_accuracy)
  print
'''

print("\tLevel\tAC\tss?\tdelta")
for level, ac in circumstances_by_level_range(range(1,20,2)):
  compare_ss(level, ac, elven_accuracy=True)
