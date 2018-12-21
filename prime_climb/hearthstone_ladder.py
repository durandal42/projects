import itertools
import collections

WIN_RATIO = 0.1
STREAK_LENGTH = 3
STREAK_CEILING = 5
MAX_RANK = 25
RANK_FLOOR = 20

def stars_per_rank(rank):
  if rank > 20: return 2
  if rank > 15: return 3
  if rank > 10: return 4
  return 5

def win(rank, stars, streak):
  stars += 1
  streak = min(streak + 1, STREAK_LENGTH)
  if streak == STREAK_LENGTH and rank > 5: stars += 1
  if stars > stars_per_rank(rank):
    stars -= stars_per_rank(rank)
    rank -= 1
    if rank <= STREAK_CEILING:
      streak = 0
  return rank, stars, streak

def lose(rank, stars, streak):
  streak = 0
  if rank < RANK_FLOOR:
    stars -= 1
  if stars < 0:
    rank += 1
    stars += stars_per_rank(rank)
  return rank, stars, streak

def update(steps):
  new_steps = {}
  for state in steps.keys():
    rank, stars, streak = state
    if rank <= 0:  # already at legend
      new_steps[state] = 0.0
    else:
      new_steps[state] = (1 + 
                          WIN_RATIO * steps[win(rank, stars, streak)] +
                          (1.0 - WIN_RATIO) * steps[lose(rank, stars, streak)]
                          )
  return new_steps

def mean(values):
  return float(sum(values)) / len(values)

def summarize(steps):
  for rank in range(MAX_RANK + 1):
    print "%d\t%d" % (rank, int(steps[(rank, 0, 0)]))

def solve(steps):
  iterations = 0
  while True:
    #print iterations
    new_steps = update(steps)
    iterations += 1
    if new_steps == steps:
      break
    steps = new_steps
  summarize(steps)
  print "(took %d iterations to stabilize)" % iterations

INITIAL = {(rank, stars, streak):1.0
           for rank in range(MAX_RANK + 1)
           for stars in range(stars_per_rank(rank) + 1)
           for streak in range(STREAK_LENGTH + 1)}

solve(INITIAL)
