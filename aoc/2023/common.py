from collections import deque


def assertEqual(expected, actual):
  assert expected == actual, f"expected: {expected}\nactual: {actual}"


assertEqual(0, 0)
try:
  assertEqual(1, 0)
  assert False
except AssertionError:
  pass


def submit(answer, expected=None):
  if expected is not None:
    assertEqual(expected, answer)
  print(answer)


def fill(grid, r, c, src='.', dst='X'):
  frontier = deque()
  seen = set()
  start = (r, c)
  frontier.appendleft(start)
  seen.add(start)
  while frontier:
    # print('len(frontier) =', len(frontier))
    loc = frontier.pop()
    r, c = loc
    # print(loc)
    grid[r][c] = dst
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
      nr, nc = r + dr, c + dc
      if (nr, nc) in seen:
        continue
      if nr not in range(len(grid)):
        continue
      if nc not in range(len(grid[0])):
        continue
      if grid[nr][nc] != src:
        continue

      frontier.appendleft((nr, nc))
      seen.add((nr, nc))

  return len(seen)
