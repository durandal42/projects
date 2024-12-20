from common import assertEqual
from common import submit

import bisect


def parse_input(input):
  obstacles = set()
  gr, gc = None, None
  for r, line in enumerate(input.splitlines()):
    for c, x in enumerate(line):
      if x == "#":
        obstacles.add((r, c))
      if x == "^":
        gr, gc = r, c

  assert gr
  assert gc

  return obstacles, gr, gc


def organize_obstacles(obstacles):
  num_rows = max(r for r, c in obstacles)+1
  num_cols = max(c for r, c in obstacles)+1

  obstacles_by_row = [[] for r in range(num_rows)]
  obstacles_by_col = [[] for c in range(num_cols)]
  for r, c in obstacles:
    obstacles_by_row[r].append(c)
    obstacles_by_col[c].append(r)
  for l in obstacles_by_row:
    l.sort()
  for l in obstacles_by_col:
    l.sort()

  return obstacles_by_row, obstacles_by_col


def patrol(obstacles_by_row, obstacles_by_col, gr, gc):
  turns = []
  turns.append((gr, gc))

  dr, dc = -1, 0
  seen_with_direction = set()

  while True:
    if dr:
      nearest_obstacle_index = bisect.bisect(obstacles_by_col[gc], gr)
      if dr < 0:
        nearest_obstacle_index -= 1
      if nearest_obstacle_index not in range(len(obstacles_by_col[gc])):
        turns.append((0 if nearest_obstacle_index < 0 else len(obstacles_by_row)-1, gc))
        break
      gr = obstacles_by_col[gc][nearest_obstacle_index] - dr
    if dc:
      nearest_obstacle_index = bisect.bisect(obstacles_by_row[gr], gc)
      if dc < 0:
        nearest_obstacle_index -= 1
      if nearest_obstacle_index not in range(len(obstacles_by_row[gr])):
        turns.append((gr, 0 if nearest_obstacle_index < 0 else len(obstacles_by_col)-1))
        break
      gc = obstacles_by_row[gr][nearest_obstacle_index] - dc
    if (gr, gc, dr, dc) in seen_with_direction:
      return None
    turns.append((gr, gc))
    seen_with_direction.add((gr, gc, dr, dc))

    dr, dc = dc, -dr

  return turns


def sign(x):
  if x < 0:
    return -1
  if x > 0:
    return 1
  return 0


def visited(turns):
  seen = set()
  for i in range(len(turns)-1):
    r1, c1 = turns[i]
    r2, c2 = turns[i+1]
    dr = sign(r2 - r1)
    dc = sign(c2 - c1)
    seen.add((r1, c1))
    while (r1, c1) != (r2, c2):
      r1 += dr
      c1 += dc
      seen.add((r1, c1))
  return seen


def day06(input):
  obstacles, gr, gc = parse_input(input)
  obstacles_by_row, obstacles_by_col = organize_obstacles(obstacles)
  return len(visited(patrol(obstacles_by_row, obstacles_by_col, gr, gc)))


test_input = '''\
....#.....
.........#
..........
..#.......
.......#..
..........
.#..^.....
........#.
#.........
......#...
'''
test_output = 41

assertEqual(test_output, day06(test_input))


print('day06 answer:')
submit(day06(open('day06_input.txt', 'r').read()),
       expected=5153)
print()

# part 2 complication

test_output = 6


def day06(input):
  obstacles, gr, gc = parse_input(input)
  obstacles_by_row, obstacles_by_col = organize_obstacles(obstacles)

  default_path = visited(patrol(obstacles_by_row, obstacles_by_col, gr, gc))

  result = 0
  for r, c in default_path:
    if (gr, gc) == (r, c):
      continue
    obstacles_by_row[r].insert(bisect.bisect(obstacles_by_row[r], c), c)
    obstacles_by_col[c].insert(bisect.bisect(obstacles_by_col[c], r), r)
    patrol_result = patrol(obstacles_by_row, obstacles_by_col, gr, gc)
    if not patrol_result:
      result += 1
    obstacles_by_row[r].remove(c)
    obstacles_by_col[c].remove(r)
  return result


assertEqual(test_output, day06(test_input))

print('day06, part 2 answer:')
submit(day06(open('day06_input.txt', 'r').read()),
       expected=1711)
print()
