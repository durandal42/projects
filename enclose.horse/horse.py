import json
from collections import deque
from collections import defaultdict
import queue
from fractions import Fraction
import multiprocessing
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


# provided by the master:
global_grid = None
global_horse = None
global_result_q = None

# managed by each worker
global_work_q = deque()
global_most_space = 0


def init_worker(grid, horse, result_q):
  global global_grid
  global_grid = grid
  global global_horse
  global_horse = horse
  global global_result_q
  global_result_q = result_q


NUM_WORKERS = 10


def solve(grid, horse, budget):
  print(f"solve({grid}, {horse}, {budget})")
  m = multiprocessing.Manager()
  result_q = m.Queue()
  init_worker(grid, horse, result_q)

  global_work_q.append((budget, set(), set(), 1))

  while global_work_q and len(global_work_q) < NUM_WORKERS:
    print("fanning out more work units...")
    budget, walls, notwalls, fanout = global_work_q.popleft()
    solve_work_unit(budget, walls, notwalls, fanout)
  print(f"fanned out to {len(global_work_q)} work units.")

  print(f"starting {NUM_WORKERS} workers...")
  pool = multiprocessing.Pool(
      processes=NUM_WORKERS, initializer=init_worker, initargs=(grid, horse, result_q,))
  workers = [pool.apply_async(solve_worker, (work,))
             for work in global_work_q]

  # Wait for all workers to finish.
  work_done = False
  while not work_done:
    work_done = True
    for w in workers:
      process_result_q(result_q)
      try:
        w.get(1)
      except multiprocessing.context.TimeoutError as e:
        work_done = False
        pass

  pool.close()

  return global_most_space


def process_result_q(result_q):
  global global_most_space
  while not result_q.empty():
    space, solution = result_q.get()
    if space > global_most_space:
      print(solution)
      global_most_space = space


def solve_worker(work_root):
  print(f"solve_worker({work_root})")
  global global_work_q
  global_work_q = deque()
  global_work_q.append(work_root)
  print("global_work_q:", global_work_q)
  while global_work_q:
    work = global_work_q.pop()
    budget, walls, notwalls, fanout = work
    solve_work_unit(budget, walls, notwalls, fanout)


def solve_work_unit(budget, walls, notwalls, fanout):
  # print(f"solve_work_unit({budget}, {walls}, {notwalls}, {fanout})")
  escape_path, space = search(global_grid, global_horse, walls)

  if not escape_path:
    # the horse didn't escape, so score this as a possible solution
    global global_most_space
    if space > global_most_space:
      global_most_space = space
      result = (space, f"found a solution using {len(walls)} walls and {space} space!"
                f"\n{print_grid(global_grid, walls)}")
      global_result_q.put(result)
    return

  # the horse did escape, so we MUST put a wall somewhere on its escape path

  if budget == 0:
    # ... but we're out of budget, so we're done with this branch :(
    return

  # iterate over all options for which cell on that path is the FIRST wall
  #   (and therefore everything up to that point is a non-wall,
  #    never to be picked again in this hypothetical branch)
  options = [i for i in range(len(escape_path) - 1)  # (don't wall the horse)
             if escape_path[i] not in notwalls]
  for i in options:
    global_work_q.append((budget-1,
                          walls | set([escape_path[i]]),
                          notwalls | set(escape_path[:i]),
                          fanout*len(options)))


def main():
  p = load_puzzle('xPt_fu')
  grid = parse_map(p['map'])
  print(grid)
  budget = int(p['budget'])
  print("budget:", budget)

  horse = find_horse(grid)
  print(horse)

  print(solve(grid, horse, budget))


if __name__ == '__main__':
  multiprocessing.freeze_support()
  main()
