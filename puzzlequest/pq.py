from enum import Enum
import random
import collections


class Gem(Enum):
  EMPTY = '⬛'
  GREEN = '🟩'
  RED = '🟥'
  YELLOW = '🟨'
  BLUE = '🟦'
  SKULL = '💀'
  STAR = '🔯'
  COIN = '💰'
  BIG_SKULL = '☠️'
  WILD2 = '🍭2'
  WILD3 = '🍭3'
  WILD4 = '🍭4'
  WILD5 = '🍭5'
  WILD6 = '🍭6'  # TODO(durandal): more wilds


MANA_GEMS = [Gem.GREEN, Gem.RED, Gem.YELLOW, Gem.BLUE]
SPAWNABLE_GEMS = MANA_GEMS + [Gem.SKULL, Gem.STAR, Gem.COIN]
WILD_GEMS = [Gem.WILD2, Gem.WILD3, Gem.WILD4, Gem.WILD5, Gem.WILD6]
SKULL_GEMS = [Gem.SKULL, Gem.BIG_SKULL]

PRETTY_PRINT = {
    Gem.EMPTY: '⬛',
    Gem.GREEN: '🟩',
    Gem.RED: '🟥',
    Gem.YELLOW: '🟨',
    Gem.BLUE: '🟦',
    Gem.SKULL: '💀',
    Gem.STAR: '🔯',
    Gem.COIN: '💰',
    Gem.BIG_SKULL: '☠️',
    Gem.WILD2: '[2]',  # '🍭',
    Gem.WILD3: '[3]',  # '🍭',
    Gem.WILD4: '[4]',  # '🍭',
    Gem.WILD5: '[5]',  # '🍭',
    Gem.WILD6: '[6]',  # '🍭',
}


def pretty_print_board(b):
  result = ('--'*8).join('++') + '\n'
  for line in b:
    result += '|'
    for cell in line:
      result += PRETTY_PRINT[cell]
    result += '|\n'
  result += ('--'*8).join('++')
  return result


def pretty_print_dict(d):
  result = '{\n'
  for k, v in d.items():
    result += f'\t{k}:\t{v}\n'
  result += '}'
  return result


EMPTY_BOARD = ((Gem.EMPTY,)*8,)*8

# print(pretty_print_board(EMPTY_BOARD))


def mutable_board(b):
  if isinstance(b, list):
    return b
  return [list(row) for row in b]


def immutable_board(b):
  if isinstance(b, tuple):
    return b
  return tuple(tuple(row) for row in b)


def random_board():
  return fill_missing(mutable_board(EMPTY_BOARD), random_gem)


def random_gem():
  return random.choice(SPAWNABLE_GEMS)


def no_gem():
  return Gem.EMPTY


def gem_from_pool():
  # TODO(durandal)
  pass


def all_coordinates():
  for r in range(8):
    for c in range(8):
      yield r, c


def fill_missing(b, gem_source):
  assert isinstance(b, list)
  for r, c in all_coordinates():
    if b[r][c] == Gem.EMPTY:
      b[r][c] = gem_source()
  return b


def match_finder_order(b):
  for r in range(8):
    for c in range(8):
      yield (r, c, b[r][c])
    yield None, None, None
  yield None, None, None
  for c in range(8):
    for r in range(8):
      yield (r, c, b[r][c])
    yield None, None, None
  yield None, None, None


def run_yield(gs):
  if any(g in WILD_GEMS for g in gs):
    actual_g = None
    mana_seen = 0
    total_mult = 1
    for g in gs:
      if g not in WILD_GEMS:
        actual_g = g
        mana_seen += 1
      else:
        total_mult *= (WILD_GEMS.index(g) + 2)
    if mana_seen == 0:
      # Wilds can match other wilds, but there does need to be
      # a mana gem somewhere in the run
      return None
    return {actual_g: mana_seen * total_mult}
  if gs[0] in (Gem.BIG_SKULL, Gem.SKULL):
    # TODO(durandal): big skulls explode
    return {Gem.SKULL: len(gs) + sum(4 for g in gs if g == Gem.BIG_SKULL)}
  return {gs[0]: len(gs)}


