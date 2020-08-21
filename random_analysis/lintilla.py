from random_analysis import *
from dnd import *

import re

R = RNG()


def roll(expr, crit=False):
  d = re.compile('(\d*)d(\d+)(v|\\^)?')
  while True:
    m = d.search(expr)
    if not m:
      break
    num_dice = int(m.group(1) or 1)
    if crit:
      num_dice *= 2
    die_size = int(m.group(2))
    adv = m.group(3)
    rolled = expand_roll(num_dice, die_size)
    if adv:
      rolled_again = expand_roll(num_dice, die_size)
      rolled = '%s(%s, %s)' % (
          {'v': 'min', '^': 'max'}[adv], rolled, rolled_again)
    expr = d.sub(rolled, expr, count=1)
  print '=', expr
  return eval(expr)


def expand_roll(n, d):
  rolled = [R.die(d) for i in range(n)]
  if len(rolled) > 1:
    sub = '(%s)' % '+'.join(str(r) for r in rolled)
  elif not rolled:
    sub = '0'
  else:
    sub = str(rolled[0])
  return sub


def init(dex=-1):
  print roll('d20 + %d' % dex)


def skill(bonus, dc):
  total = roll('d20 + %d' % bonus)
  print total
  print '- vs %d' % dc
  success = total >= dc
  print success and "SUCCESS" or "FAILURE"


def skill_contest(offense_bonus, defense_bonus):
  offense_total = roll('d20 + %d' % offense_bonus)
  print offense_total
  print '- vs -'
  defense_total = roll('d20 + %d' % defense_bonus)
  print defense_total
  success = offense_total > defense_total
  print success and "SUCCESS" or "FAILURE"


def lint_shove(defender_bonus):
  return skill_contest(21, defender_bonus)


def attack(target_ac, attack_bonus, adv='', crit_threshold=20):
  r = roll('d20%s + %d' % (adv, attack_bonus))
  if r - attack_bonus >= crit_threshold:
    print "CRITICAL HIT"
    return
  if r - attack_bonus == 1:
    print "CRITICAL MISS"
    return
  # print 'neither crit nor crit fail'
  success = r >= target_ac
  print '%d vs %d' % (r, target_ac)
  print success and "HIT" or "MISS"


def lint_attack(target_ac, adv=''):
  return attack(target_ac, 16, crit_threshold=19, adv=adv)


def lint_damage(crit=False, hw=False):
  print roll('d8+10', crit), 'slashing'
  print roll('%dd8' % (hw and 3 or 1), crit), 'radiant'


def smite(n, crit=False):
  print roll('%dd8' % n, crit), 'radiant'
