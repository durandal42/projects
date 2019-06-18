from distribution import *

def nyctala(sneak=2, dex=3, prof=2,
            advantage=True,
            elven_accuracy=False, archery=False, sharpshooter=False):
  attack_die = roll(advantage)
  if advantage and elven_accuracy:
    attack_die = highest([d20(), d20(), d20()])
  return damage(attack(attack_die, dex + prof
                       + (2 if archery else 0)
                       + (-5 if sharpshooter else 0),
                       AC),
                die(8) + dex + (10 if sharpshooter else 0) + dice(sneak, 6),
                die(8) + dice(sneak, 6))


def summarize(d):
  print d, float(d.ev())

summarize(nyctala())

def compare_ea_vs_dex(sneak, AC):
  ea_adv = (nyctala(sneak=sneak, dex=3, elven_accuracy=True).ev() -
            nyctala(sneak=sneak, dex=4, elven_accuracy=False).ev())
  ea_noadv = (nyctala(sneak=sneak, dex=3, advantage=False).ev() -
              nyctala(sneak=sneak, dex=4, advantage=False).ev())
  p = ea_noadv / (ea_noadv - ea_adv)
  if float(p) >= 1:
    conclusion = "EA always worse"
    print "[" + " " * 100 + "]"
  else:
    conclusion = "EA better when at advantage >= %.0f%%" % float(100 * p)
    print "[" + " " * int(100 * p) + "*" * (100 - int(100 * p)) + "]"
  print "%dd6 SA vs %02d AC: %s" % (sneak, AC, conclusion)

def compare_ss(sneak, AC, elven_accuracy, archery=False):
  ss = nyctala(sneak=sneak, elven_accuracy=elven_accuracy,
               archery=archery, sharpshooter=True).ev()
  noss = nyctala(sneak=sneak, elven_accuracy=elven_accuracy,
                 archery=archery, sharpshooter=False).ev()
  print "\t%d\t%d\t%s\t%s" % (sneak, AC, ("ss" if ss > noss else "noss"), float(ss - noss))

def sneak_dice(level):
  return (level+1)/2

def likely_ac(level):
  ac_by_level = monsterAC(level)
  return range(ac_by_level - 5, ac_by_level + 6)

def circumstances_by_level_range(levels):
  for l in levels:
    for ac in likely_ac(l):
      yield (l, sneak_dice(l), ac)

for level, sneak, AC in circumstances_by_level_range(range(1,13)):
  compare_ea_vs_dex(sneak, AC)
  # pass

for elven_accuracy in [False, True]:
  print "elven_accuracy: ", elven_accuracy
  print "\tlevel, sneak, AC, judgment, delta"
  for level, sneak, AC in circumstances_by_level_range(range(1,13)):
    print "\t", level,
    compare_ss(sneak, AC, elven_accuracy)
  print