def assemble_run(run, board):
  assert len(run) >= 3
  coords_cleared = tuple((r, c) for r, c, g in run)
  y = run_yield([g for r, c, g in run])
  return (y, coords_cleared)


def can_match_gem(g1, g2):
  return (g1 == g2
          or (g1 in MANA_GEMS and g2 in WILD_GEMS)
          or (g2 in MANA_GEMS and g1 in WILD_GEMS)
          or (g1 in SKULL_GEMS and g2 in SKULL_GEMS)
          )


def can_match_partial_run(g, gs):
  return all(can_match_gem(g, g2) for g2 in gs)


def find_matches(b):
  result = []
  run = []
  for r, c, g in match_finder_order(b):
    if run and not can_match_partial_run(g, [prev[2] for prev in run]):
      if len(run) >= 3 and g != Gem.EMPTY:
        assembled_run = assemble_run(run, b)
        if assembled_run[0]:
          result.append(assembled_run)
      run = []
    if g != Gem.EMPTY:
      run.append((r, c, g))
  return result


def neighbors(r, c):
  for dr in [-1, 0, 1]:
    r2 = r + dr
    if r2 not in range(0, 8):
      continue
    for dc in [-1, 0, 1]:
      c2 = c + dc
      if c2 not in range(0, 8):
        continue
      yield (r2, c2)


def purge_matches(b, matches):
  total_yields = collections.Counter()
  already_destroyed = set()
  to_destroy = set()
  for y, coords_cleared in matches:
    for r, c in coords_cleared:
      g = b[r][c]
      already_destroyed.add((r, c))
      if g == Gem.BIG_SKULL:
        for r2, c2 in neighbors(r, c):
          to_destroy.add((r2, c2))
      b[r][c] = Gem.EMPTY
  return destroy_gems(b, to_destroy - already_destroyed)


def destroy_gems(b, to_destroy, benefit=True):
  assert isinstance(b, list)

  to_destroy = collections.deque(to_destroy)
  total_yields = collections.Counter()
  while len(to_destroy) > 0:
    r, c = to_destroy.pop()
    g = b[r][c]
    if g == Gem.EMPTY:
      continue
    if benefit:
      if g == Gem.BIG_SKULL:
        for r2, c2 in neighbors(r, c):
          to_destroy.append((r2, c2))
        total_yields[Gem.SKULL] += 5
      else:
        total_yields[g] += 1

    b[r][c] = Gem.EMPTY

  return total_yields


def gravity(b):
  assert isinstance(b, list)
  for r in range(8-1, 0, -1):  # deliberately excluding 0
    for c in range(8):
      if b[r][c] == Gem.EMPTY:
        # find non-empty gem above:
        for r2 in range(r, -1, -1):
          if b[r2][c] != Gem.EMPTY:
            b[r][c], b[r2][c] = b[r2][c], b[r][c]
            break


def resolve_matches(b, gem_source, cascade=True, display=False):
  assert isinstance(b, list)
  yields = collections.Counter()
  free_move = False
  cascade_len = 0
  while True:
    matches = find_matches(b)
    # print('found matches:', matches)
    if not matches:
      break
    for y, coords in matches:
      if len(coords) >= 4:
        free_move = True
      yields += y

    cascade_len += 1
    yields += purge_matches(b, matches)
    if display:
      print('matches purged:', pretty_print_board(b), sep='\n')
    if display and free_move:
      print('FREE MOVE!')
    gravity(b)
    if display:
      print('gravity applied:', pretty_print_board(b), sep='\n')
    fill_missing(b, gem_source)
    if display:
      print('gaps filled:', pretty_print_board(b), sep='\n')
    if not cascade:
      break
  if display:
    print(f'board settled after {cascade_len} iteration(s).')
    if cascade_len >= 5:
      print("HEROIC EFFORT!")
    print('Actual yields:', yields)
  return yields, free_move


