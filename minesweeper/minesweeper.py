import random

MAX_ROWS = 40
MAX_COLS = 140

HEADER = '+' + ('-' * MAX_COLS) + '+\n'
FOOTER = HEADER

def renderMines(mines):
  result = HEADER
  for r in range(MAX_ROWS):
    result += '|'
    for c in range(MAX_COLS):
      if (r,c) not in mines:
        result += str(adjacentMines(mines, r, c) or ' ')
      else: result += '*'
    result += '|\n'
  result += FOOTER
  return result

def adjacentMines(mines, r, c):
  assert (r,c) not in mines
  return sum(1 for dr in [-1, 0, 1] for dc in [-1, 0, 1] if (r+dr, c+dc) in mines)

def addMine(mines, r, c):
  mines[(r,c)] = True

def renderView(view):
  result = HEADER
  for r in range(MAX_ROWS):
    result += '|'
    for c in range(MAX_COLS):
      if (r,c) not in view: result += '.'
      elif view[(r,c)] == 0: result += ' '
      else: result += str(view[(r,c)])
    result += '|\n'
  result += FOOTER
  return result

def step(mines, view, r, c):
  if (r,c) in view: return True
  if (r,c) in mines:
    view[(r,c)] = '*'
    return False
  view[(r,c)] = adjacentMines(mines, r, c)
  if view[(r,c)] == 0:
    for dr in [-1, 0, 1]:
      for dc in [-1, 0, 1]:
        assert r < 0 or r >= MAX_ROWS or c < 0 or c >= MAX_COLS or step(mines, view, r+dr, c+dc)
  return True

def mark(view, r, c):
  if (r,c) in view: return False
  view[(r,c)] = 'X'

def unmark(view, r, c):
  del view[(r,c)]

def autoplay(view):
  for r in range(MAX_ROWS):
    for c in range(MAX_COLS):
      known = view.get((r,c))
      if known == 'X': continue
      if known is None: continue
      if known == 0: continue
      if known == 8: continue
      assert known > 0 and known < 8

      unknown_neighbors = [(dr,dc) for dr in [-1, 0, 1] for dc in [-1, 0, 1] if view.get((r+dr, c+dc)) == None
                           and r+dr >= 0 and r+dr < MAX_COLS and c+dc >= 0 and c+dc < MAX_COLS]
      if not unknown_neighbors: continue

      marked_neighbors = [(dr,dc) for dr in [-1, 0, 1] for dc in [-1, 0, 1] if view.get((r+dr, c+dc)) == 'X'
                          and r+dr >= 0 and r+dr < MAX_COLS and c+dc >= 0 and c+dc < MAX_COLS]
      assert len(marked_neighbors) + len(unknown_neighbors) >= known

      if len(marked_neighbors) + len(unknown_neighbors) == known:
        dr,dc = unknown_neighbors[0]
        return (r+dr, c+dc), 'mark'

      if len(marked_neighbors) == known:
        dr,dc = unknown_neighbors[0]
        return (r+dr, c+dc), 'step'

  valid_steps = [(r,c) for r in range(MAX_ROWS) for c in range(MAX_COLS) if (r,c) not in view]
  return random.choice(valid_steps), 'step'

def generateMines():
  mines = {}
  for m in range(int(MAX_ROWS*MAX_COLS * 0.15)):
    addMine(mines, random.randrange(MAX_ROWS), random.randrange(MAX_COLS))
  return mines

def demo():
  mines = generateMines()
  print renderMines(mines)

  view = {}
  print renderView(view)

  alive = True
  while alive:
    target, action = autoplay(view)
    r,c = target
    if action == 'step':
      alive = step(mines, view, r, c)
    elif action == 'mark':
      mark(view, r, c)
    else:
      assert False
    print renderView(view)

demo()