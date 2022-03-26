import pointbuy
import random
import distribution
import math
import collections


def sample(dist, n):
  for _ in range(n):
    yield dist.choice(random.random())


print("Computing all pointbuy-legal stat arrays...")
pointbuy_legal = pointbuy.stat_array(
    lambda: distribution.die(8) + 7,
    sort=False).filter(lambda a: pointbuy.array_pointbuy_cost(a) == 27)

print("Number of pointbuy-legal stat arrays:", len(pointbuy_legal))

STAT_WEIGHTS_BY_CLASS = {
    "Artificer": (0, 7, 3, 5, 2, 0),
    "Barbarian": (6, 2, 3, 0, 2, 0),
    "Bard": (0, 2, 3, 1, 2, 6),
    "Bard(Valor)": (0, 7, 3, 1, 2, 6),
    "Cleric(Heavy)": (1, 1, 3, 1, 7, 1),
    "Cleric(Medium)": (0, 2, 3, 1, 7, 1),
    "Druid": (0, 2, 3, 1, 7, 0),
    "Fighter(DEX EK)": (0, 7, 3, 5, 2, 0),
    "Fighter(DEX)": (0, 7, 2, 0, 2, 0),
    "Fighter(STR EK)": (7, 1, 4, 5, 2, 0),
    "Fighter(STR)": (7, 1, 3, 0, 2, 0),
    "Monk": (0, 7, 3, 1, 6, 0),
    "Paladin": (7, 1, 4, 0, 2, 6),
    "Ranger(DEX)": (0, 7, 3, 1, 2, 1),
    "Ranger(STR)": (6, 2, 4, 1, 2, 1),
    "Rogue(AT)": (0, 8, 3, 6, 2, 1),
    "Rogue(non-AT)": (0, 8, 2, 1, 2, 1),
    "Sorcerer": (0, 2, 3, 1, 2, 5),
    "Warlock": (0, 2, 3, 1, 2, 5),
    "Wizard": (0, 2, 3, 6, 2, 0),
}

RACIAL_BONUS_INDICES = distribution.die(6).product(
    distribution.die(6)).filter(lambda x: x[0] != x[1])
# print(RACIAL_BONUS_INDICES)


def pick_racials(stats, weights):
  best_stats = None
  best_score = -100
  for bonuses, _ in RACIAL_BONUS_INDICES.items():
    plus_two, plus_one = bonuses
    stats_after_racials = list(stats)
    stats_after_racials[plus_two - 1] += 2
    stats_after_racials[plus_one - 1] += 1
    stats_after_racials = tuple(stats_after_racials)
    score = score_array(stats_after_racials, weights)
    best_score, best_stats = max(
        (best_score, best_stats), (score, stats_after_racials))
  return best_stats


def score_array(stats, weights):
  return sum((math.floor(stat/2)-5) * weight
             for stat, weight in zip(stats, weights))


BUCKET_BOUNDARIES_BY_CLASS = {}
for c, weights in STAT_WEIGHTS_BY_CLASS.items():
  print()
  print(c)
  stat_lines = pointbuy_legal.map(lambda x: pick_racials(x, weights))
  scores = stat_lines.map(lambda x: score_array(x, weights))
  distribution.summarize(scores)

  print("score distribution:")
  stats_and_scores = sorted([(score_array(stats, weights), stats)
                             for stats, p in stat_lines.items()])

  print("best statline: ", stats_and_scores[-1])
  print("worst statline:", stats_and_scores[0])
  n = len(stats_and_scores)
  NUM_BUCKETS = 100
  bucket_boundaries = [stats_and_scores[math.floor(n * p / NUM_BUCKETS)][0]
                       for p in range(NUM_BUCKETS)]
  print("percentile boundaries:", bucket_boundaries)
  BUCKET_BOUNDARIES_BY_CLASS[c] = bucket_boundaries


def assign_percentile(value, bucket_boundaries):
  for i, bucket_boundary in enumerate(bucket_boundaries):
    if bucket_boundary > value:
      return i
  return len(bucket_boundaries)


print("\n16 random pointbuy-legal statlines:")
for stats in sample(pointbuy_legal, 16):
  print(stats)
  evaluation = sorted([(assign_percentile(score_array(pick_racials(stats, weights),
                                                      weights),
                                          BUCKET_BOUNDARIES_BY_CLASS[c]),
                        c, pick_racials(stats, weights))
                       for c, weights in STAT_WEIGHTS_BY_CLASS.items()],
                      reverse=True)
  for e in evaluation:
    print("\t", e)
