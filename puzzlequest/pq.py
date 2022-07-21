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
#    EMPTY = 0
#    GREEN = 1
#    RED = 2
#    YELLOW = 3
#    BLUE = 4
#    SKULL = 5
#    STAR = 6
#    COIN = 7
#    BIG_SKULL = 8
#    WILD = 9
# more wilds

MANA_GEMS = [Gem.GREEN, Gem.RED, Gem.YELLOW, Gem.BLUE]
SPAWNABLE_GEMS = MANA_GEMS + [Gem.SKULL, Gem.STAR, Gem.COIN]

PRETTY_PRINT = {
    Gem.EMPTY: '⬛',
    Gem.GREEN: '🟩',
    Gem.RED: '🟥',
    Gem.YELLOW: '🟨',
    Gem.BLUE: '🟦',
    Gem.SKULL: '💀',
    Gem.STAR: '🔯',
    Gem.COIN: '💰',
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
    for k,v in d.items():
        result += f'\t{k}:\t{v}\n'
    result += '}'
    return result

EMPTY_BOARD = ((Gem.EMPTY,)*8,)*8

# print(pretty_print_board(EMPTY_BOARD))

def mutable_board(b):
    if isinstance(b, list): return b
    return [list(row) for row in b]

def immutable_board(b):
    if isinstance(b, tuple): return b
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
            yield r,c
            
def fill_missing(b, gem_source):
    assert isinstance(b, list)
    for r,c in all_coordinates():
        if b[r][c] == Gem.EMPTY:
            b[r][c] = gem_source()
    return b

def match_finder_order(b):
    for r in range(8):
        for c in range(8):
            yield (r,c,b[r][c])
        yield None, None, None
    yield None, None, None
    for c in range(8):
        for r in range(8):
            yield (r,c,b[r][c])
        yield None, None, None
    yield None, None, None
    
def assemble_run(r):
    assert len(r) >= 3
    g = r[0][2]
    rcs = tuple((r,c) for r,c,g in r)
    return (g, rcs)
    
def find_matches(b):
    result = []
    run = []
    for r,c,g in match_finder_order(b):
        if run and run[-1][-1] != g:
            if len(run) >= 3 and g != Gem.EMPTY:
                result.append(assemble_run(run))
            run = []
        if g != Gem.EMPTY:
            run.append((r,c,g))
    return result

def purge_matches(b, matches):
    assert isinstance(b, list)
    for g, rcs in matches:
        for r,c in rcs:
            b[r][c] = Gem.EMPTY

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

def resolve_matches(b, gem_source, recursive=True, display=False):
    assert isinstance(b, list)
    yields = []
    free_move = False
    cascade = 0
    while True:
        matches = find_matches(b)
        # print('found matches:', matches)
        if not matches: break
        for m in matches:
            g,n = m[0], len(m[1])
            if n >= 4: free_move = True
            yields.append((g,n))

        cascade += 1
        purge_matches(b, matches)
        if display: print('matches purged:', pretty_print_board(b), sep='\n')
        if display and free_move: print('FREE MOVE!')
        gravity(b)
        if display: print('gravity applied:', pretty_print_board(b), sep='\n')
        fill_missing(b, gem_source)
        if display: print('gaps filled:', pretty_print_board(b), sep='\n')
        if not recursive: break
    if display:
        print(f'board settled after {cascade} iteration(s).')
        if cascade >= 5:
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
    for r,c in all_coordinates():
        if r < 7: yield (Move.SWAP, Swap.VERTICAL, (r,c))
        if c < 7: yield (Move.SWAP, Swap.HORIZONTAL, (r,c))
    if permit_spells:
        for src in MANA_GEMS:
            for dst in MANA_GEMS:
                if src != dst:
                    yield (Move.SPELL, 'convert', (src, dst))

def consider_moves(b, gem_source, recursive=True, permit_spells=False):
    b = immutable_board(b)
    possible_yields = {}
    for move in possible_moves(permit_spells=permit_spells):
        # print("Considering the results of move:", move)
        yields, free_move = try_move(mutable_board(b), move, gem_source, recursive)
        if yields or move[0] == Move.SPELL:
            possible_yields[move] = yields, free_move
    return possible_yields

def try_move(b, move, gem_source, recursive, display=False):
    assert isinstance(b, list)
    if move[0] == Move.SWAP:
        swap_direction, rc = move[1:]
        r,c = rc
        if swap_direction == Swap.HORIZONTAL:
            b[r][c], b[r][c+1] = b[r][c+1], b[r][c]
        elif swap_direction == Swap.VERTICAL:
            b[r][c], b[r+1][c] = b[r+1][c], b[r][c]
        else: assert False
    elif move[0] == Move.SPELL:
        name, args = move[1:]
        cast_spell(b, name, args)
    if display: print('after move:', pretty_print_board(b), sep='\n')
    return resolve_matches(b, gem_source, recursive, display)

def pick_first_move(moves_and_yields):
    for s,y in moves_and_yields.items():
        return s

def pick_highest_move(moves_and_yields):
    return min(moves_and_yields.items(), key=lambda sy: sy[0][0])[0]

def pick_lowest_move(moves_and_yields):
    return max(moves_and_yields.items(), key=lambda sy: sy[0][0])[0]

def pick_highest_yield(moves_and_yields):
    mys = list(moves_and_yields.items())
    
    # pick up a free move whenever possible:
    mys_freemove = list(filter(lambda my: my[1][1], mys))
    if len(mys_freemove) > 0: mys = mys_freemove
    
    return max(mys, key=lambda my: sum(n for g,n in my[1][0]))[0]

def cast_spell(b, name, args):
    if name == 'convert':
        src,dst = args
        for r,c in all_coordinates():
            if b[r][c] == src:
                b[r][c] = dst
    else:
        assert False

def spells_known():
    return ['red to blue']

def play(b, move_picker=pick_first_move):
    total_yields = collections.Counter()
    for turn in range(10):
        basic_moves_and_yields = consider_moves(b, no_gem, recursive=False, permit_spells=False)
        while len(basic_moves_and_yields) == 0:
            print("NO MOVES AVAILABLE")
            # TODO(durandal) mana drain!
            b = random_board_no_matches()
            # TODO(durandal): random_board_no_matches_some_moves()?
            basic_moves_and_yields = consider_moves(b, no_gem, recursive=False, permit_spells=False)

        moves_and_yields = consider_moves(b, no_gem, recursive=True, permit_spells=True)
        print('available moves (recursive):', pretty_print_dict(moves_and_yields))
        move = move_picker(moves_and_yields)
        print('moving:', move)
        yields, free_move = try_move(b, move, random_gem, recursive=True, display=True)
        assert len(yields) > 0
        for g,n in yields:
            total_yields[g] += n
    print(f'simulation ended after turn {turn}')
    print(pretty_print_board(b))
    return total_yields
        

def main():
    b = random_board_no_matches()
    print(pretty_print_board(b))
    final_yields = play(b, move_picker=pick_highest_yield)
    print('final yields:', final_yields)

main()
