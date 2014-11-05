YES = 'y'
NO = 'n'
MAYBE = '?'

def update(info, runs, allow_brute_force=0):
  #print 'update(%s, %s)' % (info, runs)

  # break early if nothing to do
  if not MAYBE in info:
    #print 'no uncertainty here:\n',info, runs
    assert validate(info, runs)
    return info

  if len(runs) == 0:
    print info, runs
    assert YES not in info
    if MAYBE in info:
      print 'no runs remaining:\n', info, runs
      info = [NO] * len(info)
    return info

  if len(runs) == 1 and runs[0] == len(info):
    assert NO not in info
    if MAYBE in info:
      print 'only run fills whole range:\n', info, runs
      info = [YES] * len(info)
    return info

  if sum(runs) + len(runs)-1 == len(info):
    print 'remaining runs fit exactly:\n', info, runs
    i = 0
    for r in runs:
      assert NO not in info[i:i+r]
      info[i:i+r] = [YES] * r
      i += r
      if i < len(info):
        assert info[i] != YES
        info[i] = NO
        i += 1
    return info

  # trim leading NOs
  if info[0] == NO:
    #print 'recursing without leading no...'
    info[1:] = update(info[1:], runs, allow_brute_force)
    return info
  # trim trailing NOs
  if info[-1] == NO:
    #print 'recursing without trailing no...'
    info[:-1] = update(info[:-1], runs, allow_brute_force)
    return info

  # extend leading run
  if info[0] == YES:
    first = runs[0]
    assert NO not in info[:first]
    if MAYBE in info[:first]:
      print 'extending leading run:\n', info, runs
      info[:first] = [YES] * first
    assert info[first] != YES
    if info[first] == MAYBE:
      print 'capping leading run:\n', info, runs
      info[first] = NO
    #print 'recursing with leading run satisfied...'
    info[first:] = update(info[first:], runs[1:], allow_brute_force)
    return info
  # extend trailing run
  if info[-1] == YES:
    last = runs[-1]
    assert NO not in info[-last:]
    if MAYBE in info[-last:]:
      print 'extending trailing run:\n', info, runs
      info[-last:] = [YES] * last
    assert info[-last-1] != YES
    if info[-last-1] == MAYBE:
      print 'capping trailing run:\n', info, runs
      info[-last-1] = NO
    #print 'recursing with trailing run satisfied...'
    info[:-last] = update(info[:-last], runs[:-1], allow_brute_force)
    return info

  if len(runs) == 1 and runs[0]*2 > len(info):
    gap = len(info) - runs[0]
    assert NO not in info[gap:-gap]
    if MAYBE in info[gap:-gap]:
      print 'only run is large enough to confirm middle:\n', info, runs
      info[gap:-gap] = [YES] * (len(info) - gap*2)
      return info

  yes_locations = [i for i in range(len(info)) if info[i] == YES]
  yes_count = len(yes_locations)
  assert sum(runs) >= yes_count
  if sum(runs) == yes_count:
    if MAYBE in info:
      print 'all runs accounted for:\n', info, runs
      info = [x == YES and YES or NO for x in info]
      print info, runs
    return info

  if len(runs) == 1 and YES in info:
    first = yes_locations[0]
    last = yes_locations[-1]
    if MAYBE in info[first:last+1]:
      print 'hole found:', info, runs
      assert NO not in info[first:last+1]
      info[first:last+1] = [YES] * (last - first + 1)
      return info
    if first + runs[0] < len(info):
      assert YES not in info[first+runs[0]:]
      if MAYBE in info[first+runs[0]:]:
        print "existing run can't reach end of window:", info, runs
        info[first+runs[0]:] = [NO] * len(info[first+runs[0]:])
        return info
    if last - runs[0] + 1 > 0:
      assert YES not in info[:last-runs[0]+1]
      if MAYBE in info[:last-runs[0]+1]:
        print "existing run can't reach start of window:", info, runs
        info[:last-runs[0]+1] = [NO] * len(info[:last-runs[0]+1])
        return info

  if info[0] == MAYBE and NO in info:
    leading = 0
    while info[leading] != NO: leading += 1
    if leading < runs[0]:
      assert YES not in info[:leading]
      print "leading maybes can't satisfy first run:\n", info, runs, leading
      info[:leading] = [NO] * leading
      print info, runs
      return info
  if info[-1] == MAYBE and NO in info:
    trailing = 0
    while info[-trailing-1] != NO: trailing += 1
    if trailing < runs[-1]:
      assert YES not in info[-trailing:]
      print "trailing maybes can't satisfy last run\n", info, runs, trailing
      info[-trailing:] = [NO] * trailing
      print info, runs
      return info

  #brute force made progress:
  #['?', '?', 'y', '?', '?', '?', '?', '?', 'n', '?', '?', '?', '?', '?'] [5, 5] -->
  #['?', '?', 'y', 'y', 'y', '?', '?', 'n', 'n', 'y', 'y', 'y', 'y', 'y'] [5, 5]
  if len(runs) > 1 and NO in info:
    leading = 0
    while info[leading] in [YES, MAYBE]:
      leading += 1
    if (leading < runs[0] + runs[1] and 
      info[leading:].count(YES) + info[leading:].count(MAYBE) < sum(runs)):
      print "leading maybes can't satisfy first two runs, and rest can't satisfy all:\n", info, runs
      print "left:\n", info[:leading], runs[:1]
      print "right:\n", info[leading:], runs[1:]
      info[:leading] = update(info[:leading], runs[:1], allow_brute_force)
      info[leading:] = update(info[leading:], runs[1:], allow_brute_force)

    trailing = 0
    while info[-trailing-1] in [YES, MAYBE]:
      trailing += 1
    if (trailing < runs[-1] + runs[-2] and
      info[:-trailing-1].count(YES) + info[:-trailing-1].count(MAYBE) < sum(runs)):
      print "trailing maybes can't satisfy last two runs, and rest can't satisfy all:\n", info, runs
      print "left:\n", info[:-trailing-1], runs[:-1]
      print "right:\n", info[-trailing-1:], runs[-1:]
      info[:-trailing-1] = update(info[:-trailing-1], runs[:-1], allow_brute_force)
      info[-trailing-1:] = update(info[-trailing-1:], runs[-1:], allow_brute_force)

  #brute force made progress:
  #['?', 'y', 'n', '?', 'n', 'n', 'n', 'n', 'n', '?', 'n', 'y', '?'] [2, 2] -->
  #['y', 'y', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'n', 'y', 'y'] [2, 2]
  if MAYBE in info and min(runs) > min(count_runs(info, [MAYBE])):
    # remove any MAYBE runs with length < min
    shortest = min(runs)
    start = 0
    end = 0
    while True:
      if end == len(info) or (end < len(info) and info[end] == NO):
        if end - start > 0 and end - start < shortest:
          assert YES not in info[start:end]
          print 'stomping too-short run [%d, %d]:\n' % (start, end), info, runs, len(info)
          info[start:end] = [NO] * len(info[start:end])
          return info
        start = end+1
      if end == len(info): break
      end += 1
    
  if YES in info and max(runs) == max(count_runs(info)):
    longest = max(runs)
    # largest run should be capped
    unique = False
    appearances = [i for i,x in enumerate(runs) if x == longest]
    if len(appearances) == 1:
      unique = True
    run = 0
    for i in range(len(info)):
      cell = info[i]
      if cell != YES:
        if run == longest:
          if i < len(info) and info[i] == MAYBE:
            print 'capping end of longest run:\n', info, runs
            assert info[i] != YES
            info[i] = NO
            return info
          if i - longest - 1 >= 0 and info[i - longest - 1] == MAYBE:
            assert info[i - longest - 1] != YES
            print 'capping start of longest run:\n', info, runs
            info[i - longest - 1] = NO
            return info
          if unique:
            pivot = appearances[0]
            print 'splitting around unique longest run:\n',
            print info, runs
            print 'left:\n',info[:i - longest - 1], runs[:pivot]
            print 'right:\n',info[i:], runs[pivot+1:]
            info[:i - longest - 1] = update(info[:i - longest - 1], runs[:pivot], allow_brute_force)
            info[i:] = update(info[i:], runs[pivot+1:], allow_brute_force)
        run = 0
      elif cell == YES:
        run += 1

  info = brute_force(info, runs, allow_brute_force)

  return info


