import json
from collections import deque
from collections import defaultdict
from fractions import Fraction
import math


def load_puzzle(id):
  filecontents = open(f'maps/{id}').read()
  # print(filecontents)
  p = json.loads(filecontents)
  # print(p)
  return p


def parse_map(map_string):
  return map_string.splitlines()


def find_horse(grid):
  for r, row in enumerate(grid):
    for c, char in enumerate(row):
      if char == "H":
        return (r, c)


def make_path(visited, final):
  result = []
  current = final
  while current:
    result.append(current)
    current = visited[current]
  return result


def search(grid, horse, walls=set()):
  rows = len(grid)
  cols = len(grid[0])

  frontier = deque()
  frontier.append((horse, None))

  visited = {}

  while frontier:
    current, previous = frontier.popleft()
    # print(previous, "->", current)
    if current in visited:
      continue
    visited[current] = previous

    current_r, current_c = current
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
      next_r = current_r + dr
      next_c = current_c + dc
      if next_r not in range(0, rows) or next_c not in range(0, cols):
        return make_path(visited, current), len(visited)
      next = next_r, next_c
      if grid[next_r][next_c] in '.C' and next not in walls:
        # print(f"adding {next} to frontier")
        frontier.append((next, current))

  return None, len(visited)


def print_grid(grid, walls):
  result = []
  for r, row in enumerate(grid):
    for c, char in enumerate(row):
      if (r, c) in walls:
        result.append("X")
      else:
        result.append(char)
    result.append("\n")
  return "".join(result)


MAX_FANOUT = defaultdict(int)
MOST_SPACE = 0
PROGRESS = 0


def solve(grid, horse, budget, walls=set(), notwalls=set(), fanout=1):
  global MOST_SPACE
  global PROGRESS

  # print(f"solve(<grid>, {horse}, {budget}, walls={walls}, notwalls={notwalls})")
  escape_path, space = search(grid, horse, walls)
  # print("escape path:", escape_path)
  if escape_path:
    # print("escape path length:", len(escape_path))
    for x in escape_path:
      assert x not in walls
  # print("space roamed:", space)
  # print()

  if not escape_path:
    # the horse didn't escape, so score this as a possible solution
    if space > MOST_SPACE:
      print(f"found a solution using {len(walls)} walls and {space} space!")
      print(print_grid(grid, walls))
      print("progress:", PROGRESS, "=", float(PROGRESS))
      MOST_SPACE = space
    PROGRESS += Fraction(1, fanout)
    return space, None

  # the horse did escape, so we MUST put a wall somewhere on its escape path

  if budget == 0:
    # ... but we're out of budget, so we're done with this branch :(
    return 0, []

  # iterate over all options for which cell on that path is the FIRST wall
  #   (and therefore everything up to that point is a non-wall,
  #    never to be picked again in this hypothetical branch)
  options = [i for i in range(len(escape_path) - 1)  # (don't wall the horse itself)
             if escape_path[i] not in notwalls]
  if (len(options) > MAX_FANOUT[budget]):
    print("*"*(10-budget), f"budget: {budget}, fanout: {len(options)}")
    MAX_FANOUT[budget] = len(options)
  result = max(solve(grid, horse, budget-1,
                     walls=walls | set([escape_path[i]]),
                     notwalls=notwalls | set(escape_path[: i]),
                     fanout=fanout*len(options))
               for i in options)
  PROGRESS += Fraction(1, fanout)
  return result


def main():
  p = load_puzzle('xPt_fu')
  grid = parse_map(p['map'])
  print(grid)
  budget = int(p['budget'])
  print("budget:", budget)

  horse = find_horse(grid)
  print(horse)

  print(solve(grid, horse, budget))


main()
