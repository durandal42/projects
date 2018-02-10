YES = 'O'
NO = ' '
MAYBE = '?'

# Attempt to refine knowledge about a list of entries.
# This might be called with a subset of a full puzzle's row or column, so don't
# make assumptions about there definitely being at least one run, etc.
#
# Args:
#   info: a list of YES|NO|MAYBE, representing either a row or a column
#   runs: a list of ints, each specifying the length of a consecutive run of YES's
#   allow_brute_force: if all heuristics fail, brute force up to this many unknowns
# Returns:
#   a new list of YES|NO|MAYBE, hopefully with fewer MAYBE's
def update(info, runs, allow_brute_force=0):
  #print 'update(%s, %s)' % (info, runs)

  # break early if nothing to do
  if not MAYBE in info:
    #print 'no uncertainty here:\n',info, runs
    assert validate(info, runs)
    return info

  # if there are no runs remaining, everything must be NO
  if len(runs) == 0:
    print info, runs
    assert YES not in info
    print 'no runs remaining:\n', info, runs
    return [NO] * len(info)

  # if one run covers the entire range, everything must be YES
  if len(runs) == 1 and runs[0] == len(info):
    assert NO not in info
    print 'only run fills whole range:\n', info, runs
    return [YES] * len(info)

  # if there's exactly enough room for all runs, fill them in.
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

  # TODO(durandal): this is pretty gross if there are a lot of leading/trailing NOs.
  # trim leading NOs
  if info[0] == NO:
    info[1:] = update(info[1:], runs, allow_brute_force)
    return info
  # trim trailing NOs
  if info[-1] == NO:
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

  # Long run (> half info length) forces some middle squares to be YES.
  if len(runs) == 1 and runs[0]*2 > len(info):
    gap = len(info) - runs[0]
    assert NO not in info[gap:-gap]
    if MAYBE in info[gap:-gap]:
      print 'only run is large enough to confirm middle:\n', info, runs
      info[gap:-gap] = [YES] * (len(info) - gap*2)
      return info

  # Where are the YES's?
  yes_locations = [i for i,c in enumerate(info) if c == YES]
  # How many YES's are there?
  yes_count = len(yes_locations)
  assert sum(runs) >= yes_count

  # If we have enough YES's, all remaining MAYBE's are NO's.
  if sum(runs) == yes_count:
    if MAYBE in info:
      print 'all runs accounted for:\n', info, runs
      info = [x == YES and YES or NO for x in info]
      print info, runs
    return info

  # Exactly one run and the presence of a YES gives us some options:
  if len(runs) == 1 and YES in info:
    first = yes_locations[0]
    last = yes_locations[-1]
    # MAYBE's between first and last YES must also be YES
    if MAYBE in info[first:last+1]:
      print 'hole found:', info, runs
      assert NO not in info[first:last+1]
      info[first:last+1] = [YES] * (last - first + 1)
      return info
    # If every square from the first YES onward were all YES, could we reach the end of the window?
    # If not, squares beyond our reach must be no.
    if first + runs[0] < len(info):
      assert YES not in info[first+runs[0]:]
      if MAYBE in info[first+runs[0]:]:
        print "existing run can't reach end of window:", info, runs
        info[first+runs[0]:] = [NO] * len(info[first+runs[0]:])
        return info
    # Same deal reaching backward:
    if last - runs[0] + 1 > 0:
      assert YES not in info[:last-runs[0]+1]
      if MAYBE in info[:last-runs[0]+1]:
        print "existing run can't reach start of window:", info, runs
        info[:last-runs[0]+1] = [NO] * len(info[:last-runs[0]+1])
        return info

  # If there's no room for the first run before the first NO, all MAYBE's before that are NO's
  if info[0] == MAYBE and NO in info:
    leading = 0
    while info[leading] != NO: leading += 1
    if leading < runs[0]:
      assert YES not in info[:leading]
      print "leading maybes can't satisfy first run:\n", info, runs, leading
      info[:leading] = [NO] * leading
      print info, runs
      return info
  # Same deal from the end:
  if info[-1] == MAYBE and NO in info:
    trailing = 0
    while info[-trailing-1] != NO: trailing += 1
    if trailing < runs[-1]:
      assert YES not in info[-trailing:]
      print "trailing maybes can't satisfy last run\n", info, runs, trailing
      info[-trailing:] = [NO] * trailing
      print info, runs
      return info

  # Heuristics "learned" from brute force progress:

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