def all_bits(length):
  for i in xrange(2**length):
    bits = bin(i)[2:]
    bits = '0' * (length - len(bits)) + bits
    yield [b == '1' and YES or NO for b in bits]

def count_runs(info, to_count=[YES]):
  runs = [0]
  for cell in info:
    if cell not in to_count and runs[-1] > 0:
      runs.append(0)
    elif cell in to_count:
      runs[-1] += 1
  if runs[-1] == 0: runs = runs[:-1]
  return runs

def validate(info, expected_runs):
  #print 'validate(%s, %s)' % (info, expected_runs)
  assert MAYBE not in info
  return count_runs(info) == expected_runs

def brute_force(info, runs, allow_brute_force):
  unknowns = info.count(MAYBE)
  if unknowns > allow_brute_force or unknowns == 0: return info

  print info, runs

  possible = all_bits(unknowns)
  always_yes = [True] * unknowns
  always_no = [True] * unknowns
  possibilities = 0
  for p in possible:
    maybe_info = list(info)  # copy
    used = 0
    for i in range(len(maybe_info)):
      if maybe_info[i] == MAYBE:
        maybe_info[i] = p[used]
        used += 1
    assert MAYBE not in maybe_info
    assert used == len(p)
    if not validate(maybe_info, runs):
      continue

    possibilities += 1
    for i in range(unknowns):
      if p[i] == YES:
        always_no[i] = False
      if p[i] == NO:
        always_yes[i] = False

  assert possibilities > 0

  if True in always_yes or True in always_no:
    print 'brute force made progress:'
    print info, runs, '-->'
    used = 0
    for i in range(len(info)):
      if info[i] == MAYBE:
        assert not (always_yes[used] and always_no[used])
        if always_yes[used]: info[i] = YES
        if always_no[used]: info[i] = NO
        used +=1
    print info, runs

  return info

