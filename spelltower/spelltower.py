from trie import Trie
from tower import Tower

import sys

class Play:
    startx = None
    starty = None
    steps = []
    word = ''
    def __init__(self, word):
        self.word = word
    def add_step(self, step):
        self.steps = [step] + self.steps
    def __len__(self):
        return len(self.steps) + 1
    def __cmp__(self, other):
        return len(self) - len(other)
    def __str__(self):
        return self.word
    def touched(self):
        touched = set()
        x,y = self.startx,self.starty
        touched.add((x,y))
        for dx,dy in self.steps:
            x += dx
            y += dy
            touched.add((x,y))
        return touched


def all_plays(tower, words):
    for x in range(14):
        for y in range(10):
            if tower.occupied(x,y):
                for play in all_plays_from(tower, x,y, words.root):
                    play.startx,play.starty = x,y
                    yield play

directions = [(-1,-1), (-1, 0), (-1, 1),
              ( 0,-1),          ( 0, 1),
              ( 1,-1), ( 1, 0), ( 1, 1)]
def all_plays_from(tower, x,y, trie_node, so_far=None, touched=None, min_length=3):
    if not so_far: so_far = ''
    if not touched: touched = {}

    if (x,y) in touched: return
    touched = touched.copy()
    touched[x,y] = True
    if not tower.occupied(x,y): return

    c = tower.at(x,y).value
    if c == '.': return
    if c == '~':
        if 'Q' not in trie_node or 'U' not in trie_node['Q']: return
        so_far += 'QU'
        trie_node = trie_node['Q']['U']
    else:
        if c not in trie_node: return
        so_far += c
        trie_node = trie_node[c]
    
    min_length = max(min_length, tower.at(x,y).min_length)
    if ' ' in trie_node and len(so_far) >= min_length:
        yield Play(so_far.upper())

    for dx,dy in directions:
        for play in all_plays_from(tower, x+dx, y+dy, trie_node, so_far, touched, min_length):
            play.add_step((dx, dy))
            yield play

def score_by_length(tower, play):
    return len(play)
def score_by_negative_length(tower, play):
    return -len(play)
def score_by_destruction(tower, play):
    tower = tower.copy()
    tower.update(play)
    return -len(tower.cells)
def score_by_skyline(tower, play):
    newtower = tower.copy()
    newtower.update(play)
    return score_tower_by_skyline(tower) - score_tower_by_skyline(newtower)
import math
def score_tower_by_skyline(tower):
    score = 0
    can_continue = True
    for y in range(10):
        num_occupied = 0
        for x in range(15):
            if tower.occupied(x,y): num_occupied += 1
        score += math.pow(num_occupied, y in [0,7] and 3 or 2)
        if num_occupied >= 13: can_continue = False
    if not can_continue: score = 1000000000
    return score
def score_by_boggle(tower, play):
    score_map = {3:1, 4:1, 5:2, 6:3, 7:5}
    length = len(play)
    if length in score_map: return score_map[length]
    return 11
def score_by_alphabet(tower, play):
    return play.word
    
def find_plays(tower, words, scorer=score_by_skyline, dedup=True):
    print 'finding legal moves...'
    plays = sorted([(scorer(tower, p), p) for p in all_plays(tower, words)])
    print 'found %d legal moves' % len(plays)
    if dedup:
        deduped = []
        seen = set()
        for p in plays:
            score,word = p[0],p[1].word
            if (word,score) in seen:
                continue
            seen.add((word,score))
            deduped.append(p)
        plays = deduped
    return plays

scrabble_distribution = (['A']*9 + ['B']*2 + ['C']*2 + ['D']*4 + ['E']*12 + ['F']*2 + ['G']*3 + ['H']*2 + ['I']*9 + ['J']*1 + ['K']*1 + ['L']*4 + ['M']*2 + ['N']*6 + ['O']*8 + ['P']*2 + ['Q']*1 + ['R']*6 + ['S']*4 + ['T']*6 + ['U']*4 + ['V']*2 + ['W']*2 + ['X']*1 + ['Y']*2 + ['Z']*1)

help = '? to find/show moves, ! to play moves, + to add rows'
def solve_puzzle(tower, words):
    played = set()
    plays = []
    while True:
        print '$ ',
        input = sys.stdin.readline()
        if not input:
            print 'played words:'
            for length,p in sorted([i for i in played]):
                print '\t',p
            print 'final tower state:'
            print tower.export()
            return
        input = input.rstrip().upper()
        if not input:
            print help
        elif input[0] == '?':
            if not plays:
                plays = find_plays(tower, words)
            if len(input) > 1:
                chosen_plays = [p for score,p in plays if p.word == input[1:]]
                if chosen_plays:
                    best = chosen_plays[-1]
                    print 'showing',best.word
                    print tower.show(best)
                else:
                    print 'no matching plays.'
            else: 
                for score,play in plays:
                    print '%s\t%s' % (play.word, score)
        elif input[0] == '!':
            if not plays:
                plays = find_plays(tower, words)
            if len(input) > 1:
                chosen_plays = [p for score,p in plays if p.word == input[1:]]
            else:
                chosen_plays = [p for score,p in plays]
            if chosen_plays:
                best = chosen_plays[-1]
                print 'playing',best.word
                played.add((len(best.word), best.word))
                print tower.show(best)
                tower.update(best)
                plays = []
                print tower
            else:
                print 'no matching moves.'
        elif input[0] == '+':
            tower.append(input[1:])
            plays = []
            print tower
        elif input[0] == '@':
            import random
            tower.append(''.join([random.choice(scrabble_distribution) + str(random.randint(3,6))
                                  for i in range(8)]))
            plays = []
            print tower
        else:
            print help


import cProfile
if __name__ == '__main__':
    if len(sys.argv) > 1:
        tower = Tower(8, open(sys.argv[1]))
    else:
        tower = Tower(8, [])
    print tower
    words = Trie(open('TWL06.txt'))
    solve_puzzle(tower, words)
