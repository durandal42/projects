import itertools
import time
import functools

EMPTY = 0
FULL = 1
UNKNOWN = None


def compute_runs(cells):
  result = []
  current_run = 0
  for c in cells:
    if c == FULL:
      current_run += 1
    else:
      if current_run > 0:
        result.append(current_run)
        current_run = 0
  if current_run > 0:
    result.append(current_run)
    current_run = 0
  if len(result) == 0:
    return [0]
  return result

assert compute_runs([]) == [0]
assert compute_runs([EMPTY] * 8) == [0]
assert compute_runs([FULL] * 8) == [8]
assert compute_runs([FULL] * 8 + [EMPTY] + [FULL] * 3) == [8, 3]


def pretty_print_grid(grid, col_runs, row_runs):
  if not grid:
    return ""
  result = ''
  result += '+' + '-' * (len(grid[0]) * 2) + "+\n"
  for i, row in enumerate(grid):
    result += "|"
    for c in row:
      if c == UNKNOWN:
        result += "<>"
      if c == EMPTY:
        result += "  "
      if c == FULL:
        result += "[]"
      # result += " "
    result += "| "
    result += " ".join(str(r) for r in row_runs[i])
    result += "\n"
  result += '+' + '-' * (len(grid[0]) * 2) + "+\n"
  for i in range(max(len(r) for r in col_runs)):
    result += " "
    for j, run in enumerate(col_runs):
      if i < len(run):
        result += str(run[i]).rjust(2)
      else:
        result += "  "
    result += "\n"
  return result


def possible_cells_bitwise(cells, runs):
  num_unknowns = len([c for c in cells if c == UNKNOWN])
  if num_unknowns == 0:
    return [cells]
  if num_unknowns > 10:
    print(f"warning: {num_unknowns} is a lot of unknowns.")

  possibilities = []
  for p in itertools.product([EMPTY, FULL], repeat=num_unknowns):
    # print("bits:", p)
    maybe_cells = cells[:]
    j = 0
    for i, c in enumerate(maybe_cells):
      if c == UNKNOWN:
        maybe_cells[i] = p[j]
        j += 1
    if compute_runs(maybe_cells) == runs:
      possibilities.append(maybe_cells)
      # print("possible cells:", maybe_cells)
  return possibilities


def constrain(cells, runs):
  return constrain_bidirectional(cells, runs)


def constrain_bidirectional(cells, runs):
  return constrain_unidirectional(
      constrain_unidirectional(cells, runs)[::-1],
      runs[::-1])[::-1]


def constrain_unidirectional(cells, runs):
  # print(f"constrain({cells}, {runs})")
  can_be_empty = [False] * len(cells)
  can_be_full = [False] * len(cells)
  min_p = len(cells)
  for p in possible_cells_runwise(cells, runs):
    min_p = min(min_p, len(p))
    for i, c in enumerate(p):
      if c == EMPTY:
        can_be_empty[i] = True
      if c == FULL:
        can_be_full[i] = True
  for i in range(min_p):
    if can_be_full[i] and not can_be_empty[i]:
      cells[i] = FULL
    if can_be_empty[i] and not can_be_full[i]:
      cells[i] = EMPTY
  # print("constrained cells:", cells)
  return cells


@functools.lru_cache(maxsize=None)
def num_possibilities(slack, num_runs):
  # how many ways can we split slack among runs?
  if slack <= 0:
    return 1
  if num_runs <= 1:
    return slack + 1
  total = 0
  for i in range(slack + 1):
    total += num_possibilities(slack - i, num_runs - 1)
  return total

assert num_possibilities(0, 1) == 1
assert num_possibilities(1, 1) == 2
assert num_possibilities(2, 2) == 1 + 2 + 3

RECURSION_LIMIT = 1000
RECURSION_LIMIT_REACHED = False


def possible_cells_runwise(cells, runs, recursion_weight=None):
  global RECURSION_LIMIT_REACHED
  # print(f"possible_cells_runwise({cells}, {runs})")
  if not cells and not runs:
    return [[]]
  num_unknowns = len([c for c in cells if c == UNKNOWN])
  if num_unknowns == 0:
    if compute_runs(cells) == runs:
      # print("returning early because no unknowns in rest of row, which is
      # correctly solved")
      return [cells]
    else:
      # print("returning early because no unknowns in rest of row, which is
      # incorrectly solved")
      return []

  # print(f"possible_cells_runwise({cells}, {runs})")
  slack = len(cells) - (len(runs) - 1 + sum(runs))
  if recursion_weight is None:
    recursion_weight = 1
    num_possible = num_possibilities(slack, len(runs))
    # print(f"estimated {num_possible} possibilies to consider for {runs} (slack:{slack}, num_runs:{len(runs)}) ...", end="\n")
    # if num_possible > 10000:
    #   print(" which is too large.")
    #   return []  # hack hack hack
    # print(" going for it!.")

  # TODO(durandal): grow runs from the ends?
  # TODO(durandal): more aggressively prune possibilities
  # TOOD(durandal): if slack < max(runs)
  # TODO(durandal): extract info from possibility prefixes/suffixes

  # print(f"slack: {slack}")
  if slack < 0:
    return []

  possibilities = []
  for i in range(slack + 1):
    maybe_cells = []
    # print(f"maybe_cells: {maybe_cells}")
    possible = True
    for j in range(i):
      if cells[len(maybe_cells)] == FULL:
        possible = False
        break
      maybe_cells.append(EMPTY)
      # print(f"maybe_cells: {maybe_cells}")
    if not possible:
      break

    for j in range(runs[0]):
      if cells[len(maybe_cells)] == EMPTY:
        possible = False
        # TODO(durandal): if this fails, don't just reserve 1 more slack;
        # reserve enough to succeed.
        break
      maybe_cells.append(FULL)
      # print(f"maybe_cells: {maybe_cells}")
    if not possible:
      continue

    if len(runs) > 1:
      if cells[len(maybe_cells)] == FULL:
        possible = False
        continue
      maybe_cells.append(EMPTY)
      # print(f"maybe_cells: {maybe_cells}")
    else:
      while len(maybe_cells) < len(cells):
        if cells[len(maybe_cells)] == FULL:
          possible = False
          # TODO(durandal): if this fails, reserve enough more slack that it
          # could succeed.
          break
        maybe_cells.append(EMPTY)
        # print(f"maybe_cells: {maybe_cells}")
      if not possible:
        continue
    possibilities.append(maybe_cells)

  # print("before recursion, possibilities are:")
  # for p in possibilities:
  #   print(p)
  blowup_factor = len(possibilities) * recursion_weight
  if blowup_factor > RECURSION_LIMIT:
    # print(f"bailing out of deep recursion, with blowup_factor =
    # {blowup_factor}")
    RECURSION_LIMIT_REACHED = True
    return possibilities

  recursed_possibilities = []
  for maybe_cells in possibilities:
          # print(maybe_cells, "recursing...")
    rest_possibilities = possible_cells_runwise(
        cells[len(maybe_cells):], runs[1:], recursion_weight=len(possibilities) * recursion_weight)
    for rp in rest_possibilities:
      recursed_possibilities.append(maybe_cells + rp)

  # for p in recursed_possibilities:
  #   print(p)
  return recursed_possibilities