def update_row(grid, r, runs, allow_brute_force=0):
  #print 'update_row(%s, %s, %s)' % (grid, r, runs)
  row = grid[r][:]
  row = update(row, runs, allow_brute_force)
  #print 'row updated to %s' % row
  changed = False
  for i in range(len(row)):
    if (grid[r][i] != row[i]):
      changed = True
      #print 'updated %s -> %s' % (grid[r][i], row[i])
    grid[r][i] = row[i]
  return changed

def update_col(grid, c, runs, allow_brute_force=0):
  #print 'update_col(%s, %s, %s)' % (grid, c, runs)
  col = [row[c] for row in grid]
  col = update(col, runs, allow_brute_force)
  #print 'col updated to %s' % col
  changed = False
  for i in range(len(col)):
    if (grid[i][c] != col[i]):
      changed = True
      #print 'updated %s -> %s' % (grid[i][c], col[i])
    grid[i][c] = col[i]
  return changed

def update_all(grid, row_runs, col_runs, allow_brute_force=0):
  changed = False
  for r in range(len(grid)):
    #display(grid, row_runs, col_runs)
    if update_row(grid, r, row_runs[r], allow_brute_force): changed = True
  for l in range(len(grid[0])):
    #display(grid, row_runs, col_runs)
    if update_col(grid, l, col_runs[l], allow_brute_force): changed = True
  return changed

def solved(grid):
  for row in grid:
    if MAYBE in row: return False
  return True

def solve(grid, row_runs, col_runs):
  iterations = 0
  while update_all(grid, row_runs, col_runs):
    print 'iterations:', iterations
    iterations += 1
  print 'best possible with heuristics:'
  display(grid, row_runs, col_runs)
  if solved(grid): return
  brute = 0
  while not solved(grid) and (brute < len(grid) or brute < len(grid[0])):
    brute += 1
    print 'allowing brute force with up to %d unknowns...' % brute
    while update_all(grid, row_runs, col_runs, allow_brute_force=brute):
      print 'iterations:', iterations
      iterations += 1
  print 'best possible with brute force:'
  display(grid, row_runs, col_runs)

def display(grid, all_row_runs, all_col_runs):
  result = ''

  max_row_runs_length = max([len(' '.join([str(run) for run in row_runs])) for row_runs in all_row_runs])

  max_col_runs = max(len(col_run) for col_run in all_col_runs)
  for i in range(max_col_runs):
    result += '  ' + ' ' * max_row_runs_length
    for col_runs in all_col_runs:
      if i < len(col_runs):
        col_run = str(col_runs[i])
        if len(col_run) < 2:
          result += ' '
        result += col_run
      else:
        result += '  '
    result += '\n'

  result += ' '*max_row_runs_length + ' +' + '--'*len(grid[0]) + '-+\n'
  for row,row_runs in zip(grid, all_row_runs):
    row_runs = ' '.join([str(run) for run in row_runs])
    result += ' ' * (max_row_runs_length - len(row_runs)) + row_runs
    result += ' |'
    for cell in row:
      result += ' '
      if cell == YES:
        result += 'O'
      if cell == NO:
        result += ' '
      if cell == MAYBE:
        result += '?'
    result += ' |\n'
  result += ' '*max_row_runs_length + ' +' + '--'*len(grid[0]) + '-+\n'
  print result,

def init_grid(num_rows, num_columns):
  return [[MAYBE for c in range(num_columns)] for r in range(num_rows)]

'''
grid = init_grid(3,4)
row_runs = [[1], [2,3], [4,5,6]]
col_runs = [[1], [2,3], [4,5,6], [7,8,9,10]]

display(grid, row_runs, col_runs)
solve(grid, row_runs, col_runs)
'''

def parse_runs(lines):
  row_runs = []
  col_runs = []
  for line in lines:
    line = line.strip()
    if line == 'rows':
      mode = 'rows'
      continue
    if line == 'cols':
      mode = 'cols'
      continue

    runs = [int(run) for run in line.split(' ')]
    if mode == 'rows':
      row_runs.append(runs)
    if mode == 'cols':
      col_runs.append(runs)
  return init_grid(len(row_runs), len(col_runs)), row_runs, col_runs

import sys

grid, row_runs, col_runs = parse_runs(sys.stdin.readlines())
display(grid, row_runs, col_runs)
solve(grid, row_runs, col_runs)