# given a length, generate every possible set of YES/NO sequences of that length
# TODO(durandal): by the time we call this, we know how many YES's need to appear;
#   instead generate all permutations of that many YES's and the complementary number of NO's
import perm_unique
def all_bits(num_yes, num_no):
  for p in perm_unique.perm_unique([YES] * num_yes + [NO] * num_no):
    yield p
#  length = num_yes + num_no
#  for i in xrange(2**length):
#    bits = bin(i)[2:]  # binary digits representing i
#    bits = '0' * (length - len(bits)) + bits  # pad with leading 0's
#    yield [b == '1' and YES or NO for b in bits]

# Given a row/column, return a list of runs:
def count_runs(info, to_count=[YES]):
  runs = [0]
  for cell in info:
    if cell not in to_count and runs[-1] > 0:
      runs.append(0)
    elif cell in to_count:
      runs[-1] += 1
  if runs[-1] == 0: runs = runs[:-1]
  return runs

# Given a row/column and the constraints it was supposed to satisfy, see if it does.
def validate(info, expected_runs):
  #print 'validate(%s, %s)' % (info, expected_runs)
  assert MAYBE not in info
  return count_runs(info) == expected_runs

def brute_force(info, runs, allow_brute_force):
  num_unknowns = info.count(MAYBE)
  if num_unknowns == 0:
    # no unknowns at all; already done!
    return info
  if num_unknowns > allow_brute_force:
    # Too many num_unknowns for this brute force level; abort.
    return info

  print 'attempting brute force (level %d) on:' % allow_brute_force, info, runs

  num_yes = info.count(YES)
  num_no = info.count(NO)
  # these have not yet been checked for consistency, or even appropriate count of YES/NO's
  possible = all_bits(sum(runs) - num_yes, len(info) - sum(runs) - num_no)

  # across all consistent possibilities, are any squares *always* YES/NO?
  always_yes = [True] * num_unknowns
  always_no = [True] * num_unknowns

  possibilities = 0
  consistent_possibilities = 0
  for p in possible:
    maybe_info = list(info)  # copy
    used = 0
    for i,_ in enumerate(maybe_info):
      if maybe_info[i] == MAYBE:
        maybe_info[i] = p[used]
        used += 1
    assert MAYBE not in maybe_info  # we filled in all the MAYBE's
    assert used == len(p)  # we used all our bits

    possibilities += 1
    if not validate(maybe_info, runs):  # check for consistency
      continue
    consistent_possibilities += 1

    # update always_yes,always_no with our findings
    for i in range(num_unknowns):
      if p[i] == YES:
        always_no[i] = False
      if p[i] == NO:
        always_yes[i] = False

  print 'considered %d possibilities and found %d consistent ones.' % (possibilities, consistent_possibilities)
  # There'd better be at least one consistent possibility...
  assert consistent_possibilities > 0

  if True in always_yes or True in always_no:
    # At least one square was consistently YES or consistently NO; fill it in.
    print 'brute force made progress:'
    print info, runs, '-->'
    used = 0
    for i,_ in enumerate(info):
      if info[i] == MAYBE:
        assert not (always_yes[used] and always_no[used])
        if always_yes[used]: info[i] = YES
        if always_no[used]: info[i] = NO
        used +=1
    print info, runs

  return info

# Unpack a row from a grid, apply heuristics, and repack results back into the grid.
# return whether anything changed.
def update_row(grid, r, runs, allow_brute_force=0):
  row = grid[r][:]
  row = update(row, runs, allow_brute_force)
  changed = False
  for i in range(len(row)):
    if grid[r][i] != row[i]:
      changed = True
      grid[r][i] = row[i]
  return changed