def random_board_no_matches():
  b = mutable_board(random_board())
  resolve_matches(b, random_gem)
  return b


class Move(Enum):
  SWAP = 1
  SPELL = 2


class Swap(Enum):
  VERTICAL = 1
  HORIZONTAL = 2


def possible_moves(permit_spells=False):
  for r, c in all_coordinates():
    if r < 7:
      yield (Move.SWAP, Swap.VERTICAL, (r, c))
    if c < 7:
      yield (Move.SWAP, Swap.HORIZONTAL, (r, c))
  if permit_spells:
    for src in MANA_GEMS:
      for dst in MANA_GEMS:
        if src != dst:
          yield (Move.SPELL, 'convert', (src, dst))


def consider_moves(b, gem_source=no_gem, cascade=True, permit_spells=False):
  b = immutable_board(b)
  possible_yields = {}
  for move in possible_moves(permit_spells=permit_spells):
    # print("Considering the results of move:", move)
    yields, free_move = try_move(mutable_board(b), move, gem_source, cascade)
    if yields or move[0] == Move.SPELL:
      possible_yields[move] = yields, free_move
  return possible_yields


def try_move(b, move, gem_source, cascade, display=False):
  assert isinstance(b, list)
  if move[0] == Move.SWAP:
    swap_direction, rc = move[1:]
    r, c = rc
    if swap_direction == Swap.HORIZONTAL:
      b[r][c], b[r][c+1] = b[r][c+1], b[r][c]
    elif swap_direction == Swap.VERTICAL:
      b[r][c], b[r+1][c] = b[r+1][c], b[r][c]
    else:
      assert False
  elif move[0] == Move.SPELL:
    name, args = move[1:]
    cast_spell(b, name, args)
  if display:
    print('after move:', pretty_print_board(b), sep='\n')
  return resolve_matches(b, gem_source, cascade, display)


def pick_first_move(moves_and_yields):
  for s, y in moves_and_yields.items():
    return s


def pick_highest_move(moves_and_yields):
  return min(moves_and_yields.items(), key=lambda sy: sy[0][0])[0]


def pick_lowest_move(moves_and_yields):
  return max(moves_and_yields.items(), key=lambda sy: sy[0][0])[0]


def pick_highest_yield(moves_and_yields):
  mys = list(moves_and_yields.items())

  # pick up a free move whenever possible:
  mys_freemove = list(filter(lambda my: my[1][1], mys))
  if len(mys_freemove) > 0:
    mys = mys_freemove

  return max(mys, key=lambda my: sum(y for g, y in my[1][0].items()))[0]


def cast_spell(b, name, args):
  if name == 'convert':
    src, dst = args
    for r, c in all_coordinates():
      if b[r][c] == src:
        b[r][c] = dst
  else:
    assert False


def spells_known():
  return ['red to blue']


def play(b, move_picker=pick_first_move):
  total_yields = collections.Counter()
  for turn in range(10):
    basic_moves_and_yields = consider_moves(
        b, cascade=False, permit_spells=False)
    while len(basic_moves_and_yields) == 0:
      print("NO MOVES AVAILABLE")
      # TODO(durandal) mana drain!
      b = random_board_no_matches()
      # TODO(durandal): random_board_no_matches_some_moves()?
      basic_moves_and_yields = consider_moves(
          b, cascade=False, permit_spells=False)

    moves_and_yields = consider_moves(
        b, cascade=True, permit_spells=True)
    print('available moves (cascade):', pretty_print_dict(moves_and_yields))
    move = move_picker(moves_and_yields)
    print('moving:', move)
    yields, free_move = try_move(
        b, move, random_gem, cascade=True, display=True)
    assert len(yields) > 0
    total_yields += yields
  print(f'simulation ended after turn {turn}')
  print(pretty_print_board(b))
  return total_yields


def main():
  b = random_board_no_matches()
  print(pretty_print_board(b))
  final_yields = play(b, move_picker=pick_highest_yield)
  print('final yields:', final_yields)


if __name__ == '__main__':
  main()
