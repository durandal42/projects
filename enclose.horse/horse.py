import json
from collections import deque
from collections import defaultdict
import queue
from fractions import Fraction
import multiprocessing
import math
from enum import Enum
import time


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


def build_adjacency(grid):
  rows = len(grid)
  cols = len(grid[0])

  adjacency = defaultdict(list)
  portals = defaultdict(list)
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

  for id, cells in portals.items():
    print(f"linking portal {id}: {cells}")
    assert len(cells) == 2
    adjacency[cells[0]].append(cells[1])
    adjacency[cells[1]].append(cells[0])

  return adjacency


def make_path(visited, final):
  result = []
  current = final
  while current:
    result.append(current)
    current = visited[current]
  return result


def search(grid, adjacency, horse, walls=set()):
  rows = len(grid)
  cols = len(grid[0])

  frontier = deque()
  frontier.append((horse, None))

  visited = {}
  cherries_visited = 0

  while frontier:
    current, previous = frontier.popleft()
    # print(previous, "->", current)
    if current in visited:
      continue
    visited[current] = previous

    current_r, current_c = current
    if grid[current_r][current_c] == 'C':
      cherries_visited += 1
    for next in adjacency[current]:
      next_r, next_c = next
      if next_r not in range(0, rows) or next_c not in range(0, cols):
        return make_path(visited, current), len(visited)
      if next not in walls:
        # print(f"adding {next} to frontier")
        frontier.append((next, current))

  return None, len(visited) + 3 * cherries_visited


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
global_adjacency = None
global_horse = None
global_result_q = None
global_control_q = None

# managed by each worker
global_work_q = deque()
global_most_space = 0


def init_worker(grid, adjacency, horse, result_q, control_q):
  global global_grid
  global_grid = grid
  global global_adjacency
  global_adjacency = adjacency
  global global_horse
  global_horse = horse
  global global_result_q
  global_result_q = result_q
  global global_control_q
  global_control_q = control_q


NUM_WORKERS = 10


def solve(grid, adjacency, horse, budget):
  print(f"solve({grid}, {horse}, {budget})")
  m = multiprocessing.Manager()
  result_q = m.Queue()
  control_q = m.Queue()

  print(f"starting {NUM_WORKERS} workers...")
  pool = multiprocessing.Pool(
      processes=NUM_WORKERS,
      initializer=init_worker,
      initargs=(grid, adjacency, horse, result_q, control_q))
  workers = [pool.apply_async(solve_worker) for i in range(NUM_WORKERS)]

  init_worker(grid, adjacency, horse, result_q, control_q)
  global_work_q.append((budget, set(), set(), 1))
  solve_coordinator(NUM_WORKERS)
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

  return global_most_space


def process_result_q(result_q):
  global global_most_space
  while not result_q.empty():
    space, solution = result_q.get()
    if space > global_most_space:
      print(solution)
      global_most_space = space


class ControlSignal(Enum):
  # payload = work unit
  # pushing this message is asking someone to do this work
  DO_WORK = 1

  # no payload
  # pushing this message is asking for more work to do
  MORE_WORK_PLEASE = 2

  # no payload
  # pushing this message says all work is done, time to shut down
  ALL_DONE = 3


def coordinator_try_shutdown():
  # If there's outstanding work anywhere in the queue, pick it back up
  # Otherwise, respond to all MORE_WORK_PLEASE requests with ALL_DONE
  # Either way, return how many net ALL_DONEs we added to the queue.
  num_more_work_please = 0
  num_all_done = 0
  while True:
    try:
      message = global_control_q.get(False)
      if message[0] == ControlSignal.DO_WORK:
        work = message[1]
        print(
            "coordinator: someone sent work back, so we can pick back up:",
            work)
        global_work_q.append(work)
        # put all the MORE_WORK_PLEASE back in the queue
        for i in range(num_more_work_please):
          global_control_q.put((ControlSignal.MORE_WORK_PLEASE, None))
        # recall any ALL_DONEs, replacing them with MORE_WORK_PLEASE
        for i in range(num_all_done):
          global_control_q.put((ControlSignal.MORE_WORK_PLEASE, None))
        return -num_all_done
      if message[0] == ControlSignal.MORE_WORK_PLEASE:
        num_more_work_please += 1
      if message[0] == ControlSignal.ALL_DONE:
        num_all_done += 1
    except queue.Empty:
      break
  if num_more_work_please > 0:
    print(
        f"coordinator: {num_more_work_please} workers are asking for work,"
        " but we don't have any. Send ALL_DONE! ")
    for i in range(num_more_work_please):
      global_control_q.put((ControlSignal.ALL_DONE, None))
    # put any consumed ALL_DONE's back in the queue
    for i in range(num_all_done):
      global_control_q.put((ControlSignal.ALL_DONE, None))

  return num_more_work_please