# Unpack a col from a grid, apply heuristics, and repack results back into the grid.
# return whether anything changed.
def update_col(grid, c, runs, allow_brute_force=0):
  col = [row[c] for row in grid]
  col = update(col, runs, allow_brute_force)
  changed = False
  for i in range(len(col)):
    if grid[i][c] != col[i]:
      changed = True
      grid[i][c] = col[i]
  return changed

# Given a grid and constraints, do one progress pass and return whether progress was made.
def update_all(grid, row_runs, col_runs, allow_brute_force=0):
  changed = False
  for r in range(len(grid)):
    if update_row(grid, r, row_runs[r], allow_brute_force):
      changed = True
  for l in range(len(grid[0])):
    if update_col(grid, l, col_runs[l], allow_brute_force):
      changed = True
  return changed

# Is this grid solved?
def solved(grid):
  for row in grid:
    if MAYBE in row: return False
  return True

# Given a grid and constraints, solve it as best as possible.
def solve(grid, row_runs, col_runs):
  iterations = 0
  for brute in range(max(len(grid), len(grid[0]))):
    if brute > 0:
      print 'allowing brute force with up to %d unknowns...' % brute
    else:
      print 'applying heuristics...'
    # Apply heuristics until they stop making progress:
    while update_all(grid, row_runs, col_runs, allow_brute_force=brute):
      print 'iterations:', iterations
      iterations += 1
    if solved(grid): break
    print 'progress so far:\n', display(grid, row_runs, col_runs)
  if not solved(grid):
    print 'couldn\'t solve even with brute force! (this should never happen)'
  elif brute > 0:
    print 'solved using brute force level %d.', brute
  else:
    print 'solved using heuristics alone.'
  display(grid, row_runs, col_runs)

# Pretty-print a grid and row/column constraints
def display(grid, all_row_runs, all_col_runs):
  result = ''

  # the longest row prefix we'll need to print:
  max_row_runs_length = max([len(' '.join([str(run) for run in row_runs])) for row_runs in all_row_runs])

  # the tallest column header we'll need to print:
  max_col_runs = max(len(col_run) for col_run in all_col_runs)

  # print column headers:
  for i in range(max_col_runs):
    # empty upper-left corner:
    result += '  ' + ' ' * max_row_runs_length

    for col_runs in all_col_runs:
      # if this column has enough runs to need an entry on this line:
      if i < len(col_runs):
        col_run = str(col_runs[i])
        # TODO(durandal): use string format
        if len(col_run) < 2:
          result += ' '
        result += col_run
      else:
        result += '  '
    result += '\n'

  # print upper grid border:
  result += ' '*max_row_runs_length + ' +' + '--'*len(grid[0]) + '-+\n'

  # print rows:
  for row,row_runs in zip(grid, all_row_runs):
    row_runs = ' '.join(str(run) for run in row_runs)
    # padding for short row run label:
    result += ' ' * (max_row_runs_length - len(row_runs)) + row_runs
    # left grid border:
    result += ' |'
    # grid contents:
    result += ' '.join(row)
    # right grid border:
    result += ' |\n'

  # print lower grid border (same as upper):
  result += ' '*max_row_runs_length + ' +' + '--'*len(grid[0]) + '-+\n'

  print result,

# Initialize a blank grid of the appropriate size, full of MAYBE's
def init_grid(num_rows, num_columns):
  return [[MAYBE for c in range(num_columns)] for r in range(num_rows)]

'''
grid = init_grid(3,4)
row_runs = [[1], [2,3], [4,5,6]]
col_runs = [[1], [2,3], [4,5,6], [7,8,9,10]]

display(grid, row_runs, col_runs)
solve(grid, row_runs, col_runs)
'''

# Given lines of text specifying a problem, parse the row and column runs:
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
  return row_runs, col_runs

# "main" function:
# TODO(durandal): use actual python main
import sys
row_runs, col_runs = parse_runs(sys.stdin.readlines())  # TODO(durandal) support input by named file
grid = init_grid(len(row_runs), len(col_runs))
display(grid, row_runs, col_runs)
solve(grid, row_runs, col_runs)
