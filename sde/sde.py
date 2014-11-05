def fight(dice, attacker='hero', backlash=False, weak=False, fragile=False, vulnerable=False, massive=False):
    return [cross_counted(dice, lambda x: resolve_combat(x, attacker, backlash, weak, fragile, vulnerable, massive))]
def battle(results, *args):
    result = cross_counted(results, resolve_battle)
    for f in args:
        result = collapse(result, f)
    return result

def cross_counted(args, f):
    ans = {():1}
    for arg in args:
        ans = dict([(x+(y,), times*t)
                    for (x,t) in ans.iteritems()
                    for (y,times) in arg.iteritems()])
    result = {}
    for x,y in ans.iteritems():
        x = f(x)
        if x not in result:
            result[x] = 0
        result[x] += y
    return result

BLANK = 0
PIP = 1
HEART = 'h'
POT = 'p'
def resolve_combat(dice, attacker, backlash, weak, fragile, vulnerable, massive):
    pips,hearts,pots,wounds,backlash_wounds = 0,0,0,0,0
    max_offense = 0
    max_defense = 0
    for d in dice:
        if d == 'hp':
            hearts += 1
            pots += 1
        elif d == 'h': hearts += 1
        elif d == 'p': pots += 1
        else:
            pips += d
            if d > max_offense:
                max_offense = d
            if d < max_defense: # defense dice are negative
                max_defense = d
    if weak: pips -= max_offense
    if fragile: pips -= max_defense
    if pips > 0: wounds = 1
    if pips < 0 and backlash: backlash_wounds = 1
    if wounds <= 0: hearts,pots = 0,0
    if massive: wounds *= 2

    if attacker is 'boss':
        hearts += pots
        pots = 0
    elif attacker is not 'hero':
        hearts,pots = 0,0

    if vulnerable: wounds += 1

    return (wounds, hearts, pots, backlash_wounds)

def resolve_battle(fights):
    wounds,hearts,pots,backlash=0,0,0,0
    for w,h,p,b in fights:
        wounds += w
        hearts += h
        pots += p
        backlash += b
    return (wounds,hearts,pots,backlash)

def collapse(h, f):
    result = { }
    for k,v in h.iteritems():
        k = f(k)
        if k in result:
            result[k] += v
        else:
            result[k] = v
    return result

def print_histogram(h, label='event', display_cumulative=False):
    if len(h.values()) == 1 and 0 in h: return
    total = sum(h.values())
    width = len(str(total))
    cumulative = 0
    #    print total,"possible events"
    print '%s\tprobability' % label,
    if display_cumulative: print '\tcumulative\treverse cumulative'
    else: print

    expected = 0.0
    for k in sorted(h.keys()):
        v = h[k]
        expected += float(k)*float(v)/float(total)
        cumulative += v
        print '%d\t%4f' % (k, float(v)/float(total)),
        if display_cumulative: print '\t(%4f)\t(%4f)' % (float(cumulative)/float(total),
                                                         float(total - cumulative)/float(total))
        else: print
    print 'EV: %4f' % expected

def analyze(title, b):
    print 'outcome analysis for \'%s\':' % title
    h = battle(b);
    # print '(%d outcomes, %d distinct)' % (sum(h.values()), len(h.values()))
    print_histogram(collapse(h, lambda x: x[0]), 'wounds')
    print_histogram(collapse(h, lambda x: x[1]), 'hearts')
    print_histogram(collapse(h, lambda x: x[2]), 'pots')
    print_histogram(collapse(h, lambda x: x[3]), 'thorns')
    print

BLUE = [{ HEART:1, BLANK:2, PIP:2, PIP*2:1 }]
RED = [{ POT:1, BLANK:1, PIP:2, PIP*2:1, PIP*3:1 }]
GREEN = [{ HEART+POT:1, PIP:2, PIP*2:1, PIP*3:1, PIP*4:1 }]
WHITE = [{ PIP:1 }]

def vs(dice):
    return [collapse(d, lambda x: x not in ['h','p','hp'] and -x or 0) for d in dice]

#print BLUE, RED, GREEN
#print vs(BLUE), vs(RED), vs(GREEN)

#analyze('naked paladin basic x2 vs unarmored', 2 * fight(BLUE*3 + vs(0*BLUE + 0*RED)))
#analyze('naked paladin smite x1 vs unarmored', 1 * fight(BLUE*3 + RED + vs(0*BLUE + 0*RED)))
#analyze('naked barbarian full berserk vs 1w', 6 * fight(RED*2 + vs(WHITE)))
#analyze('+2r mage basic x4 vs starfire', 4 * fight(RED*4 + BLUE*0 + vs(BLUE+RED+GREEN)))
#analyze('+2r mage magma strike x2 vs starfire', 2 * fight(RED*4 + BLUE*3 + vs(BLUE+RED+GREEN)))
analyze('naked pally basic attack x2 vs beetle w/chitin', 2 * fight(BLUE*3 + vs(WHITE+RED*2), backlash=True))
analyze('naked pally smite vs beetle w/chitin', 1 * fight(BLUE*3 + RED + vs(WHITE+RED*2), backlash=True))
#analyze('+1b pally smite vs beetle', 1 * fight(BLUE*3 + RED + BLUE + vs(WHITE+RED*2), backlash=True))
#analyze('+1r pally smite vs beetle', 1 * fight(BLUE*3 + RED + RED + vs(WHITE+RED*2), backlash=True))
#analyze('+1r1b pally smite vs beetle', 1 * fight(BLUE*3 + RED + RED + BLUE + vs(WHITE+RED*2), backlash=True))
#analyze('+2r pally smite vs beetle', 1 * fight(BLUE*3 + RED + RED*2 + vs(WHITE+RED*2), backlash=True))
#analyze('naked mage magma strike x1 vs beetle', 1 * fight(RED*2 + BLUE*3 + vs(WHITE + RED*2), backlash=True))

'''
analyze('naked mage basic attack x3 vs spawner',
        3 * fight(RED*2 + BLUE*0 + vs(WHITE)))
analyze('+2b mage basic attack x3 vs spawner',
        3 * fight(RED*2 + BLUE*2 + vs(WHITE)))
analyze('+2b1g mage basic attack x3 vs spawner',
        3 * fight(RED*2 + BLUE*2 + GREEN + vs(WHITE)))
'''

'''
analyze('Rex Smash w/full mob + dragon rage vs +1r Dwarf w/backlash',
        1 * fight(RED*2 + BLUE*3 + BLUE + GREEN + vs(RED*3),
        backlash=True, attacker='boss', massive=True))
analyze('weakened Rex Smash w/full mob + dragon rage vs +1r Dwarf w/backlash',
        1 * fight(RED*2 + BLUE*3 + BLUE + GREEN + vs(RED*3),
        backlash=True, attacker='boss', massive=True, weak=True))
analyze('Rex Smash w/full mob + dragon rage vs +1r fragile Dwarf w/backlash',
        1 * fight(RED*2 + BLUE*3 + BLUE + GREEN + vs(RED*3),
        backlash=True, attacker='boss', massive=True, fragile=True))
'''

#analyze('paladin w/Roxor\'s Bane melee x3 vs Rockgut',
#        3 * fight(RED + BLUE*3 + vs(WHITE + RED), vulnerable=True))