assert constrain([UNKNOWN], [1]) == [FULL]
assert constrain([UNKNOWN] * 2, [1]) == [UNKNOWN, UNKNOWN]
assert constrain([UNKNOWN] * 3, [2]) == [UNKNOWN, FULL, UNKNOWN]
assert constrain([UNKNOWN] * 3 + [FULL], [2]) == [EMPTY, EMPTY, FULL, FULL]
assert (constrain([FULL, EMPTY, UNKNOWN, FULL, UNKNOWN, UNKNOWN, UNKNOWN, FULL, UNKNOWN, UNKNOWN], [1, 1, 3])
        == [FULL, EMPTY, EMPTY, FULL, EMPTY, UNKNOWN, UNKNOWN, FULL, UNKNOWN, UNKNOWN])


def is_solved(grid):
  for row in grid:
    for cell in row:
      if cell == UNKNOWN:
        return False
  return True


def solve_grid_recursion_limited(grid, column_runs, row_runs):
  touched_rows = set()
  touched_cols = set()
  passes = 0
  # TODO(durandal): run each row (or col) constraint pass in parallel
  while not is_solved(grid):
    touched_cols = set()
    for i, row_run in enumerate(row_runs):
      if passes > 0 and i not in touched_rows:
        continue
      # print("constraining row %d..." % i)
      row = grid[i]
      new_row = constrain(row[:], row_run)
      for j, new_val in enumerate(new_row):
        if new_val != row[j]:
          touched_cols.add(j)
          grid[i][j] = new_val
    if touched_cols:
      print(f"newly contrained by row:\n{pretty_print_grid(grid, column_runs, row_runs)}")
    if is_solved(grid):
      break

    if passes > 0 and not touched_cols:
      break

    touched_rows = set()
    for i, col_run in enumerate(column_runs):
      if passes > 0 and i not in touched_cols:
        continue
      # print("constraining col %d..." % i)
      col = [row[i] for row in grid]
      new_col = constrain(col[:], col_run)
      for j, new_val in enumerate(new_col):
        if new_val != col[j]:
          touched_rows.add(j)
          grid[j][i] = new_val
    if touched_rows:
      print(f"newly contrained by col:\n{pretty_print_grid(grid, column_runs, row_runs)}")

    if passes > 0 and not touched_rows:
      break

    passes += 1
  # print(pretty_print_grid(grid, column_runs, row_runs))
  return grid


def solve_grid(column_runs, row_runs):
  global RECURSION_LIMIT, RECURSION_LIMIT_REACHED
  RECURSION_LIMIT = 10
  RECURSION_LIMIT_REACHED = True

  solve_start = time.time()

  grid = [[UNKNOWN] * len(column_runs) for _ in row_runs]
  print(f"initial grid:\n{pretty_print_grid(grid, column_runs, row_runs)}")

  while not is_solved(grid):
    if not RECURSION_LIMIT_REACHED:
      print("could not make progress, and recursion limit wasn't reached.")
      break
    RECURSION_LIMIT_REACHED = False
    RECURSION_LIMIT *= 2
    print(f"attempting to make progress with recursion limit {RECURSION_LIMIT}")
    grid = solve_grid_recursion_limited(grid, column_runs, row_runs)

  solve_end = time.time()
  print(f"finished solving in {solve_end - solve_start:.2f} seconds")
  return grid

assert solve_grid([], []) == []
assert solve_grid([[1]], [[1]]) == [[FULL]]

# solve_grid([[1, 1, 1, 1, 1], [1, 1, 1], [1, 1, 3], [1, 1],
#             [1, 1, 1], [1, 3], [1, 1, 3], [1, 2, 4], [1, 2], [1, 1]],
#            [[1, 1, 5], [0], [1], [4, 2, 1], [2], [1, 2], [4], [4, 4], [1, 2], [3, 1]])


# TODO(durandal): colored nonograms!!??
