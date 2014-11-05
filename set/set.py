NUM_NAMES = {
    0:"one",
    1:"two",
    2:"three",
}
COLOR_NAMES = {
    0:"red",
    1:"green",
    2:"blue",
}
SHADING_NAMES = {
    0:"empty",
    1:"half",
    2:"full",
}
SYMBOL_NAMES = {
    0:"diamond",
    1:"squiggle",
    2:"oval",
}


def name(c):
    return "[%s %s %s %s%s]" % (
        NUM_NAMES[c[0]],
        COLOR_NAMES[c[1]],
        SHADING_NAMES[c[2]],
        SYMBOL_NAMES[c[3]],
        c[0] and 's' or '')

def third_card(a, b):
    return [third(first, second) for first,second in zip(a,b)]

def third(a, b):
    if a == b: return a
    else: return 3 - a - b

def all_cards():
    for num in NUM_NAMES.keys():
        for color in COLOR_NAMES.keys():
            for shading in SHADING_NAMES.keys():
                for symbol in SYMBOL_NAMES.keys():
                    yield [num, color, shading, symbol]

def demo():
    cards = [c for c in all_cards()]
    import random
    random.shuffle(cards)

    previous_c = None
    for c in cards:
        if previous_c:
            print name(previous_c), name(c), name(third_card(previous_c, c))
        previous_c = c

def max_set():
    cards = [c for c in all_cards()]
    print "finding max set of non-matching cards from a deck of size %d" % len(cards)
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
#    print 'include:', include
#    print 'exclude:', exclude
    result = max(include, exclude)
    if result > global_max:
        global_max = result
        print global_max[0], [name(c) for c in global_max[1]]
    return result

print max_set()
