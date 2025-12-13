from clues import *

evaluate(
    knowns={
        F: 0,
        K: 1, S: 1,
        T: 1,
        H: 0,
        G: 0, X: 0,
        C: 0,
        L: 0,
        A: 0,
        B: 0,
        P: 0,
        O: 0,
        V: 1,
        W: 0,
        D: 0,
    },
    claims=[
        # F: There are no innocents above Xavi who neighbor Phil
        'innocents(above(X) & neighbors(P)) == 0',
        # S: There are more criminals than innocents to the right of Phil
        'criminals([S,T]) > innocents([S,T])',
        # T: Hal is one of 11 innocents on the edges
        'innocents([H]) == 1 and innocents(edges()) == 11',
        # H: Zara is the only one with only 1 innocent neighbor
        'innocents(neighbors(Z)) == 1 and min(innocents(neighbors(s)) for s in SUBJECTS if s is not Z) >= 2',
        # G: Both criminals in column C are connected
        'criminals([C, G, K, S, X]) == 2',  # TODO: connected
        # C: Only 1 of the 2 innocents in row 3 is Hal's neighbor
        'innocents(row(3)) == 2 and innocents(row(3) & neighbors(H)) == 1',
        # L: No singer has a criminal directly above them
        'max(criminals(above(s, directly=True)) for s in [D,E]) == 0',
        # A: Ellie has exactly 4 innocent neighbors
        'innocents(neighbors(E)) == 4',
        # B: There are more criminals among coders than any other profession
        'criminals(profession("coder")) > max(criminals(profession(p)) for p in set(PROFESSIONS) if p != "coder")',
        # P: Each row has at least 2 innocents
        'min(innocents(r) for r in GRID) >= 2',
        # O: Debra and Wanda have an equal number of innocent neighbors
        'innocents(neighbors(D)) == innocents(neighbors(W))',
        # V: Linda has more criminal neighbors than Oscar
        'criminals(neighbors(L)) > criminals(neighbors(O))',
        # W: Hal has more innocent neighbors than Oscar
        'innocents(neighbors(H)) > innocents(neighbors(O))',
        # D: There's an odd number of innocents neighboring Freya
        'innocents(neighbors(F)) % 2 == 1',
    ])