def solve_coordinator(num_workers):
  while True:
    # do an amount of work
    for _ in range(1000):
      if not global_work_q:
        # print("coordinator: ran out of local work")
        time.sleep(1)
        delta_num_workers = coordinator_try_shutdown()
        num_workers -= delta_num_workers
        if delta_num_workers != 0:
          print(f"coordinator_try_shutdown() resulted in {delta_num_workers} "
                "being told to shut down")
          print(f"coordinator: {num_workers} workers "
                "are believed still to be working.")
        if num_workers == 0:
          return
        else:
          continue

      # print("coordinator: doing local work")
      budget, walls, notwalls, fanout = global_work_q.pop()
      solve_work_unit(budget, walls, notwalls, fanout)
    try:
      # print("coordinator: processing result queue")
      process_result_q(global_result_q)
      # print("coordinator: see if anyone has anything to say")
      message = global_control_q.get(False)  # nonblocking get
      if message[0] == ControlSignal.MORE_WORK_PLEASE:
        if len(global_work_q) > 1:
          work = global_work_q.popleft()  # oldest outstanding work unit
          print("coordinator: saw MORE_WORK_PLEASE, "
                "sharing our oldest work unit:", work)
          print(f"coordinator: still have {len(global_work_q)} "
                "local work units.")
          global_control_q.put((ControlSignal.DO_WORK, work))
        else:
          print("coordinator: saw MORE_WORK_PLEASE, "
                "can't offer any work to do right now")
          global_control_q.put((ControlSignal.MORE_WORK_PLEASE, work))
      if message[0] in [ControlSignal.ALL_DONE, ControlSignal.DO_WORK]:
        # print("coordinator: saw [ALL_DONE,DO_WORK], putting it back")
        global_control_q.put(message)
    except queue.Empty:
      # print("coordinator: there were no messages")
      pass


def solve_worker():
  print(f"solve_worker()")
  global global_work_q
  global_work_q = deque()
  while True:
    while global_work_q:
      # print("worker: doing local work")
      work = global_work_q.pop()
      budget, walls, notwalls, fanout = work
      solve_work_unit(budget, walls, notwalls, fanout)

    print("worker: asking for more work")
    global_control_q.put((ControlSignal.MORE_WORK_PLEASE, None))

    # print("worker: listening for messages...")
    message = global_control_q.get()  # blocking get; no timeout
    if message[0] == ControlSignal.DO_WORK:
      print("worker: got more work:", message[1])
      global_work_q.append(message[1])
    if message[0] == ControlSignal.ALL_DONE:
      print("worker: shutting down.")
      return
    if message[0] == ControlSignal.MORE_WORK_PLEASE:
      if len(global_work_q) > 1:
        print("worker: saw MORE_WORK_PLEASE, sharing our oldest work unit")
        work = global_work_q.popleft()  # oldest outstanding work unit
        global_control_q.put((ControlSignal.DO_WORK, work))
      else:
        # print("worker: saw MORE_WORK_PLEASE, can't offer any work to do right now")
        time.sleep(10)
        global_control_q.put(message)


def solve_work_unit(budget, walls, notwalls, fanout):
  # print(f"solve_work_unit({budget}, {walls}, {notwalls}, {fanout})")
  escape_path, space = search(
      global_grid, global_adjacency, global_horse, walls)

  if not escape_path:
    # the horse didn't escape, so score this as a possible solution
    global global_most_space
    if space > global_most_space:
      global_most_space = space
      result = (
          space,
          f"found a solution using {len(walls)} walls and {space} space!"
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
             if escape_path[i] not in notwalls
             and global_grid[escape_path[i][0]][escape_path[i][1]] == '.'
             ]
  for i in options:
    global_work_q.append((budget-1,
                          walls | set([escape_path[i]]),
                          notwalls | set(escape_path[:i]),
                          fanout*len(options)))


def main():
  p = load_puzzle('gl7REy')
  grid = parse_map(p['map'])
  print(grid)
  budget = int(p['budget'])
  print("budget:", budget)

  horse = find_horse(grid)
  print(horse)

  adjacency = build_adjacency(grid)
  print(adjacency)

  print(solve(grid, adjacency, horse, budget))


if __name__ == '__main__':
  multiprocessing.freeze_support()
  main()
