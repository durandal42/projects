BRANCH = 2
PARTY_SIZE = 4


def render_hydra(hydra, depth=0):
  result = "\t" * depth
  result += str(len(hydra))
  if len(hydra):
    result += ":\n"
    for head in hydra:
      result += render_hydra(head, depth + 1)
  else:
    result += "\n"
  return result


def chop(hydra, head_path):
  assert hydra  # never call chop on a headless hydra
  hi = head_path[0]
  if len(head_path) == 1:
    # we're chopping a head connected directly to the body
    assert not hydra[hi]  # can't chop heads with children
    return tuple(head for i, head in enumerate(hydra) if i != hi)
  elif len(head_path) > 2:
    # the chop is much further up the chain
    return tuple(i == hi and chop(hydra[i], head_path[1:]) or hydra[i]
                 for i in range(len(hydra)))
  elif len(head_path) == 2:
    # the interesting case; we need to spawn more heads
    head = hydra[hi]  # the head whose child will be chopped
    # print 'head whose child will be chopped:', head
    hi2 = head_path[1]
    # chop the head!
    head = tuple(h for i, h in enumerate(head) if i != hi2)
    # print 'head after chopping child:', head
    # ... and spawn two new copies of its parent
    hydra = tuple(h for i, h in enumerate(hydra)
                  if i != hi) + (head,) * (BRANCH + 1)
    # print 'hydra spawns new copies:', hydra
    return hydra
  assert False


def eligible_chops(hydra):
  result = []
  for i, head in enumerate(hydra):
    if head:
      ec = eligible_chops(head)
      for c in ec:
        result.append([i] + c)
    else:
      result.append([i])
  return result

import random


def shallow_chop(eligible_chops):
  return min((len(ec), ec) for ec in eligible_chops)[1]


def deep_chop(eligible_chops):
  return max((len(ec), ec) for ec in eligible_chops)[1]


def opportunistic_deep_chop(eligible_chops):
  return max((len(ec) == 1 and 100 or len(ec), -ec[-1], ec) for ec in eligible_chops)[-1]


def num_heads(hydra):
  if not hydra:
    return 0
  return len(hydra) + sum(num_heads(head) for head in hydra)


def complexity(hydra, depth=0, branch=BRANCH):
  if not hydra:
    return 0
  return sum((branch + 2)**complexity(head, depth + 1, branch) for head in hydra)


def defeat(hydra, f=random.choice, display=False):
  if display:
    print "attacking hydra using strategy %s..." % f.__name__
  chops = 0
  head_exposure = 0
  while hydra:
    if display:
      print 'hydra still lives after %d chops, with %d total heads and complexity %d:' % (chops, num_heads(hydra), complexity(hydra))
      if num_heads(hydra) < 40:
        print render_hydra(hydra)
    if chops % PARTY_SIZE == 0:
      head_exposure += num_heads(hydra)
    ec = eligible_chops(hydra)
    # print 'eligible chops:', ec
    c = f(ec)
    # print 'chosen chop:', c
    hydra = chop(hydra, c)
    chops += 1
  if display:
    print "hydra defeated after %d chops, suffering %d head exposure!" % (chops, head_exposure)
  return chops, head_exposure

import collections


def weighted_average(counter):
  value_sum = 0
  total_count = 0
  for v, c in counter.items():
    value_sum += v * c
    total_count += c
  return value_sum / float(total_count)


def sample_defeats(hydra, n=100):
  chop_counts = collections.Counter()
  exposure_counts = collections.Counter()
  for i in range(n):
    c, e = defeat(hydra)
    chop_counts[c] += 1
    exposure_counts[e] += 1
  return weighted_average(chop_counts), weighted_average(exposure_counts)

HYDRAS = [
    # (),
    ((),),
    (((),),),
    ((((),),),),
    # (((((),),),),),
    # ((), ((),), ((), ((),))),
    # (((), (), ()),),
]
STRATEGIES = [
    shallow_chop,
    deep_chop,
    opportunistic_deep_chop
]
for h in HYDRAS:
  print render_hydra(h)
  for s in STRATEGIES:
    print defeat(h, f=s, display=False), s.__name__
  print sample_defeats(h), "random.choice"
