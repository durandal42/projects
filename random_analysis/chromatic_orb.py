import distribution
import collections


def orb_dice(n=1):
  # return distribution.dice(n+2, 8)
  return distribution.cartesian_product([distribution.die(8) for _ in range(n+2)])


def any_match(t):
  return collections.Counter(t).most_common(1)[0][1] > 1


for level in range(1, 2):
  print("Level:", level)
  od = orb_dice(level)

  print("raw dice:")
  print(od)

  print("sorted dice:")
  print(od.map(lambda d: tuple(sorted(d))))

  print("counted dice:")
  print(od.map(lambda d: tuple(collections.Counter(d).items())))

  print("Damage:")
  distribution.summarize(od.map(sum))

  print("Chance of fork:")
  print(od.map(any_match))
  print()
