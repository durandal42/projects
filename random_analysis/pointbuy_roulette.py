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
    "Artificer": (0, 8, 3, 4, 2, 0),
    "Barbarian": (6, 3, 4, 0, 2, 0),
    "Bard": (0, 3, 3, 1, 2, 6),
    "Bard (Valor)": (0, 8, 3, 1, 2, 6),
    "Cleric (Heavy)": (2, 1, 3, 1, 7, 1),
    "Cleric (Medium)": (0, 3, 3, 1, 7, 1),
    "Druid": (0, 3, 3, 1, 7, 0),
    "Fighter (DEX EK)": (0, 8, 3, 3, 2, 0),
    "Fighter (DEX)": (0, 8, 2, 0, 2, 0),
    "Fighter (STR EK)": (8, 1, 4, 3, 2, 0),
    "Fighter (STR)": (8, 1, 3, 0, 2, 0),
    "Monk ": (0, 8, 3, 1, 6, 0),
    "Paladin": (8, 1, 4, 0, 2, 5),
    "Ranger (DEX)": (0, 8, 3, 1, 5, 1),
    "Ranger (STR)": (8, 2, 4, 1, 5, 1),
    "Rogue (AT)": (0, 9, 3, 4, 2, 1),
    "Rogue (non-AT)": (0, 9, 2, 1, 2, 1),
    "Sorcerer ": (0, 3, 3, 1, 2, 5),
    "Warlock": (0, 3, 3, 1, 2, 5),
    "Wizard": (0, 3, 3, 6, 2, 0),
}

RACIAL_BONUS_INDICES = distribution.cartesian_product(
    [distribution.die(6),
     # distribution.die(6),
     distribution.die(6)]).filter(lambda x: x[0] != x[1])
print(RACIAL_BONUS_INDICES)


def pick_racials(stats, weights):
  best_stats = None
  best_score = -100
  for bonuses, _ in RACIAL_BONUS_INDICES.items():
    stats_after_racials = list(stats)
    stats_after_racials[bonuses[0] - 1] += 2
    stats_after_racials[bonuses[1] - 1] += 1
    if len(bonuses) >= 3:
      stats_after_racials[bonuses[2] - 1] += 1
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

  # print("score distribution:")
  # distribution.summarize(pointbuy_legal
  #                        .map(lambda x: pick_racials(x, weights))
  #                        .map(lambda x: score_array(x, weights)))

  stats_and_scores = []
  for stats, p in pointbuy_legal.items():
    post_racials = pick_racials(stats, weights)
    stats_and_scores.append(
        (score_array(post_racials, weights), stats, post_racials))
  stats_and_scores.sort()

  print("best statline: ", stats_and_scores[-1])
  print("worst statline:", stats_and_scores[0])
  n = len(stats_and_scores)
  NUM_BUCKETS = 100
  bucket_boundaries = [stats_and_scores[math.floor(n * p / NUM_BUCKETS)][0]
                       for p in range(NUM_BUCKETS)]
  # print("percentile boundaries:", bucket_boundaries)
  BUCKET_BOUNDARIES_BY_CLASS[c] = bucket_boundaries


def assign_percentile(value, bucket_boundaries):
  for i, bucket_boundary in enumerate(bucket_boundaries):
    if bucket_boundary > value:
      return i
  return len(bucket_boundaries)

def evaluate(stats):
  evaluation = []
  for c, weights in STAT_WEIGHTS_BY_CLASS.items():
    post_racials = pick_racials(stats, weights)
    score = score_array(post_racials, weights)
    evaluation.append((assign_percentile(score, BUCKET_BOUNDARIES_BY_CLASS[c]),
                       c, post_racials))
  evaluation.sort(reverse=True)
  return evaluation

print("\n16 random pointbuy-legal statlines:")
for stats in sample(pointbuy_legal, 16):
  print(stats)
  for e in evaluate(stats):
    print("\t", e)

best_class_count = collections.Counter()
worst_class_count = collections.Counter()
for stats,p in pointbuy_legal.items():
  e = evaluate(stats)
  best_class_count[e[0][1]] += 1
  worst_class_count[e[-1][1]] += 1
print("Class representation (best):", best_class_count)
print("Class representation (worst):", worst_class_count)
