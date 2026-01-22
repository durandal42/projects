import json
from collections import deque
from collections import defaultdict
from typing import NamedTuple
import queue
from fractions import Fraction
import multiprocessing
import math
from enum import Enum
import time
import argparse


class PuzzleInfo(NamedTuple):
  grid: list[str]
  horse: tuple
  adjacency: dict
  budget: int


def build_puzzle_info(id):
  filecontents = open(f'maps/{id}').read()
  # print(filecontents)
  json_spec = json.loads(filecontents)

  grid = parse_map(json_spec['map'])
  budget = int(json_spec['budget'])
  horse = find_horse(grid)
  adjacency = build_adjacency(grid)
  puzzle_info = PuzzleInfo(grid=grid, horse=horse,
                           budget=budget, adjacency=adjacency)
  print(puzzle_info)

  return puzzle_info


def parse_map(map_string):
  return map_string.splitlines()


def find_horse(grid):
  for r, row in enumerate(grid):
    for c, char in enumerate(row):
      if char == "H":
        return (r, c)


def build_adjacency(grid):
  rows = len(grid)
  cols = len(grid[0])

  adjacency = defaultdict(list)
  portals = defaultdict(list)
  num_spaces = 0
  for r, row in enumerate(grid):
    for c, char in enumerate(row):
      if char != '~':  # wall
        current = r, c
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
          neighbor_r = r + dr
          neighbor_c = c + dc
          if (neighbor_r not in range(0, rows)
              or neighbor_c not in range(0, cols)
                  or grid[neighbor_r][neighbor_c] != '~'):
            neighbor = neighbor_r, neighbor_c
            adjacency[current].append(neighbor)

      if char.isdigit():
        portals[char].append(current)

      if char == '.':
        num_spaces += 1

  for id, cells in portals.items():
    print(f"linking portal {id}: {cells}")
    assert len(cells) == 2
    adjacency[cells[0]].append(cells[1])
    adjacency[cells[1]].append(cells[0])

  return adjacency


def search(puzzle_info, walls=set()):
  # print(f'search({puzzle_info}, {walls})')
  grid = puzzle_info.grid
  adjacency = puzzle_info.adjacency
  rows = len(grid)
  cols = len(grid[0])

  frontier = deque()
  frontier.append(puzzle_info.horse)

  visited = set()
  bonus_score = 0

  while frontier:
    # print(f"frontier still has {len(frontier)} spaces")
    current = frontier.popleft()
    if current in visited:
      continue
    visited.add(current)

    current_r, current_c = current
    if grid[current_r][current_c] == 'C':
      # cherries
      bonus_score += 3
    if grid[current_r][current_c] == 'S':
      # bees
      bonus_score -= 5
    for next in adjacency[current]:
      next_r, next_c = next
      if next_r not in range(0, rows) or next_c not in range(0, cols):
        # print("not enclosed")
        return False, 0, visited
      if next not in walls:
        # print(f"adding {next} to frontier")
        frontier.append(next)

  return True, len(visited) + bonus_score, None


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
global_puzzle_info = None
global_result_q = None
global_status_d = None

# managed by each worker
global_work_q = deque()
global_most_score = 0


def init_shared_state(puzzle_info, result_q, status_d):
  global global_puzzle_info
  global_puzzle_info = puzzle_info
  global global_result_q
  global_result_q = result_q
  global global_status_d
  global_status_d = status_d


def solve(puzzle_info, num_workers=10):
  print(f"solve({puzzle_info})")
  m = multiprocessing.Manager()
  result_q = m.Queue()
  status_d = m.dict()
  init_shared_state(puzzle_info, result_q, status_d)

  print(f"starting {num_workers} workers...")
  pool = multiprocessing.Pool(
      processes=num_workers,
      initializer=init_shared_state,
      initargs=(puzzle_info, result_q, status_d))
  workers = [pool.apply_async(solve_worker, (i,)) for i in range(num_workers)]

  global_work_q.append((puzzle_info.budget, set(), set(), 1))
  solve_coordinator(num_workers)
  print("solve_coordinator finished.")

  # Wait for all workers to finish.
  work_done = False
  while not work_done:
    work_done = True
    for w in workers:
      process_result_q(result_q)
      try:
        w.get(1)
      except multiprocessing.context.TimeoutError as e:
        print(
            "solve_coordinator() finished, "
            "but a worker has not terminated yet.")
        work_done = False
        pass

  pool.close()

  return global_most_score


def process_result_q(result_q):
  global global_most_score
  while not result_q.empty():
    score, solution = result_q.get()
    if score > global_most_score:
      print(solution)
      global_most_score = score


class ControlSignal(Enum):
  # no payload
  # initial state for all workers
  STARTING_UP = 1

  # no payload
  # worker sets this to ask for work to do
  REQUEST_WORK = 2

  # payload = work unit
  # coordinator sets this to ask a worker to do this work
  PUSH_WORK = 3

  # no payload
  # worker sets this to indicate they're currently doing work
  WORKING = 4

  # no payload
  # coordinator sets this to ask a worker to give back a work unit
  RETURN_WORK = 5

  # payload = work unit
  # worker sets this status to offer an uncompleted
  # work unit back to the coordinator
  OFFER_WORK = 6

  # no payload
  # coordinator sets this to shut down a worker
  ALL_DONE = 7


