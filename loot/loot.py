import random

LOOT_CLASSES = 6
# handwaving here; assume each player wants loot from only one of the following sets
# armor(7): cloth, {agi,int} leather, {agi,int} mail, {dps,tanky} plate
# weapons(6): caster, healer, melee agi, ranged, 1h str, 2h str
# trinkets(5): caster, healer, agi dps, str dps, tanky
RAID_SIZE = 25
LOOT_CLASS_CONTENTION = {
  0:3,
  1:4,
  2:5,
  3:6,
  4:7,
}

LOOT_SLOTS = 14

OLD_SYSTEM_LOOTS_PER_BOSS = 4
NEW_SYSTEM_CHANCE_OF_LOOT = 0.16

def make_naked_raid():
  result = []
  for loot_class,num in LOOT_CLASS_CONTENTION.iteritems():
    for i in range(num):
      result.append((loot_class, [False]*LOOT_SLOTS))
  return result

def loot_saturation(raid, class_filter=None):
  if class_filter is not None:
    raid = [r for r in raid if r[0] == class_filter]
  total_slots = sum([len(r[1]) for r in raid])
  equipped = sum([len([l for l in r[1] if l]) for r in raid])
  return float(equipped) / float(total_slots)

def old_system(raid, greedy=0.0):
  num_sharded = 0
  num_equipped = 0
  for i in xrange(OLD_SYSTEM_LOOTS_PER_BOSS):
    loot_class = random.choice(LOOT_CLASS_CONTENTION.keys())
    loot_slot = random.choice(range(LOOT_SLOTS))

    eligible_raiders = [r for r in raid if r[0] == loot_class and (random.random() < greedy or
                                                                   not r[1][loot_slot])]
    if eligible_raiders:
      # pick a winner
      winner = random.choice(eligible_raiders)
      # equip the loot
      winner[1][loot_slot] = True
      num_equipped += 1
    else:
      num_sharded += 1
  return num_equipped,num_sharded

def new_system(raid):
  num_equipped,num_duplicates = 0,0
  for r in raid:
    if random.random() < NEW_SYSTEM_CHANCE_OF_LOOT:
      loot_slot = random.choice(range(LOOT_SLOTS))
      if r[1][loot_slot]:
        num_duplicates += 1
      else:
        r[1][loot_slot] = True
        num_equipped += 1
  return num_equipped,num_duplicates

def raid_until_saturation(allocate_functions):
  classes_to_consider = [min(LOOT_CLASS_CONTENTION.keys()), max(LOOT_CLASS_CONTENTION.keys())]
  raids = [make_naked_raid() for a in allocate_functions]

  print "kills",
  for i in range(len(allocate_functions)):
    print "\tsaturation%d" % i,
    for loot_class in classes_to_consider:
      print "\tsaturation%d:%d" % (i, loot_class),
  print

  num_bosses = 0
  while max([loot_saturation(r) for r in raids]) < .95:
    num_bosses += 1
    print num_bosses,
    for raid,allocate in zip(raids, allocate_functions):
      allocate(raid)
      print "\t%f" % loot_saturation(raid),
      for loot_class in classes_to_consider:
        print "\t%f" % loot_saturation(raid, loot_class),
    print

raid_until_saturation([lambda r: old_system(r, 0.0),
                       lambda r: old_system(r, 0.5),
                       lambda r: old_system(r, 1.0),
                       new_system])
