import itertools
import time

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
  # print(f"constrain({cells}, {runs})")
  can_be_empty = [False] * len(cells)
  can_be_full = [False] * len(cells)
  for p in possible_cells_runwise(cells, runs):
    for i, c in enumerate(p):
      if c == EMPTY:
        can_be_empty[i] = True
      if c == FULL:
        can_be_full[i] = True
  for i in range(len(cells)):
    if can_be_full[i] and not can_be_empty[i]:
      cells[i] = FULL
    if can_be_empty[i] and not can_be_full[i]:
      cells[i] = EMPTY
  # print("constrained cells:", cells)
  return cells


def possible_cells_runwise(cells, runs):
  num_unknowns = len([c for c in cells if c == UNKNOWN])
  if num_unknowns == 0 and compute_runs(cells) == runs:
    return [cells]

  # print(f"possible_cells_runwise({cells}, {runs})")
  slack = len(cells) - (len(runs) - 1 + sum(runs))
  # print(f"slack: {slack}")
  if slack < 0:
    return []
  possibilities = []
  for i in range(slack + 1):
    maybe_cells = []
    possible = True
    for j in range(i):
      if cells[len(maybe_cells)] == FULL:
        possible = False
        break
      maybe_cells.append(EMPTY)
    if not possible:
      continue

    for j in range(runs[0]):
      if cells[len(maybe_cells)] == EMPTY:
        possible = False
        break
      maybe_cells.append(FULL)
    if not possible:
      continue
    if len(runs) > 1:
      if cells[len(maybe_cells)] == FULL:
        possible = False
        continue
      maybe_cells.append(EMPTY)
      # print(maybe_cells, "recursing...")
      rest_possibilities = possible_cells_runwise(
          cells[len(maybe_cells):], runs[1:])
      for rp in rest_possibilities:
        possibilities.append(maybe_cells + rp)
    else:
      while len(maybe_cells) < len(cells):
        if cells[len(maybe_cells)] == FULL:
          possible = False
          break
        maybe_cells.append(EMPTY)
      if not possible:
        continue
      possibilities.append(maybe_cells)

  # for p in possibilities:
  #   print(p)
  return possibilities

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


def solve_grid(column_runs, row_runs):
  solve_start = time.time()

  grid = [[UNKNOWN] * len(column_runs) for _ in row_runs]
  print(f"initial grid:\n{pretty_print_grid(grid, column_runs, row_runs)}")

  touched_rows = set()
  touched_cols = set()
  passes = 0
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
      print("could not make progress.")
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
      print("could not make progress.")
      break

    passes += 1
  # print(pretty_print_grid(grid, column_runs, row_runs))
  solve_end = time.time()
  print(f"finished solving in {solve_end - solve_start:.2f} seconds")
  return grid


assert solve_grid([], []) == []
assert solve_grid([[1]], [[1]]) == [[FULL]]

# solve_grid([[1, 1, 1, 1, 1], [1, 1, 1], [1, 1, 3], [1, 1],
#             [1, 1, 1], [1, 3], [1, 1, 3], [1, 2, 4], [1, 2], [1, 1]],
#            [[1, 1, 5], [0], [1], [4, 2, 1], [2], [1, 2], [4], [4, 4], [1, 2], [3, 1]])
