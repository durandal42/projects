from clues import *

evaluate(
    knowns={
        E: 0,
        I: 1,
        N: 1,
        X: 1,
        T: 0,
        O: 1,
        V: 0, Z: 1,
        J: 0, L: 1,
        F: 0, G: 1,
        B: 1, C: 0,
        D: 1, H: 1, M: 0, P: 1, S: 0,
    },
    claims=[
        # E: Isaac is one of two or more criminals below me
        'num_criminals(below(E)) >= 2 and is_criminal(I)',
        # I: All criminals below Alice are connected
        'connected(criminals(below(A)))',
        # N: Only 1 of the 2 criminals to the right of Terry is Xavi's neighbor
        'num_criminals(right(T)) == 2 and num_criminals(right(T) & neighbors(X)) == 1',
        # X: I am one of 2 criminals in row 5
        'num_criminals(row(5)) == 2',
        # T: Only one of the 3 criminals neighboring Xavi is Zach's neighbor
        'num_criminals(neighbors(X)) == 3 and num_criminals(neighbors(X) & neighbors(Z)) == 1',
        # O: Sofia and Terry have an equal number of innocent neighbors
        'num_innocents(neighbors(S)) == num_innocents(neighbors(T))',
        # V: Lisa and Paula share an odd number of innocent neighbors
        'num_innocents(neighbors(L) & neighbors(P)) % 2 == 1',
        # Z: Both innocents in column D are connected
        'connected(innocents(column(D))) and num_innocents(column(D)) == 2',
        # J: Lisa has exactly 4 innocent neighbors
        'num_innocents(neighbors(L)) == 4',
        # L: Gary and I share an odd number of innocent neighbors
        'num_innocents(neighbors(L) & neighbors(G)) % 2 == 1',
        # F: There's an odd number of innocents neighboring Carl
        'num_innocents(neighbors(C)) % 2 == 1',
        # G: Vince and I have an equal number of criminal neighbors
        'num_criminals(neighbors(G)) == num_criminals(neighbors(V))',
        # C: Vince and I have an equal number of innocent neighbors
        'num_innocents(neighbors(C)) == num_innocents(neighbors(V))',
        # D: Nancy and Barb have an equal number of innocent neighbors
        'num_innocents(neighbors(N)) == num_innocents(neighbors(B))',
    ])
