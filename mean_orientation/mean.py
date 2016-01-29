def distance(a, b):
  diff = b - a
  if diff < -90: diff += 180
  if diff >= 90: diff -= 180
  return diff

def mean(orientations):
  #print orientations
  naive_mean = sum(orientations) / float(len(orientations))
  adjust = 180 / float(len(orientations))
  candidates = [(naive_mean + i * adjust) % 180
                for i in range(len(orientations))]
  print candidates
  best = (float("inf"), None)
  for c in candidates:
    left_distance, right_distance = 0, 0
    for o in orientations:
      dist = distance(o, c)
      if dist < 0: left_distance -= dist
      if dist > 0: right_distance += dist
    print c, left_distance, right_distance
    if left_distance != right_distance:
      continue
    best = min(best, (left_distance, c))
  return best[1]

import math
def saul(orientations):
  x = [math.cos(math.radians(2.0 * o)) for o in orientations]
  y = [math.sin(math.radians(2.0 * o)) for o in orientations]
  mean_x = sum(x) / float(len(x))
  mean_y = sum(y) / float(len(y))
  mean_o = math.degrees(math.atan2(mean_y, mean_x))
  if mean_o < 0: mean_o += math.pi 
  return mean_o / 2.0

print saul([89, 91])
assert saul([89, 91]) == 90

print saul([1, 179])
assert saul([1, 179]) == 0

print saul(range(180))

