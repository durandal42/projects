NUMBERS = [
    "1",
    "2",
    "3",
]
COLORS = [
    "red",
    "green",
    "blue",
]
SHADINGS = [
    "empty",
    "half",
    "full",
]
SYMBOLS = [
    "diamond",
    "squiggle",
    "oval",
]

QUALITIES_SET = [
    NUMBERS,
    COLORS,
    SHADINGS,
    SYMBOLS,
]

FUGUEAL_BORDER_SHAPES = [
    "square",
    "circle",
    "hexagon",
]
FUGUEAL_INNER_SHAPES = [
    "square",
    "circle",
    "triangle",
]

QUALITIES_FUGUEAL = [
    NUMBERS,
    FUGUEAL_BORDER_SHAPES,
    NUMBERS,
    FUGUEAL_INNER_SHAPES,
]

QUALITIES = QUALITIES_SET
QUALITIES = QUALITIES_FUGUEAL
NUM_QUALITIES = len(QUALITIES)
NUM_OPTIONS = len(QUALITIES[0])
assert min(len(qn) for qn in QUALITIES) == max(len(qn) for qn in QUALITIES)

import itertools

def name(c):
    return "(%s)" % " ".join(QUALITIES[i][c[i]] for i in range(NUM_QUALITIES))
def names(cs):
    return "[%s]" % " ".join(name(c) for c in cs)

def parse(s):
    tokens = s.split(" ")
    assert len(tokens) == NUM_QUALITIES
    return tuple(QUALITIES[i].index(tokens[i]) for i in range(NUM_QUALITIES))
def parse_many(strs):
    return [parse(s) for s in strs]

def third_card(a, b):
    return tuple(third(first, second) for first,second in zip(a,b))

def third(a, b):
    if a == b: return a
    else: return 3 - a - b

def all_cards():
    return itertools.product(range(NUM_OPTIONS), repeat=NUM_QUALITIES)

def demo():
    cards = list(all_cards())
    import random
    random.shuffle(cards)

    previous_c = None
    for c in cards:
        if previous_c:
            print(name(previous_c), name(c), name(third_card(previous_c, c)))
        previous_c = c

# demo()
        
def max_set():
    cards = list(all_cards())
    print("finding max set of non-matching cards from a deck of size %d" % len(cards))
    return max_set_helper([], cards)

global_max = (0, [])
def max_set_helper(so_far, to_come):
    global global_max
    if not to_come: return (len(so_far), so_far)
    if len(so_far) + len(to_come) < global_max[0]: return (0,[])
    next = to_come[0]
    to_come = to_come[1:]
    exclude = max_set_helper(so_far[:], to_come[:])
    forbidden = [third_card(c, next) for c in so_far]
    so_far.append(next)
    include = max_set_helper(so_far[:], [c for c in to_come if not c in forbidden])
#    print('include:', include)
#    print('exclude:', exclude)
    result = max(include, exclude)
    if result > global_max:
        global_max = result
        print(global_max[0], [name(c) for c in global_max[1]])
    return result

# print(max_set())

def solve(cards):
    print("Finding all solutions in the following set of cards:", names(cards))
    found = set()
    for c1 in cards:
        for c2 in cards:
            if c1 == c2: continue
            for c3 in cards:
                if c1 == c3: continue
                if c2 == c3: continue
                if third_card(c1, c2) == c3:
                    solution = tuple(sorted([c1, c2, c3]))
                    if solution not in found:
                        print("\t", names([c1, c2, c3]))
                    found.add(solution)
    if len(found)*3 > len(cards):
        print("WARNING: more solutions found than needed! be careful!")

solve(parse_many([
    "3 hexagon 3 circle",
    "2 hexagon 3 triangle",
    "2 hexagon 2 circle",
    "3 circle 2 circle",
    "3 circle 3 square",
    "1 square 3 circle",
    "3 circle 1 triangle",
    "3 square 1 circle",
    "1 square 3 square",
    ]))

solve(parse_many([
    '1 circle 2 circle',
    '3 circle 3 triangle',
    '1 circle 3 circle',
    '2 circle 1 square',
    '2 hexagon 1 square',
    '3 hexagon 1 triangle',
    '1 hexagon 1 circle',
    '2 circle 1 circle',
    '3 circle 2 circle',
    ]))
    
    
