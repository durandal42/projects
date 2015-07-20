import random

def merge(intervals, new_interval):
  for i in intervals:
    if not new_interval:
      yield i
    elif i[1] < new_interval[0]:  # entirely before new
      yield i
    elif i[0] > new_interval[1]:  # entirely after new
      yield new_interval
      new_interval = None
      yield i
    else:  # partial overlap
      new_interval = (min(i[0], new_interval[0]), max(i[1], new_interval[1]))
  if new_interval:
    yield new_interval


DROP_SIZE = 0.01
SIDEWALK_MIN = 0.0
SIDEWALK_MAX = 1.0
def rain():
  drops = 0
  intervals = []
  while len(intervals) != 1 or intervals[0][0] > SIDEWALK_MIN or intervals[0][1] < SIDEWALK_MAX:
    drop_start = random.uniform(SIDEWALK_MIN - DROP_SIZE, SIDEWALK_MAX)
    drop_end = drop_start + DROP_SIZE
    drop = (drop_start, drop_end)
    drops += 1
    intervals = list(merge(intervals, drop))
  return drops

NUM_TRIALS = 10000
print sum(rain() for i in range(NUM_TRIALS)) / NUM_TRIALS