def solve_coordinator(num_workers):
  looking_for_work = False
  while True:
    process_result_q(global_result_q)
    # print(f"coordinator has {len(global_work_q)} work units ready to hand out")
    # print("coordinator sees status:")
    all_workers_idle = True
    for k, v in global_status_d.items():
      # print(f"\t{k}: {v}")
      status, payload = v

      if status == ControlSignal.REQUEST_WORK:
        if global_work_q:
          global_status_d[k] = (ControlSignal.PUSH_WORK, global_work_q.pop())
          all_workers_idle = False
        else:
          looking_for_work = True
      else:
        all_workers_idle = False
      if status == ControlSignal.WORKING and looking_for_work:
        global_status_d[k] = (ControlSignal.RETURN_WORK, None)
      if status == ControlSignal.OFFER_WORK:
        global_work_q.append(payload)
        global_status_d[k] = (ControlSignal.WORKING, None)
        looking_for_work = False

    if all_workers_idle and len(global_status_d) == num_workers and not global_work_q:
      print("coordinator: all workers are asking for work, and we have nothing to give; shutting down.")
      for k, v in global_status_d.items():
        global_status_d[k] = (ControlSignal.ALL_DONE, None)
      return

    time.sleep(2)


def solve_worker(worker_id):
  print(f"solve_worker({worker_id})")
  global_status_d[worker_id] = (ControlSignal.STARTING_UP, )
  print(f"worker {worker_id}: set state to STARTING_UP")

  global global_work_q
  global_work_q = deque()
  while True:
    # print(f"worker {worker_id}: doing local work")
    for _ in range(10000):
      if global_work_q:
        work = global_work_q.pop()
        budget, walls, notwalls, fanout = work
        solve_work_unit(budget, walls, notwalls, fanout)
      else:
        if global_status_d[worker_id][0] in [
                ControlSignal.WORKING,
                ControlSignal.STARTING_UP,
                ControlSignal.RETURN_WORK]:
          print(f"worker {worker_id}: asking for more work")
          global_status_d[worker_id] = (ControlSignal.REQUEST_WORK, None)
          time.sleep(1)
        break

    # print(f"worker {worker_id}: checking for status update...")
    status, payload = global_status_d[worker_id]
    # print(f"worker {worker_id} status:", status)
    if status == ControlSignal.PUSH_WORK:
      print(f"worker {worker_id}: got more work:", payload)
      global_work_q.append(payload)
      global_status_d[worker_id] = (ControlSignal.WORKING, None)
    if status == ControlSignal.ALL_DONE:
      print(f"worker {worker_id}: shutting down.")
      return
    if status == ControlSignal.RETURN_WORK:
      if len(global_work_q) > 1:
        print(f"worker {worker_id}: saw RETURN_WORK, sharing our oldest work unit")
        work = global_work_q.popleft()  # oldest outstanding work unit
        global_status_d[worker_id] = (ControlSignal.OFFER_WORK, work)
      else:
        print(f"worker {worker_id}: saw RETURN_WORK, but has no work to share")


def solve_work_unit(budget, walls, notwalls, fanout):
  # print(f"solve_work_unit({budget}, {walls}, {notwalls}, {fanout})")
  enclosed, score, visited = search(global_puzzle_info, walls)

  if enclosed:
    # score this as a possible solution
    global global_most_score
    if score > global_most_score:
      global_most_score = score
      result = (
          score,
          f"found a solution using {len(walls)} walls and {score} score!"
          f"\n{print_grid(global_puzzle_info.grid, walls)}")
      global_result_q.put(result)
    return

  # the horse did escape, so we MUST put a wall somewhere on its escape path

  if budget == 0:
    # ... but we're out of budget, so we're done with this branch :(
    return

  # iterate over all options for which cell on that path is the FIRST wall
  #   (and therefore everything up to that point is a non-wall,
  #    never to be picked again in this hypothetical branch)
  options = [
      (r, c) for r, c in visited
      if (r, c) not in notwalls
      and global_puzzle_info.grid[r][c] == '.'
  ]
  for i, wall in enumerate(options):
    global_work_q.append((budget-1,
                          walls | set([wall]),
                          notwalls | set(options[:i]),
                          fanout*len(options)))


def main():
  parser = argparse.ArgumentParser(
      prog='Enclose.Horse Solver',
      description='Solves daily puzzles offered by enclose.horse')
  parser.add_argument('-m', '--map', default='Kj7mXp')
  parser.add_argument('-w', '--workers', type=int, default=10)
  args = parser.parse_args()

  puzzle_info = build_puzzle_info(args.map)
  print(puzzle_info)

  print(solve(puzzle_info, num_workers=args.workers))


if __name__ == '__main__':
  multiprocessing.freeze_support()
  main()
