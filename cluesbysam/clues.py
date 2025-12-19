import itertools
import collections
import functools

# 0 = innocent
# 1 = criminal

SUBJECT_TO_STATUS = {}


def is_criminal(subject):
  return SUBJECT_TO_STATUS[subject] == 1


def is_innocent(subject):
  return not is_criminal(subject)


def criminals(subjects):
  return frozenset(filter(is_criminal, subjects))


def innocents(subjects):
  return frozenset(filter(is_innocent, subjects))


def num_criminals(subjects):
  return sum(1 for s in subjects if is_criminal(s))


def num_innocents(subjects):
  return len(subjects) - num_criminals(subjects)


def evaluate(knowns, claims):
  print("knowns:", knowns)
  for subject, status in knowns.items():
    SUBJECT_TO_STATUS[subject] = status

  unknowns = sorted(set(SUBJECTS) - set(knowns.keys()))
  print("unknowns:", unknowns)
  num_unknowns = len(SUBJECTS) - len(knowns)
  print(f"\nevaluating {len(claims)} claims across 2^{num_unknowns} = {2 ** num_unknowns} possibilities...")

  consistent_statuses_by_unknown_subjects = collections.defaultdict(set)
  for p in itertools.product([0, 1], repeat=num_unknowns):
    # print(p)
    for i, status in enumerate(p):
      SUBJECT_TO_STATUS[unknowns[i]] = status
    # print(SUBJECT_TO_STATUS)
    # print(claims)
    evals = [eval(c) for c in claims]
    # print("->", evals)
    if all(evals):
      # print(p)
      for subject_index, criminal_status in enumerate(p):
        consistent_statuses_by_unknown_subjects[subject_index].add(criminal_status)
  # print(consistent_statuses_by_unknown_subjects)
  assert len(consistent_statuses_by_unknown_subjects) > 0
  print()

  print("discoveries:")
  for i, statuses in consistent_statuses_by_unknown_subjects.items():
    if len(statuses) == 1:
      status = next(iter(statuses))
      # print(f"proved: {subjects[subject_index]} is {status and 'criminal' or 'innocent'}")
      print(f"{unknowns[i]}: {status}, ")


def fill_knowns(claim, knowns):
  for subject, status in knowns.items():
    claim = claim.replace(subject, str(status))
  return claim


def direction(suspect, dr, dc, directly=False):
  result = []
  r, c = LOCATIONS[suspect]
  while True:
    r += dr
    c += dc
    if r not in range(len(GRID)) or c not in range(len(GRID[r])):
      break
    result.append(GRID[r][c])
    if directly:
      break
  # print(f"direction({suspect}, {dr}, {dc}, {directly}) = {result}")
  return frozenset(result)


@functools.cache
def above(suspect, directly=False):
  return direction(suspect, -1, 0, directly)


@functools.cache
def below(suspect, directly=False):
  return direction(suspect, 1, 0, directly)


@functools.cache
def left(suspect, directly=False):
  return direction(suspect, 0, -1, directly)


@functools.cache
def right(suspect, directly=False):
  return direction(suspect, 0, 1, directly)


@functools.cache
def neighbors(suspect):
  result = []
  r1, c1 = LOCATIONS[suspect]
  for dr in [-1, 0, 1]:
    r2 = r1 + dr
    if r2 not in range(len(GRID)):
      continue
    for dc in [-1, 0, 1]:
      if dr == 0 and dc == 0:
        continue
      c2 = c1 + dc
      if c2 not in range(len(GRID[r2])):
        continue
      result.append(GRID[r2][c2])
  print(f"neighbors({suspect}) = {result}")
  return frozenset(result)


@functools.cache
def edges():
  result = set()
  for row in GRID:
    result.add(row[0])
    result.add(row[-1])
  result.update(GRID[0])
  result.update(GRID[-1])
  return frozenset(result)

@functools.cache
def total():
  result = set()
  for row in GRID:
    result.update(row)
  return frozenset(result)


@functools.cache
def corners():
  return frozenset([
      GRID[0][0],
      GRID[-1][0],
      GRID[0][-1],
      GRID[-1][-1],
  ])


@functools.cache
def row(i):
  return frozenset(GRID[i-1])


@functools.cache
def column(s):
  c = "ABCD".index(s)
  return frozenset(row[c] for row in GRID)


@functools.cache
def profession(prof):
  result = []
  for p, s in zip(PROFESSIONS, SUBJECTS):
    if p == prof:
      result.append(s)
  print(f"subjects with profession {prof}: {result}")
  return frozenset(result)


@functools.cache
def directly_connected(s1, s2):
  result = any((s1 in above(s2, directly=True),
                s1 in below(s2, directly=True),
                s1 in left(s2, directly=True),
                s1 in right(s2, directly=True)))
  # print(f'directly_connected({s1}, {s2}): {result}')
  return result


@ functools.cache
def connected(subjects):
  ingroup = list(subjects)[:1]
  outgroup = list(subjects)[1:]
  result = True
  while len(outgroup) > 0 and result == True:
    # print('ingroup:', ingroup)
    # print('outgroup:', outgroup)
    for s1 in outgroup:
      if any(directly_connected(s1, s2) for s2 in ingroup):
        ingroup.append(s1)
        outgroup.remove(s1)
        break
    else:
      result = False
      break
  # print(f"connected({subjects}): {result})")
  return result


# TODO: optimize unreferenced suspects
# TODO: connected
# TODO: professions
GRID = [
    'ABCE',
    'FGHI',
    'JKLM',
    'NRST',
    'UVWZ',
]
SUBJECTS = sorted(set(''.join(GRID)))
print('subjects:', SUBJECTS)
for s in SUBJECTS + ['A', 'B', 'C', 'D']:
  globals()[s] = s

PROFESSIONS = [
    'pilot', 'sleuth', 'pilot', 'sleuth',
    'singer', 'cop', 'farmer', 'cook',
    'pilot', 'painter', 'farmer', 'painter',
    'singer', 'mech', 'cook', 'cook',
    'singer', 'mech', 'cop', 'painter',
]

LOCATIONS = {}
for _r, _row in enumerate(GRID):
  for _c, _cell in enumerate(_row):
    LOCATIONS[_cell] = (_r, _c)
print("locations:", LOCATIONS)

# assert(connected('HLPV'))
# assert(connected(frozenset({'H', 'A', 'P', 'L', 'V'})))

evaluate(
    knowns={
      S:0,
      M:1,
      C:1, H:1, L:0,
      A:0, E:0,
      K:1, R:1, 
      I:0, W:1,
      B:0,
    },
    claims=[
      'is_criminal(M) and num_criminals(neighbors(S)) == 5',
      'connected(innocents(above(W))) and num_innocents(above(W)) == 2',
      'num_criminals(neighbors(B)) > num_criminals(neighbors(Z))',
      'num_criminals(neighbors(C)) == num_criminals(neighbors(Z))',
      'num_innocents(row(1) & corners()) == 2',
      'num_innocents(neighbors(S) & edges()) == 2',
      'num_criminals(column(C)) > num_criminals(column(D))',
      'num_innocents(total()) == 12',
      'num_innocents(row(5)) == 2',

    ])
