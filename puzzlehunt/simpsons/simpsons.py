DATA = '''YUGKOOBCIMOC
ARALPHJLJBKX
PMEXJXYEXAQU
XALMQZLTYRJT
QZTEOKRUSTYS
XUDTSRUSPKMO
MGEMYXSMIIQC
YACARLAETXAS
NXRGSRXHFJSI
NQJGTYEXVUID
EKXIERYZAELS
LJNESUOHLIMX
'''

LINES = DATA.splitlines()
print(LINES)
GRID = [[x for x in line] for line in LINES]
print('\n'.join(str(l) for l in GRID))

ROWS = len(GRID)
COLS = len(GRID[0])

CELL_INDICES = [(x,y) for x in range(ROWS) for y in range(COLS)]

GRID_D = {(x,y):GRID[x][y] for x,y in CELL_INDICES}
print(GRID_D)
assert len(GRID_D) == ROWS * COLS

TARGETS = [
    'BART',
    'CARL',
    'CLETUS',
    'COMICBOOKGUY',
    'DISCOSTU',
    'HOMER',
    'KRUSTY',
    'LENNY',
    'LISA',
    'MAGGIE',
    'MARGE',
    'MARTIN',
    'MILHOUSE',
    'PATTY',
    'RALPH',
    'SELMA',
    'SMITHERS',
    ]

import collections

TARGETS = set([line.strip().upper() for line in open('/usr/share/dict/words') if len(line) >= 5])
prefixes = set()
for length in range(ROWS):
    prefixes = prefixes.union([t[:length+1] for t in TARGETS])
print("#targets:", len(TARGETS))
print("#prefixes:", len(prefixes))

used_count = collections.defaultdict(int)
for sx,sy in CELL_INDICES:
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0: continue
            word = ""
            for i in range(ROWS):
                x, y = sx + i*dx, sy + i*dy
                if (x < 0 or y < 0 or
                    x >= len(GRID) or y >= len(GRID[x])): break
                word += GRID[x][y]
                if word not in prefixes: break
                if word in TARGETS:
                    print(word, x, y, dx, dy)

# print(total_used)
print("".join([GRID[x][y] for (x,y),c in sorted(used_count.items()) if c > 1]))
